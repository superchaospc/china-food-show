# Vertical video delivery

Use a 1080 × 1920 canvas. For a 16:9 master, fit the complete picture across the middle (1080 × 608, starting at y=656). Keep both subtitle lines and the final mix. For another aspect ratio, preserve the original geometry; a native 9:16 master does not need a second frame around it.

Use the approved series artwork in the top and bottom panels. For the approved 16:9 layout, the centered top logo is about 876 px wide with about 103 px clear above its first visible mark. The lower panel starts at y=1264. Place the location and two-line episode title on the left, the small logo on the right and the rule below, as a group. The first line of type starts about 36 px below the footage. Fit long titles without colliding with the logo. Verify an actual decoded frame.

Every episode gets a full native-duration vertical MP4. If the source duration exceeds 180.000 seconds, also produce a separate 179.000-second vertical cut. Exactly three minutes gets the full edition alone. Use the transcript, watch the footage on both sides of each proposed edit, and remove redundancy, waits or unrelated promotions first. Keep the setup, distinctive action and outcome. Cut on whole thoughts, keep the final audio and burned-in captions in sync, and check the first and last shots. Verify the exported duration with ffprobe and decode the final files.

For an approved landscape master, prepare two 1080 × 656 PNG panels with the episode title already typeset on the footer. The following example preserves the full programme and its AAC mix.

```sh
ffmpeg -i master.mp4 -i header.png -i footer.png \
  -filter_complex '[1:v]scale=out_color_matrix=bt709,format=yuv420p[h];[2:v]scale=out_color_matrix=bt709,format=yuv420p[f];[0:v]scale=1080:608,setsar=1,pad=1080:1920:0:656[m];[m][h]overlay=0:0[t];[t][f]overlay=0:1264[v]' \
  -map '[v]' -map 0:a:0 -c:v libx264 -crf 19 -pix_fmt yuv420p \
  -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a copy -movflags +faststart full-vertical.mp4
```
