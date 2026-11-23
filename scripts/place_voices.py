#!/usr/bin/env python3
"""Place cached English turns on the source timeline; preserve overlapping speakers."""
import argparse
from array import array
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from voice import prepare

RATE = 48000
RAW = ['-f', 'f32le', '-ar', str(RATE), '-ac', '1']


def ffmpeg(options, payload=None):
    return subprocess.check_output(
        ['ffmpeg', '-nostdin', '-v', 'error', '-n', *options], input=payload)


def spoken_region(cache):
    # Keep any audible attacks/breaths outside the timestamped words. The
    # timestamps also protect weak syllables below the amplitude threshold.
    if not (cache/'ready').is_file():
        raise ValueError(f'Missing completed voice cache {cache.name}; run voice.py first')
    reply = json.loads((cache/'alignment.json').read_text())
    align = reply.get('alignment') or reply['normalized_alignment']
    timed = [(float(a), float(b)) for ch,a,b in zip(align['characters'],
             align['character_start_times_seconds'], align['character_end_times_seconds'], strict=True)
             if ch.strip()]
    if not timed or any(not (math.isfinite(a) and math.isfinite(b) and 0 <= a <= b) for a,b in timed):
        raise ValueError(f'Invalid character timestamps in cache {cache.name}')
    samples = array('f', ffmpeg(['-i', str(cache/'audio.mp3'), '-map', '0:a:0', *RAW, '-']))
    limit = 10**(-52/20)
    first = next((i for i,v in enumerate(samples) if abs(v)>limit), None)
    if first is None:
        raise ValueError(f'No audible speech in cache {cache.name}')
    last = len(samples) - next(i for i,v in enumerate(reversed(samples)) if abs(v)>limit)
    first = max(0, min(first, round(RATE*min(a for a,_ in timed))) - round(.018*RATE))
    last = min(len(samples), max(last, round(RATE*max(b for _,b in timed))) + round(.055*RATE))
    return samples[first:last]


def fit(clip, available, max_speed, turn_id):
    if len(clip) <= available:
        return clip
    # Allow WSOLA a few ms of output variation, without increasing the cap.
    speed = min(max_speed, len(clip)/max(1,available-round(.015*RATE)))
    if len(clip) <= available*max_speed and speed > 1:
        raw = ffmpeg([*RAW, '-i', '-', '-af', f'atempo={speed:.9f}', *RAW, '-'], clip.tobytes())
        result = array('f', raw)
        if result and len(result) <= available:
            return result
    raise ValueError(f'{turn_id}: speech lasts {len(clip)/RATE:.2f}s for a {available/RATE:.2f}s '
                     'window; tighten the translation or use an adjacent quiet interval')


def level(path):
    cmd = ['ffmpeg','-nostdin','-hide_banner','-nostats',*RAW,'-i',str(path),'-af',
           'loudnorm=I=-18:TP=-2:LRA=11:print_format=json','-f','null','-']
    log = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True).stderr
    m, _ = json.JSONDecoder().raw_decode(log[log.rfind('{'):])
    loudness, peak = float(m['input_i']), float(m['input_tp'])
    # Short isolated turns may fall below the LUFS gate; keep their gain
    # unless attenuation is required for peak headroom.
    desired = -18-loudness if math.isfinite(loudness) else 0.0
    return min(desired, -2-peak) if math.isfinite(peak) else 0.0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan', type=Path, help='voice.py JSON, with start and end seconds on each turn')
    p.add_argument('cache', type=Path, help='voice.py cache root')
    p.add_argument('--duration', required=True, type=float, help='source video presentation length, seconds')
    p.add_argument('--output', required=True, type=Path, help='new WAV on the source timeline')
    p.add_argument('--max-speed', type=float, default=1.12, help='tempo cap, default 1.12; use 1 to disable')
    args = p.parse_args()
    if not math.isfinite(args.duration) or args.duration <= 0 or round(args.duration*RATE)<1:
        p.error('duration must span at least one sample')
    if not 1 <= args.max_speed <= 1.20:
        p.error('max-speed must be between 1.0 and 1.20')
    if args.output.suffix.lower() != '.wav' or args.output.exists():
        p.error('output must be a new .wav file')
    plan = json.loads(args.plan.read_text())
    turns = prepare(plan)
    total = round(args.duration*RATE)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as tmp:
        raw = Path(tmp)/'voices.f32'
        with raw.open('w+b') as f:
            f.truncate(total*4)
            for (tid,_,_,fingerprint), turn in zip(turns, plan['turns'], strict=True):
                start, end = float(turn['start']), float(turn['end'])
                if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end):
                    p.error(f'{tid}: invalid start/end in seconds')
                a,b = round(start*RATE),round(end*RATE)
                if not 0 <= a < b <= total:
                    p.error(f'{tid}: turn extends outside the source timeline')
                clip = fit(spoken_region(args.cache/fingerprint), b-a, args.max_speed, tid)
                f.seek(a*4)
                before = array('f', f.read(len(clip)*4))
                mixed = array('f', (x+y for x,y in zip(clip,before,strict=True)))
                f.seek(a*4)
                f.write(mixed.tobytes())
        gain = level(raw) if turns else 0
        out = Path(tmp)/'voice.wav'
        ffmpeg([*RAW, '-i', str(raw), '-af', f'volume={gain:.4f}dB', '-c:a','pcm_s24le',
                '-rf64','auto',str(out)])
        os.link(out, args.output)
    print(f'{len(turns)} turns, {total} samples, track gain {gain:+.1f} dB')


if __name__ == '__main__':
    main()
