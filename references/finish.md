# Prepare and export the picture

## Source repair

Use these steps for footage you own or have permission to edit. If the source already has a clean master, use it directly.

1. Inspect the original in display orientation. Measure each unwanted mark, including its shadow, using full-size frame coordinates. Inspect cuts for changes in position. Preserve any subtitles, signs, menus or prices that should remain visible.
2. Prefer the Watermark Remover in HitPaw Edimakor when repair is needed. Import the original and verify the selection against a frame containing the entire mark. Recheck the estimated cost and available balance with the exact file and selection loaded. A public installation has no spending authorization by default. Obtain approval for the quoted job or apply an existing per-job budget precisely, including its boundary. Record the receipt, continue tracking the same submission, and recover a stalled download before considering a new charge.
3. Before adding a logo, check motion in the repaired area. Look for tearing across an edge, duplicated textures, or a patch that moves one frame behind the surrounding picture. Compare cut boundaries and fast motion in the original and returned files. Match frames by content away from the repaired area; equal lengths and frame counts alone can conceal an offset.
4. If the service resizes or softens the entire video, map the verified repair back to source coordinates and composite only the affected pixels over the original. Feather the outside edge of the mark and keep its center fully covered. Preserve the original color matrix, range, geometry and display timestamps. A VFR source needs its actual frame correspondence and timestamps; average FPS alone is insufficient.

## Export

Prepare an aligned clean master, a finished mix starting at zero, and an ASS file with the same display geometry. For sources with visible subtitles use English ASS. If both languages need to be burned in, use the combined ASS produced by the caption tool.

```sh
python3 scripts/render.py --reference source.mp4 --video clean.mp4 \
  --ass captions/english.ass --audio mix.m4a --output final.mp4
```

For branding, append `--logo /path/to/your-transparent.png`. Add `--box X Y WIDTH HEIGHT` to fit its visible lettering into a measured rectangle. Coordinates start at the top left. Transparent canvas padding is excluded from the measurement and the image retains its proportions. Omit the box to use the default upper-right placement. No logo or music is distributed with this project.

The renderer handles square-pixel, display-oriented, 8-bit SDR 4:2:0 masters with readable video duration and increasing presentation timestamps. It encodes H.264, preserves the frame clock, copies an AAC mix or encodes other supported input audio as AAC, then verifies the staged export before publishing the requested new file. Prepare a compatible master or use an appropriate finishing workflow for HDR, rotated or non-square-pixel material.

## Delivery checks

Decode the export. Compare runtime, frame count, timestamps, and the audio mix with their inputs. Compare both the English SRT and the words burned into the MP4 against the approved dub. Include short answers, overlap and price mentions. Use the [caption workflow](captions.md) to verify zero-frame differences between Chinese and English onsets, switches, ends and gaps. Check the SRT boundaries too. Every source price must have an inline USD equivalent on the same line in both outputs. Correct any deviation before delivery. Watch difficult motion at normal speed and look at the logo against both bright and dark backgrounds. Listen through speaker changes, cooking sounds and quiet passages. Place the verified MP4 in the [episode delivery folder](../SKILL.md#final-delivery). Keep the matching English SRT in the episode workspace for future checks. Keep reusable voice caches, media, receipts and project files in your private workspace.
