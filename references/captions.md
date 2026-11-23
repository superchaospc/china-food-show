# Time captions to speech and on-screen text

For dubbed dialogue, copy the words from the final recorded turns and check them against the final audio. Time the cues to audible phrases and speaker changes. One Chinese on-screen line can span several English replies. For a menu, title or other written-only caption, translate the visible words and retain their original frame interval and gaps.

## Locate the source text

Start with platform captions when available and check against the picture. On macOS, the optional Vision OCR tool samples a rectangle in display coordinates. This example uses one subtitle band on a 1920 by 1080 frame. Measure the band again for every source.

```sh
swiftc -O scripts/scan_zh.swift -o /tmp/scan_zh
/tmp/scan_zh source.mp4 200 890 1520 100 0.2 > ocr.jsonl
```

Each sample contains a timestamp and observed words with bounding boxes. Sample more frequently around short flashes or use frame-by-frame inspection. Keep the source OCR record. Arrange the final English cues in a UTF-8 JSON array in display order. Use zero-based frame indices and an exclusive end. All prose in the example below is a placeholder; replace the source field with the actual original text.

```json
[
  {
    "start_frame": 0,
    "end_frame_exclusive": 91,
    "zh": "Original caption text",
    "en": "Bag or bowl?",
    "margin_v": 188
  }
]
```

Keep the price wording the speaker used. When a conversion is useful, display it in a separate note using the episode’s dated exchange rate and the correct portion. Keep this note outside the dialogue ASS/SRT text and the dialogue verification region. Verify each visible upper and lower outline when placing the English text closely above the original; the margin is in canvas pixels. Intentional line breaks can be encoded with JSON newline escapes. Each cue may specify a different `font_size`.

For white text with a dark outline, add the rough frame bounds and `bbox` as `[x, y, width, height]` for the visible text in each row. Use a Python environment with NumPy and OpenCV to refine the boundaries:

```sh
python3 scripts/refine_edges.py source.mp4 rough.json cues.json
```

Review intervals marked `needs_review`; exit status 2 signals that some need attention. Check the source frames, correct their bounds and mark them `reviewed`. A fade, textured background, moving caption or several caption positions can require manual inspection. Inspect the rest of the clip for short captions the coarse OCR missed.

## Generate and verify

```sh
python3 scripts/captions.py source.mp4 cues.json captions/
```

This writes `english.ass` and `english.srt` from the same cue text. Compare the dialogue from both files in order with the final recorded script, allowing punctuation, capitalization and line breaks. Review any missing, added or substituted words against the audio before rendering. The timing uses actual presentation timestamps, with switches between neighboring frames so rounding to ASS centiseconds does not shift a cut. If the source has no visible subtitles, supply `zh_margin_v` for every cue, use `--add-chinese`, and render the resulting `bilingual.ass`. Omit speech and captions where the scene calls for neither.

Verify the delivered video against a frame-aligned reference without the English text, using an ROI that contains every English glyph but excludes unrelated edits. Example for a lower subtitle band:

```sh
python3 scripts/verify_captions.py source.mp4 final.mp4 cues.json \
  captions/english.ass --roi 0,760,1920,144
```

This uses NumPy and FFmpeg to decode frames and compare visible English glyphs and blank intervals. For a newly added bilingual layer, keep the Chinese region outside this ROI or supply a reference with the same Chinese layer. Inspect failures in the output around each affected frame, then rerun after corrections. Also check readability, spelling, speaker attribution and layout at normal playback size.
