#!/usr/bin/env python3
"""Refine rough OCR intervals for static white Chinese hard subtitles with dark outlines."""
import argparse
from bisect import bisect_left
import json
import math
from pathlib import Path
import subprocess
import tempfile

import cv2
import numpy as np

from captions import atomic_text, probe


def geometry(rows, width, height):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Expected a list of rough caption intervals')
    rects = []
    for i, row in enumerate(rows,1):
        if not row.get('zh','').strip():
            raise ValueError(f'Cue {i} needs the Chinese text confirmed by OCR or visual reading')
        box = row['bbox']
        if len(box)!=4 or not all(isinstance(v,int) for v in box):
            raise ValueError(f'Cue {i}: bbox must be [x,y,width,height] in source pixels')
        x,y,w,h = box
        if min(w,h)<1 or not (0<=x<x+w<=width and 0<=y<y+h<=height):
            raise ValueError(f'Cue {i}: bbox outside source')
        pad=max(2,round(h*.09))
        rects.append((max(0,x-pad),max(0,y-pad),min(width,x+w+pad),min(height,y+h+pad)))
    return rects


def estimate(local, row, times, search):
    s=row['start_frame']; e=row['end_frame_exclusive']
    if not (type(s) is int and type(e) is int and 0<=s<e<len(times)):
        raise ValueError('Invalid rough frame range')
    mid=row.get('seed_frame',(s+e)//2)
    if type(mid) is not int or not s<=mid<e:
        raise ValueError('Seed frame must be inside the rough interval')
    n=len(local)
    lo=bisect_left(times,max(0,times[s]-search))
    hi=min(n,bisect_left(times,times[e]+search)+1)
    half_span=max(1,round((e-s)*.20))
    samples=np.unique(np.rint(np.linspace(max(s,mid-half_span),min(e-1,mid+half_span),13)).astype(int))
    patch=local[samples]
    med=np.median(patch,axis=0).astype(np.uint8)
    radius=max(2,min(5,round(med.shape[0]/12)))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1))
    light=(np.percentile(patch,12,axis=0)>190)&(cv2.erode(med,kernel)<70)
    dark=(np.percentile(patch,88,axis=0)<78)&(cv2.dilate(med,kernel)>190)
    light &= cv2.dilate(dark.astype(np.uint8),kernel)>0
    dark &= cv2.dilate(light.astype(np.uint8),kernel)>0
    detail={'light_pixels':int(light.sum()),'dark_pixels':int(dark.sum())}
    if min(detail.values())<12:
        return None,'too few stable light strokes or dark outlines',detail
    contrast=float(med[light].mean()-med[dark].mean())
    if contrast<110:
        return None,'weak contrast in confirmed seed',detail
    scores=np.empty(hi-lo)
    for a in range(lo,hi,128):
        b=min(hi,a+128); block=local[a:b]
        scores[a-lo:b-lo]=(block[:,light].mean(1)-block[:,dark].mean(1))/contrast
    active=scores>.62
    if not active[mid-lo]:
        return None,'seed frame did not match',detail
    changes=np.flatnonzero(active[1:]!=active[:-1])+1+lo
    a=max([lo]+[v for v in changes if v<=mid])
    b=min([hi]+[v for v in changes if v>mid])
    outside=[scores[k-lo] for k in (a-1,b) if lo<=k<hi]
    inside=float(scores[a-lo:b-lo].min())
    detail.update(min_inside=round(inside,3),max_adjacent=round(max(outside,default=0),3))
    if (a==lo and lo>0) or (b==hi and hi<n):
        return None,'matching strokes extend to search limit',detail
    if inside<.73 or max(outside,default=0)>.45:
        return None,'ambiguous or fading boundary; inspect actual image',detail
    # A drop-out and reappearance inside a supposedly uninterrupted OCR cue deserves review.
    tolerance=2
    if active[max(0,s-lo+tolerance):max(0,a-lo-tolerance)].any() or active[b-lo+tolerance:max(0,e-lo-tolerance)].any():
        return None,'more than one run of the same glyphs within rough interval',detail
    return (int(a),int(b)),None,detail


def run(args):
    times,width,height=probe(args.source.resolve())
    rows=json.loads(args.rough.read_text())
    rects=geometry(rows,width,height)
    left=min(v[0] for v in rects); top=min(v[1] for v in rects)
    width=max(v[2] for v in rects)-left; height=max(v[3] for v in rects)-top
    factor=min(1,32/min(v[3]-v[1] for v in rects))
    sw,sh=max(1,round(width*factor)),max(1,round(height*factor))
    graph=f'format=gray,crop={width}:{height}:{left}:{top},scale={sw}:{sh}:flags=area'
    summary=[]
    with tempfile.TemporaryDirectory(dir=args.work_dir) as tmp:
        raw=Path(tmp)/'band.y8'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','4','-i',str(args.source.resolve()),
                        '-map','0:v:0','-vf',graph,'-fps_mode','passthrough','-pix_fmt','gray','-f','rawvideo',str(raw)],check=True)
        frames=np.memmap(raw,mode='r',dtype=np.uint8).reshape(-1,sh,sw)
        if len(frames)!=len(times)-1:
            raise ValueError('Decoded source and frame index do not match')
        for row,(x,y,r,b) in zip(rows,rects):
            x0=math.floor((x-left)*sw/width); x1=math.ceil((r-left)*sw/width)
            y0=math.floor((y-top)*sh/height); y1=math.ceil((b-top)*sh/height)
            ends,reason,detail=estimate(frames[:,y0:y1,x0:x1],row,times,args.search_seconds)
            result={key:v for key,v in row.items() if key not in ('start_frame','end_frame_exclusive')}
            result.update(rough_frames=[row['start_frame'],row['end_frame_exclusive']],edge_evidence=detail)
            if ends:
                result.update(start_frame=ends[0],end_frame_exclusive=ends[1],edge_status='matched')
            else:
                result.update(edge_status='needs_review',reason=reason)
            summary.append(result)
    conflicts=set()
    for i in range(1,len(summary)):
        a,b=summary[i-1],summary[i]
        if 'end_frame_exclusive' in a and 'start_frame' in b and a['end_frame_exclusive']>b['start_frame']:
            conflicts.update([i-1,i])
    for i in conflicts:
        row=summary[i]; row.pop('start_frame');row.pop('end_frame_exclusive')
        row.update(edge_status='needs_review',reason='two identified caption intervals overlap')
    args.output.parent.mkdir(exist_ok=True,parents=True)
    atomic_text(args.output,json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    unresolved=[i+1 for i,r in enumerate(summary) if r['edge_status']=='needs_review']
    print(json.dumps({'captions':len(rows),'needs_review':unresolved}))
    return 2 if unresolved else 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('rough',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--search-seconds',type=float,default=1.5,help='Search around each approximate boundary')
    parser.add_argument('--work-dir',type=Path,help='Existing directory for temporary decoded grayscale band')
    args=parser.parse_args()
    if not math.isfinite(args.search_seconds) or args.search_seconds<=0:
        parser.error('--search-seconds must be positive')
    return run(args)


if __name__=='__main__':
    raise SystemExit(main())
