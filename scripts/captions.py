#!/usr/bin/env python3
"""Build English ASS/SRT from the frame intervals of Chinese captions in a source video."""
import argparse
from bisect import bisect_left
from fractions import Fraction
from html import escape
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def probe(source):
    fields = (
        'stream=width,height,time_base,nb_frames,start_pts,duration_ts:'
        'stream_side_data=rotation:frame=best_effort_timestamp,duration,pkt_duration'
    )
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
               '-show_streams', '-show_entries', fields, '-of', 'json', str(source)]
    info = json.loads(subprocess.check_output(command))
    stream = info['streams'][0]
    frames = info['frames']
    if not frames:
        raise ValueError('No displayed video frames')
    stamps = [int(f['best_effort_timestamp']) for f in frames]
    if any(a >= b for a, b in zip(stamps, stamps[1:])):
        raise ValueError('Presentation timestamps must increase in display order; probe the conformed source')
    declared_count = stream.get('nb_frames', 'N/A')
    if declared_count != 'N/A' and int(declared_count) != len(stamps):
        raise ValueError(f'Decoded {len(stamps)} frames but stream declares {declared_count}; inspect source')
    frame_duration = next((int(frames[-1][k]) for k in ('duration', 'pkt_duration')
                           if frames[-1].get(k) not in (None, 'N/A') and int(frames[-1][k]) > 0), None)
    if frame_duration is None:
        if stream.get('duration_ts') in (None, 'N/A'):
            raise ValueError('Could not establish the end of the final displayed frame')
        origin = stream.get('start_pts', stamps[0])
        frame_duration = int(origin) + int(stream['duration_ts']) - stamps[-1]
        if frame_duration <= 0:
            raise ValueError('Invalid final frame duration')
    time_base = Fraction(stream['time_base'])
    timestamps = [(t - stamps[0]) * time_base for t in stamps + [stamps[-1] + frame_duration]]
    width, height = stream['width'], stream['height']
    for side in stream.get('side_data_list', []):
        if abs(int(side.get('rotation', 0))) % 180 == 90:
            width, height = height, width
            break
    return timestamps, width, height


def boundary(frame, timestamps, units):
    """Put the encoded switch between adjacent presentation times, favoring their midpoint."""
    if frame == 0:
        return 0
    if frame == len(timestamps) - 1:
        return max(math.floor(timestamps[frame-1] * units) + 1,
                   math.floor(timestamps[frame] * units + Fraction(1,2)))
    before, at = timestamps[frame - 1] * units, timestamps[frame] * units
    lower, upper = math.floor(before) + 1, math.floor(at)
    if lower > upper:
        raise ValueError(f'Frame {frame} cannot be expressed at 1/{units} second caption precision')
    midpoint = math.floor((before + at + 1) / 2)
    ticks = min(upper, max(lower, midpoint))
    if bisect_left(timestamps, Fraction(ticks, units)) != frame:
        raise ValueError(f'Could not represent exact caption boundary at frame {frame}')
    return ticks


def stamp(ticks, units):
    seconds, rest = divmod(ticks, units)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if units == 1000:
        return f'{hours:02}:{minutes:02}:{seconds:02},{rest:03}'
    return f'{hours}:{minutes:02}:{seconds:02}.{rest:02}'


def ass_header(width, height, font_size):
    scale = height / 1080
    margin_x = round(width * 140 / 1920)
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{font_size},&H00FFFFFF,&H00FFFFFF,&H00101010,&H70000000,-1,0,0,0,100,100,0,0,1,{max(1,3*scale):g},{max(0.25,scale):g},2,{margin_x},{margin_x},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def require_int(row, key, low, high):
    value = row.get(key)
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{key} must be an integer in [{low}, {high}], got {value!r}')
    return value


def encode(rows, timestamps, width, height, default_size):
    if not isinstance(rows, list):
        raise ValueError('Expected a JSON list of visible captions')
    total_frames = len(timestamps) - 1
    ass = [ass_header(width, height, default_size)]
    srt = []
    previous = 0
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f'Cue {number} must be an object')
        if row.get('edge_status') == 'needs_review':
            raise ValueError(f'Cue {number} has an unresolved edge; review its source frames')
        start = require_int(row, 'start_frame', previous, total_frames - 1)
        end = require_int(row, 'end_frame_exclusive', start + 1, total_frames)
        previous = end
        if not all(isinstance(row.get(k), str) and row[k].strip() for k in ('zh', 'en')):
            raise ValueError(f'Cue {number} needs Chinese visible text and English translation')
        margin = require_int(row, 'margin_v', 0, height - 1)
        size = require_int(row, 'font_size', 1, height) if 'font_size' in row else default_size
        lines = [s.strip() for s in row['en'].replace(r'\N', '\n').splitlines()]
        if any(not s for s in lines):
            raise ValueError(f'Blank line within cue {number}')
        text = r'\N'.join(s.replace('{',r'\{').replace('}',r'\}') for s in lines)
        if size != default_size:
            text = r'{\fs' + str(size) + '}' + text
        t0, t1 = (stamp(boundary(f, timestamps, 100), 100) for f in (start, end))
        ass.append(f'Dialogue: 0,{t0},{t1},Default,,0,0,{margin},,{text}\n')
        s0, s1 = (stamp(boundary(f, timestamps, 1000), 1000) for f in (start, end))
        srt.extend([str(number), f'{s0} --> {s1}', *[escape(s, quote=False) for s in lines], ''])
    return ''.join(ass), ('\n'.join(srt) + '\n' if srt else '')


def atomic_text(path, text):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode='w', encoding='utf-8') as out:
        tmp = Path(out.name)
        try:
            out.write(text)
            out.close()
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('cues', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--font-size', type=int, help='Default ASS font size in source canvas pixels')
    parser.add_argument('--add-chinese', action='store_true', help='Create bilingual.ass when source has no visible Chinese captions; supply zh_margin_v per cue')
    args = parser.parse_args()
    times, width, height = probe(args.source.resolve())
    size = args.font_size if args.font_size is not None else max(1, round(50 * height / 1080))
    if not 1 <= size <= height:
        parser.error('font size must fit source height')
    rows = json.loads(args.cues.read_text(encoding='utf-8'))
    ass, srt = encode(rows, times, width, height, size)
    if args.add_chinese:
        zh_rows = []
        for row in rows:
            lower = require_int(row, 'zh_margin_v', 0, height - 1)
            if lower >= row['margin_v']:
                raise ValueError('Chinese must sit below its paired English; check the measured margins')
            zh_rows.append({**row, 'en': row['zh'], 'font_size': row.get('zh_font_size', size), 'margin_v': lower})
        zh_ass, _ = encode(zh_rows, times, width, height, size)
        zh_events = [line for line in zh_ass.splitlines() if line.startswith('Dialogue:')]
        # Native macOS CJK face; select it only for Chinese events.
        event_format = ',Default,,0,0,'
        style = next(line for line in ass.splitlines() if line.startswith('Style: Default,'))
        zh_style = style.replace('Default,Arial,', 'Chinese,PingFang SC,', 1)
        bilingual = ass.replace(style, style + '\n' + zh_style, 1)
        bilingual += ''.join(line.replace(event_format, ',Chinese,,0,0,', 1)+'\n' for line in zh_events)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_text(args.output_dir / 'english.ass', ass)
    atomic_text(args.output_dir / 'english.srt', srt)
    if args.add_chinese:
        atomic_text(args.output_dir / 'bilingual.ass', bilingual)
    print(f'{len(rows)} caption intervals for {len(times)-1} displayed frames, {width}×{height}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error
