#!/usr/bin/env python3
"""Burn an episode's frame-timed ASS and optional transparent logo onto its clean master."""
import argparse
import json
import os
import subprocess
import tempfile
from fractions import Fraction
from math import ceil
from pathlib import Path


def probe(path, selector, entries):
    result = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", selector,
                                      "-show_entries", entries, "-of", "json", str(path)])
    return json.loads(result)


def stream(path, selector):
    info = probe(path, selector, "stream:stream_side_data")
    if not info.get("streams"):
        raise ValueError(f"No {selector} stream in {path}")
    return info["streams"][0]


def video_info(path):
    info = stream(path, "v:0")
    if any(int(s.get("rotation", 0)) % 360 for s in info.get("side_data_list", [])):
        raise ValueError("Normalize display rotation losslessly where possible before measuring the mark")
    if info.get("sample_aspect_ratio", "1:1") not in ("N/A", "1:1", "0:1"):
        raise ValueError("Normalize non-square pixels before measuring captions and the logo")
    if info["pix_fmt"] not in ("yuv420p", "yuvj420p") or info.get("color_transfer") in ("smpte2084", "arib-std-b67"):
        raise ValueError("This SDR 8-bit renderer requires a compatible master; preserve HDR/other formats separately")
    return info


def frame_clock(path, info):
    data = probe(path, "v:0", "frame=best_effort_timestamp")
    pts = [int(frame["best_effort_timestamp"]) for frame in data["frames"]]
    if not pts or any(second <= first for first, second in zip(pts, pts[1:])):
        raise ValueError(f"Missing or non-increasing video timestamps in {path}")
    origin = pts[0]
    tick = Fraction(info["time_base"])
    return [(value - origin) * tick for value in pts]


def verify_clock(path, info, reference, expected):
    if (info["width"], info["height"]) != (reference["width"], reference["height"]):
        raise ValueError(f"Frame geometry differs from the original: {path}")
    actual = frame_clock(path, info)
    if len(actual) != len(expected):
        raise ValueError(f"Frame count differs: expected {len(expected)}, got {len(actual)}")
    tolerance = max(Fraction(info["time_base"]), Fraction(reference["time_base"]))
    for index, (a, b) in enumerate(zip(actual, expected)):
        if abs(a - b) > tolerance:
            raise ValueError(f"Timestamp mismatch at frame {index} in {path}")
    if abs(float(info["duration"]) - float(reference["duration"])) > max(0.002, float(tolerance)):
        raise ValueError(f"Last-frame duration differs from source: {path}")


