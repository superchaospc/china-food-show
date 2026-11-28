# Prepare and export the picture

## Badge and framing

Lock the edit and center-crop to 4:3. Measure the upper-right watermark, including shadows, in cropped picture coordinates. Use approved opaque artwork covering that rectangle. The Wayne’s Price Tag version uses a black background, white condensed letters and gold rules. Check moving shots and preserve subtitles and menus. Apply the badge to the 4:3 picture before adding black bars. Inspect position changes by shot.

## Export

Prepare an edit-locked 4:3 master, a finished mix starting at zero, and an ASS file with the same display geometry. For sources with visible subtitles use English ASS. If both languages need to be burned in, use the combined ASS produced by the caption tool.

```sh
python3 scripts/render.py --video locked-4x3.mp4 \
  --ass captions/english.ass --audio mix.m4a --badge approved-badge.png --output episode-4x3.mp4
```

Use `--box X Y WIDTH HEIGHT` to cover a measured upper-right mark. The opaque badge scales proportionally from the top-right corner. Supply an image with a fully opaque background. For an already captioned master, omit `--ass` and reuse the existing subtitles. Older transparent wordmark projects can still use `--logo`. Source artwork, voices and music are supplied by the operator.

The renderer handles square-pixel, display-oriented, 8-bit SDR 4:2:0 masters with readable video duration and increasing presentation timestamps. It encodes H.264, preserves the frame clock, copies an AAC mix or encodes other supported input audio as AAC, then verifies the staged export before publishing the requested new file. Prepare a compatible master or use an appropriate finishing workflow for HDR, rotated or non-square-pixel material.

## Delivery checks

Decode the export. Compare runtime, frame count, timestamps, and the audio mix with their inputs. Compare both the English SRT and the words burned into the MP4 against the approved dub. Include short answers, overlap and price mentions. Use the [caption workflow](captions.md) to verify zero-frame differences between Chinese and English onsets, switches, ends and gaps. Check the SRT boundaries too. Every source price must have an inline USD equivalent on the same line in both outputs. Correct any deviation before delivery. Watch difficult motion at normal speed and look at the logo against both bright and dark backgrounds. Listen through speaker changes, cooking sounds and quiet passages. Check the [two video formats](vertical.md) and put both verified MP4 files and both posters in the [episode delivery folder](../SKILL.md#publishing-folder). Keep the matching English SRT in the episode workspace for future checks. Keep reusable voice caches, media, receipts and project files in your private workspace.
