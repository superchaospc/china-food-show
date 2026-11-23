# Episode covers

Deliver three independently composed JPEGs: 3840 x 2160 for YouTube (16:9), 1440 x 1080 for a 4:3 landscape placement, and 1080 x 1440 for TikTok (3:4). Select a still that shows what the hook promises. A vendor lifting a wok, a dish changing hands, or a tight serving shot usually reads better at thumbnail size than a crowded counter.

## Select the frames and words

Start from full-resolution licensed footage before subtitles and logos are burned in. Choose one text-free master image that shows the dish clearly in all three crops. If creating artwork from episode frames, match the actual ingredients and serving context. Place the focal action toward the right half of the YouTube image to allow for the headline on the left. For the narrower 4:3 landscape frame, keep the subject and headline inside its edges, using a tighter type block if needed. For TikTok, look for a vertical arrangement with the subject in the upper half and quiet space below it.

Build the covers around authentic food and human action from the episode. Use large, bold type in warm yellow and ivory with a short rule beneath the title. Keep the portrait title low and clear of its subject. Any light weathering you add in a design editor should preserve the letterforms at phone size. Use the episode’s own photographic identity and original typography. Avoid another show’s host, artwork, logos, or title marks.

When the user approves a cover and asks for new wording, edit the text on the approved landscape and portrait originals. Preserve the photograph, crop, large series title, and separator rules. The command below composes new covers from clean stills.

Use a brief, factual English hook. Show prices in US dollars on covers and in the English publishing title and description. Convert using the episode’s dated rate and preserve the serving size. For example, a serving priced at about US$7.49 can use “Worth $7.49?” Keep any price, location, or claim consistent with the episode. A shorter portrait hook can help retain a readable size. Include a location only when it helps the viewer.

Inspect all three source crops for Chinese characters. Check signs, labels, menus, packaging, clothing, reflections, old captions, and background watermarks. For an English-only result, choose a clean alternate frame or crop the writing out before rendering. Do not cover writing with a headline and assume it has disappeared. The script validates supplied text. It cannot confirm the language of pixels in a photograph.

## Render the covers

Install Pillow and use a locally installed bold font. Run the command from the repository root.

```sh
python3 scripts/covers.py \
  --still frames/serving-wide.jpg \
  --hook 'Every Dish Is $1.80' \
  --location 'Sichuan, China' \
  --output-dir covers
```

The required arguments are `--still`, `--hook`, and `--output-dir`. Pass the same master once via `--still` to compose all three covers. Use `--wide-focus 0.74,0.44` or `--portrait-focus 0.61,0.38` to identify the subject in normalized coordinates measured from the top left of its source still. Use `--four-three-focus` to position the subject in the 4:3 crop. When adding a missing 4:3 image to an existing pack, pass `--only 4x3`. Existing files are preserved. Pass `--font` to use a particular local TTF or OTF file.

Inspect meat fibers, food edges and other subject details at full size in each crop. Choose a sharper still or episode-based master if camera or subject motion smears the food. Open every exported JPEG at full resolution to check every edge for visible Chinese text. Then inspect them at phone-thumbnail size. Confirm that hands, faces, the key dish, and the English headline remain readable in their respective crops. If a crop fails, adjust its focus and render it again. If you need a different master image, regenerate the full set from that image.

## Publishing

- `youtube-16x9.jpg` is a custom thumbnail for a regular YouTube video. The script exports a 16:9 image at the recommended 3840 x 2160 size and keeps the JPEG within 2 MB. [YouTube thumbnail guidance](https://support.google.com/youtubecreatorstudio/answer/72431?hl=en)
- `landscape-4x3.jpg` is the 1440 x 1080 landscape cover. Keep it alongside the other covers in the episode delivery folder.
- `tiktok-3x4.jpg` is a portrait editorial cover asset. TikTok documents selecting a frame from the video on the posting screen. If the posting workflow offers frame selection, choose the intended frame from the video or prepare a separate posting cut that incorporates the cover when appropriate. [TikTok cover selection](https://support.tiktok.com/en/using-tiktok/creating-videos/editing-posting-and-deleting)
