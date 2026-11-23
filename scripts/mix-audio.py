#!/usr/bin/env python3
"""Mix time-aligned dialogue, location sound and an optional user-supplied score."""
import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

RATE = 48000


def run(args):
    subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-nostdin', '-n', *args], check=True)


def finite(value):
    num = float(value)
    if not math.isfinite(num):
        raise argparse.ArgumentTypeError('expected a finite number')
    return num


def audio_duration(path):
    info = json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
         'stream=duration_ts,time_base', '-of', 'json', str(path)]))
    if not info.get('streams') or 'duration_ts' not in info['streams'][0]:
        raise ValueError(f'Cannot measure the audio timeline in {path}; use a decoded WAV')
    stream = info['streams'][0]
    return int(stream['duration_ts']) * Fraction(stream['time_base'])


def build_loop(score, target, start, end, fade):
    source = '[0:a:0]aresample=48000'
    if fade:
        graph = (source + ',asplit=3[a][b][c];'
                 f'[a]atrim=start_sample={end}:end_sample={end+fade},asetpts=PTS-STARTPTS[tail];'
                 f'[b]atrim=start_sample={start}:end_sample={start+fade},asetpts=PTS-STARTPTS[head];'
                 f'[c]atrim=start_sample={start+fade}:end_sample={end},asetpts=PTS-STARTPTS[mid];'
                 f'[tail][head]acrossfade=ns={fade}[seam];[seam][mid]concat=n=2:v=0:a=1[out]')
    else:
        graph = source + f',atrim=start_sample={start}:end_sample={end},asetpts=PTS-STARTPTS[out]'
    run(['-i', str(score), '-filter_complex', graph, '-map', '[out]', '-c:a', 'pcm_f32le', str(target)])
    if round(audio_duration(target)*RATE) != end-start:
        raise ValueError('The decoded recording does not cover the loop and its crossfade tail')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--duration', required=True, type=finite, help='source presentation length in seconds')
    p.add_argument('--bed', type=Path, help='synchronized clean location sound')
    p.add_argument('--voice', type=Path, help='synchronized English narration')
    p.add_argument('--music', type=Path, help='a recording to play once, or loop between the supplied points')
    p.add_argument('--loop-start', type=finite, help='loop start in score seconds')
    p.add_argument('--loop-end', type=finite, help='exclusive loop end in score seconds')
    p.add_argument('--loop-fade', type=finite, default=0, help='seconds of music after loop end to blend into its start')
    p.add_argument('--music-gain', type=finite, default=-13.0, help='music gain in dB')
    p.add_argument('--bed-gain', type=finite, default=-3.5, help='clean ambience gain in dB')
    p.add_argument('--output', required=True, type=Path, help='new 48 kHz stereo PCM .wav')
    args = p.parse_args()
    if not any((args.bed, args.voice, args.music)):
        p.error('supply at least one of --bed, --voice or --music')
    if args.output.suffix.lower() != '.wav' or args.output.exists():
        p.error('output must be a new .wav file')
    samples = round(args.duration * RATE)
    if samples < 1:
        p.error('duration must span at least one sample')
    loop = args.loop_start is not None or args.loop_end is not None
    if loop and (not args.music or args.loop_start is None or args.loop_end is None):
        p.error('looping requires --music, --loop-start and --loop-end')
    if args.loop_fade < 0 or (args.loop_fade and not loop):
        p.error('a nonnegative loop fade requires a loop')
    if loop:
        start, end, fade = [round(x*RATE) for x in (args.loop_start, args.loop_end, args.loop_fade)]
        if not (0 <= start < end and fade < end-start):
            p.error('choose an increasing loop interval longer than the crossfade')
        if end + fade > round(audio_duration(args.music)*RATE):
            p.error('the music must extend through loop-end plus loop-fade')
    if args.voice and audio_duration(args.voice) > args.duration + 0.001:
        p.error('the voice extends beyond the video; check the final turn')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as tmp:
        inputs, filters, tracks = [], [], []
        length = f'atrim=end_sample={samples}'
        stem = f'aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo,apad,{length}'
        if args.music:
            music = args.music
            if loop:
                music = Path(tmp) / 'loop.wav'
                build_loop(args.music, music, start, end, fade)
                inputs.extend(['-stream_loop', '-1'])
            inputs.extend(['-i', str(music)])
            fade_seconds = min(1.0, args.duration / 2)
            filters.append(f'[0:a:0]{stem},volume={args.music_gain}dB,'
                           f'afade=t=in:d={fade_seconds:.9f},afade=t=out:st={args.duration-fade_seconds:.9f}:d={fade_seconds:.9f}[music]')
            tracks.append('[music]')
        if args.bed:
            inputs.extend(['-i', str(args.bed)])
            filters.append(f'[{len(tracks)}:a:0]{stem},volume={args.bed_gain}dB[bed]')
            tracks.append('[bed]')
        if args.voice:
            inputs.extend(['-i', str(args.voice)])
            filters.append(f'[{len(tracks)}:a:0]{stem}[narration]')
            if tracks:
                filters.append('[narration]asplit=2[voice][detector]')
                if len(tracks) == 2:
                    filters.append(''.join(tracks) + 'amix=inputs=2:normalize=0[room]')
                    tracks = ['[room]']
                filters.append(tracks[0] + '[detector]sidechaincompress=threshold=0.035:ratio=3:'
                               'attack=20:release=400:detection=rms[soft]')
                tracks = ['[voice]', '[soft]']
            else:
                tracks = ['[narration]']
        if len(tracks) == 2:
            filters.append(''.join(tracks) + 'amix=inputs=2:normalize=0[full]')
            tracks = ['[full]']
        filters.append(tracks[0]+f'alimiter=limit=0.89:level=false:latency=true,apad,{length}[out]')
        rendered = Path(tmp) / 'render.wav'
        run([*inputs, '-filter_complex', ';'.join(filters), '-map', '[out]',
             '-c:a', 'pcm_s24le', '-rf64', 'auto', str(rendered)])
        os.link(rendered, args.output)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
