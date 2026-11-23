#!/usr/bin/env python3
"""Run an offline two-second source-to-captioned-export check using synthetic media."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def run_script(name, *args, cwd):
    subprocess.run([sys.executable, str(SCRIPTS / name), *args], cwd=cwd, check=True)


def main():
    with tempfile.TemporaryDirectory(prefix="china-food-show-") as tmp:
        job = Path(tmp)
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-f", "lavfi", "-i",
                        "testsrc2=size=640x360:rate=30:duration=2", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "source.mp4"], cwd=job, check=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-f", "lavfi", "-i",
                        "sine=frequency=300:sample_rate=48000:duration=2", "bed.wav"], cwd=job, check=True)
        rows = [{"start_frame": 4, "end_frame_exclusive": 28, "zh": "Source cue one",
                 "en": "Fresh from the wok", "margin_v": 65, "font_size": 25},
                {"start_frame": 30, "end_frame_exclusive": 54, "zh": "Source cue two",
                 "en": "How spicy is it?", "margin_v": 65, "font_size": 25}]
        (job / "cues.json").write_text(json.dumps(rows), encoding="utf-8")
        run_script("captions.py", "source.mp4", "cues.json", "captions", cwd=job)
        run_script("mix-audio.py", "--duration", "2", "--bed", "bed.wav", "--output", "mix.wav", cwd=job)
        run_script("render.py", "--video", "source.mp4", "--ass", "captions/english.ass",
                   "--audio", "mix.wav", "--output", "final.mp4", cwd=job)
        run_script("verify_captions.py", "source.mp4", "final.mp4", "cues.json",
                   "captions/english.ass", "--roi", "0,180,640,130", cwd=job)


if __name__ == "__main__":
    main()
