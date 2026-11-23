#!/usr/bin/env python3
"""Locate the episode workspace for a video link, optionally bind a verified local source."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import parse_qs, urlsplit


def identify(link):
    parsed = urlsplit(link)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Expected a video link starting with http:// or https://")
    if parsed.hostname == "bilibili.com" or parsed.hostname.endswith(".bilibili.com"):
        match = re.fullmatch(r"/video/(BV[0-9A-Za-z]+|av[0-9]+)/?", parsed.path)
        if match:
            part = parse_qs(parsed.query).get("p", ["1"])[0]
            if part.isdecimal() and int(part) >= 1:
                return match[1] if int(part) == 1 else f"{match[1]}-p{int(part)}"
    # Preserve meaningful query parameters outside known video URLs without storing their values.
    return "video-" + hashlib.sha256(link.encode()).hexdigest()[:24]


def describe(source):
    command = ["ffprobe", "-v", "error", "-show_entries",
               "format=duration:stream=index,codec_type,codec_name,width,height,avg_frame_rate,nb_frames,sample_rate:stream_disposition=attached_pic:stream_side_data=rotation",
               "-of", "json", str(source)]
    media = json.loads(subprocess.check_output(command))
    if not any(s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")
               for s in media.get("streams", [])):
        raise ValueError("Source has no video stream")
    hasher = hashlib.sha256()
    with source.open("rb") as fd:
        for block in iter(lambda: fd.read(4 * 1024 * 1024), b""):
            hasher.update(block)
    return {"source_path": str(source), "source_sha256": hasher.hexdigest(), "media": media}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--root", type=Path, default=Path.home() / "Movies" / "The China Food Show")
    parser.add_argument("--source", type=Path, help="Source already downloaded or recovered for this link")
    parser.add_argument("--dry-run", action="store_true", help="Inspect the link and optional source without writing or using the network")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    key = identify(args.url)
    job = root / key
    record = {"episode": key, "workspace": str(job)}
    if args.source:
        record.update(describe(args.source.expanduser().resolve(strict=True)))
    if args.dry_run:
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return
    job.mkdir(parents=True, exist_ok=True, mode=0o700)
    manifest = job / "episode.json"
    with (job / ".episode.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if manifest.exists():
            old = json.loads(manifest.read_text())
            if old.get("source_sha256") and record.get("source_sha256", old["source_sha256"]) != old["source_sha256"]:
                raise ValueError("Different source for this episode; verify link/part and use a separate workspace for a new cut")
            record = {**old, **record}
        with tempfile.NamedTemporaryFile(mode="w", dir=job, delete=False) as temp:
            json.dump(record, temp, ensure_ascii=False, indent=2)
            temp.write("\n")
        os.replace(temp.name, manifest)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
