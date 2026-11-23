#!/usr/bin/env python3
"""Plan timestamped ElevenLabs speech turns; --generate uses the resolved voice IDs and a resumable cache."""
import argparse
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.error
import urllib.request


def write(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
    os.replace(handle.name, path)


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()


def prepare(plan):
    model = plan["model_id"]
    cast = plan["cast"]
    seen_ids = set()
    turns = []
    for line in plan["turns"]:
        turn_id, speaker, text = line["id"], line["speaker"], line["text"].strip()
        if not turn_id or turn_id in seen_ids or not text:
            raise ValueError("Each turn needs a unique nonempty id and spoken text")
        seen_ids.add(turn_id)
        voice = cast[speaker]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", voice):
            raise ValueError("Resolve an actual voice ID for each active speaker")
        body = {"text": text, "model_id": model, "language_code": "en"}
        for opt in ("previous_text", "next_text", "voice_settings"):
            if opt in line:
                body[opt] = line[opt]
        fingerprint = hashlib.sha256(encoded({"voice_id": voice, "body": body, "format": "mp3_44100_128"})).hexdigest()
        turns.append((turn_id, voice, body, fingerprint))
    return turns


def generate_one(cache, voice, body, authorize):
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (cache / "lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        audio = cache / "audio.mp3"
        alignment = cache / "alignment.json"
        if (cache / "ready").is_file() and audio.is_file() and audio.stat().st_size and alignment.is_file():
            return
        # If we received the response but crashed before publishing the files, finish offline.
        raw = cache / "response.json"
        if not raw.exists():
            if (cache / "submitted.json").exists():
                raise RuntimeError(f"Pending receipt in {cache.name}; reconcile with ElevenLabs history before any new charge")
            key = authorize()
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
                data=encoded(body), headers={"xi-api-key": key, "Content-Type": "application/json"})
            write(cache / "submitted.json", encoded({"voice_id": voice, "body": body}))
            try:
                with urllib.request.urlopen(req, timeout=240) as response:
                    payload = response.read()
                    headers = {k:v for k,v in response.headers.items()
                               if k.lower() in ("request-id", "history-item-id", "character-cost")}
                    write(raw, payload)
                    write(cache / "receipt.json", encoded(headers))
            except urllib.error.HTTPError as err:
                raise RuntimeError(f"ElevenLabs HTTP {err.code} for {cache.name}; inspect the account and request before retry") from None
        result = json.loads(raw.read_bytes())
        speech = base64.b64decode(result.pop("audio_base64"), validate=True)
        if not speech or not (result.get("alignment") or result.get("normalized_alignment")):
            raise ValueError("Incomplete timestamped output; recover this generation from history")
        write(audio, speech)
        subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name",
                        "-of", "csv=p=0", str(audio)], stdout=subprocess.DEVNULL, check=True)
        write(alignment, encoded(result))
        write(cache / "ready", b"ok\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("plan", type=Path)
    p.add_argument("cache", type=Path)
    p.add_argument("--generate", action="store_true", help="Submit uncached turns after the production agent has reviewed cast, cost and permissions")
    a = p.parse_args()
    turns = prepare(json.loads(a.plan.read_text()))
    def key():
        if not os.environ.get("ELEVENLABS_API_KEY"):
            raise RuntimeError("Use the execution host's configured ElevenLabs credential in the process environment")
        return os.environ["ELEVENLABS_API_KEY"]
    unique = {fingerprint: body for _,_,body,fingerprint in turns}
    print(json.dumps({"turns":len(turns), "uncached_characters":sum(len(body["text"]) for f,body in unique.items()
                      if not (a.cache/f/"ready").exists()),"outputs":{i:str(a.cache/f/"audio.mp3") for i,_,_,f in turns}},
                     ensure_ascii=False, indent=2), flush=True)
    if a.generate:
        for _, voice, body, fingerprint in turns:
            generate_one(a.cache/fingerprint, voice, body, key)


if __name__ == "__main__":
    main()