def ink_bounds(logo):
    info = stream(logo, "v:0")
    width, height = info["width"], info["height"]
    alpha = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(logo), "-frames:v", "1",
                                     "-vf", "format=rgba,alphaextract,format=gray", "-f", "rawvideo", "-"])
    if len(alpha) != width * height or max(alpha) < 128 or min(alpha) > 12:
        raise ValueError("Logo must have a transparent background and a visible wordmark")
    # Discard only near-invisible padding. Otherwise the measured size would refer to the PNG canvas.
    points = [index for index, value in enumerate(alpha) if value > 12]
    xs = [index % width for index in points]
    ys = [index // width for index in points]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


def mark_filter(size, ink, box):
    width, height = size
    if box is None:
        bw, bh = max(1, round(width * .20)), max(1, round(height * .065))
        box = width - bw - round(width * .018), round(height * .03), bw, bh
    bx, by, bw, bh = box
    if min(bx, by) < 0 or min(bw, bh) < 1 or bx + bw > width or by + bh > height:
        raise ValueError("Watermark rectangle must be inside the full-size video")
    ix, iy, iw, ih = ink
    factor = min(bw / iw, bh / ih)
    w, h = max(1, round(iw * factor)), max(1, round(ih * factor))
    x, y = bx + (bw - w) // 2, by + (bh - h) // 2
    # A transparent pixel of padding lets a 4:2:0 overlay start on an odd original-image coordinate.
    dx, dy = x % 2, y % 2
    tile_w, tile_h = 2 * ((w + dx + 1) // 2), 2 * ((h + dy + 1) // 2)
    print(f"Visible logo {w}x{h} at ({x},{y}); target rectangle {tuple(box)}", flush=True)
    label = (f"[2:v]format=rgba,crop={iw}:{ih}:{ix}:{iy}:exact=1,scale={w}:{h}:flags=lanczos,"
             f"format=rgba,pad={tile_w}:{tile_h}:{dx}:{dy}:color=black@0,setsar=1[mark];")
    return label + f"[base][mark]overlay={x-dx}:{y-dy}:eof_action=repeat:repeatlast=1[out]"


def badge_filter(width, height, logo, box):
    """Anchor the approved opaque artwork to the top-right of the active picture."""
    mark = stream(logo, "v:0")
    ratio = Fraction(mark["width"], mark["height"])
    needed_w, needed_h = max(2, round(width * 224 / 1440)), 0
    if box:
        x, y, w, h = box
        if min(x, y) < 0 or min(w, h) <= 0 or x + w > width or y + h > height:
            raise ValueError("Measure the watermark on the cropped picture")
        needed_w, needed_h = max(needed_w, width - x), y + h
    # Choose even dimensions and preserve the entire mark including its opaque backing.
    w = 2 * ceil(max(needed_w, needed_h * ratio) / 2)
    h = 2 * ceil(w / ratio / 2)
    if w > width or h > height:
        raise ValueError("The detected mark needs shot-specific masking")
    return (f"[2:v]scale={w}:{h}:flags=lanczos,setsar=1[badge];"
            f"[base][badge]overlay={width-w}:0:eof_action=repeat:repeatlast=1[out]")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("video", "audio", "output"):
        p.add_argument("--" + name, required=True, type=Path)
    p.add_argument("--reference", type=Path, help="Original media used to check geometry and presentation timestamps")
    p.add_argument("--box", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
    p.add_argument("--ass", type=Path, help="Omit for a master with approved bilingual captions")
    branding = p.add_mutually_exclusive_group()
    branding.add_argument("--logo", type=Path, help="Transparent wordmark for older projects")
    branding.add_argument("--badge", type=Path, help="Opaque upper-right badge for the cropped picture")
    args = p.parse_args()
    if args.box and not (args.logo or args.badge):
        p.error("--box requires --badge or --logo")
    video, audio, output = (item.resolve() for item in (args.video, args.audio, args.output))
    subtitles = args.ass.resolve() if args.ass else None
    reference = (args.reference or video).resolve()
    if output.exists():
        raise ValueError(f"Choose a new output path: {output}")
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output must be an MP4 file")
    info = video_info(video)
    ref = info if reference == video else video_info(reference)
    expected = frame_clock(reference, ref)
    if video != reference:
        verify_clock(video, info, ref, expected)
        for field in ("color_range", "color_space", "color_primaries", "color_transfer"):
            if info.get(field) != ref.get(field):
                raise ValueError(f"Normalize and check source and clean-master {field} before export")
    a = stream(audio, "a:0")
    tolerance = max(.06, 1 / float(Fraction(ref["avg_frame_rate"])))
    if abs(float(a.get("start_time", 0))) > .002 or abs(float(a["duration"]) - float(ref["duration"])) > tolerance:
        raise ValueError("Supply a full-duration final mix aligned to zero before rendering")
    if subtitles and not subtitles.is_file():
        raise ValueError(f"Missing ASS: {subtitles}")
    graph = "[0:v]setpts=PTS-STARTPTS"
    if subtitles:
        graph += ",ass=captions.ass:shaping=auto"
    logo_input = []
    if args.badge:
        badge = args.badge.resolve()
        logo_input = ["-i", str(badge)]
        graph += "[base];" + badge_filter(info["width"], info["height"], badge, args.box)
    elif args.logo is None:
        graph += "[out]"
    else:
        logo = args.logo.resolve()
        logo_input = ["-i", str(logo)]
        graph += "[base];" + mark_filter((info["width"], info["height"]), ink_bounds(logo), args.box)
    tags = []
    for field, flag in (("color_range", "-color_range"), ("color_space", "-colorspace"),
                        ("color_primaries", "-color_primaries"), ("color_transfer", "-color_trc")):
        if info.get(field) not in (None, "unknown", "unspecified", "reserved"):
            tags += [flag, info[field]]
    codec = ["-c:a", "copy"] if a["codec_name"] == "aac" else ["-c:a", "aac", "-b:a", "256k"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as work:
        tmp = Path(work)
        if subtitles:
            (tmp / "captions.ass").symlink_to(subtitles)
        stage = tmp / "render.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(video), "-i", str(audio),
                        *logo_input, "-filter_complex", graph, "-map", "[out]", "-map", "1:a:0",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                        "-fps_mode:v", "passthrough", "-enc_time_base:v", info["time_base"],
                        "-video_track_timescale", str(Fraction(info["time_base"]).denominator),
                        *tags, *codec, "-metadata:s:a:0", "language=eng", "-movflags", "+faststart",
                        str(stage)], cwd=tmp, check=True)
        verify_clock(stage, video_info(stage), ref, expected)
        mixed = stream(stage, "a:0")
        if abs(float(mixed["duration"]) - float(a["duration"])) > tolerance:
            raise ValueError("Final audio duration differs from the input mix")
        os.link(stage, output)
    print(f"Saved {len(expected)} frames to {output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
