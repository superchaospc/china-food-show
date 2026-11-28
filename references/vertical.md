# Two video formats from one edit

For sources longer than 180 seconds, lock a 179-second edit. Otherwise keep the original runtime unless the user sets another target. Remove repetitions or waits while preserving whole thoughts, the quoted price, the defining action and the outcome. Record the edit points in source frames. Apply them to the picture, isolated voices, clean ambience and caption cues. Score the finished timeline, check every cut, and encode its final AAC once.

Use a fixed center crop. For a 1920×1080 square-pixel source, `crop=1440:1080:240:0` removes 240 pixels on the left and right. Check the action and both caption lines. If a narrow source makes the requested crop incompatible with a key shot or subtitle, identify the affected shot before changing its framing.

From the finished 4:3 master, derive the 9:16 edition by adding equal pure-black bands above and below. Keep the active picture edge to edge and preserve the native detail, frame timing, color and badge placement. For a 1440×1080 SDR master with its approved badge and subtitles:

```sh
ffmpeg -n -i master-4x3.mov -i final-audio.m4a \
  -filter_complex '[0:v]split=2[wide][v];[v]pad=1440:2560:0:740:color=black[tall]' \
  -map '[wide]' -map 1:a:0 -c:v libx264 -crf 15 -preset slow -fps_mode passthrough -pix_fmt yuv420p -c:a copy -movflags +faststart episode-4x3.mp4 \
  -map '[tall]' -map 1:a:0 -c:v libx264 -crf 15 -preset slow -fps_mode passthrough -pix_fmt yuv420p -c:a copy -movflags +faststart episode-9x16.mp4
```

Adapt dimensions, pixel format and color metadata to the actual source. Deliver the 4:3 file directly if it is already approved. When recovering it from the vertical master, export actual cropped pixels: some hardware decoders show incorrect boundaries for metadata-only crops. Decode the final files, compare video PTS, frame counts and audio packet payloads, and inspect the central image, bars, subtitle boundaries and cooking action. Check beginning, middle and end with software and hardware playback.
