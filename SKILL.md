---
name: china-food-show
description: Produce an English edition of a Chinese street-food, restaurant or market video from a link or local file, with speaker-aware dubbing, English captions synchronized to visible source captions, optional music and a transparent channel logo, and English-only landscape and portrait covers.
---

# The China Food Show

Use this workflow when a user wants a finished English edition of a food video. If the user supplies only a link in a project that uses this workflow by default, inspect the title or sample first. Respect requests to download, analyze, or revise only one element separately.

1. **Prepare the source.** Run `scripts/episode.py URL` to locate the workspace. Obtain the authorized video through the user's downloader, or reuse an existing source. Bind the local file with `scripts/episode.py URL --source FILE`. Record geometry, display rotation, timestamps and audio streams. Use the same workspace when resuming. For links with multiple parts, process the requested part.
2. **Prepare a clean picture.** If an authorized source needs watermark repair, prefer dedicated software such as HitPaw Edimakor's Watermark Remover. Read the actual quote against the user's current approval before submitting. Assign one operator per paid job and recover the existing result after interruptions. Preserve the existing captions. Check moving textures before adding a new logo. See [Finishing](references/finish.md).
3. **Build the caption timeline from the picture.** Measure the first visible frame and first absent frame of each source caption. Translate for a listener who has never seen the dish. Keep short questions and replies natural. When a price matters, preserve the original currency and add an approximate USD equivalent using a dated rate. Place English immediately above the source line. Use `--add-chinese` for a source that needs both languages burned in. See [Captions](references/captions.md).
4. **Cast the speakers you hear.** Use the creator's authorized voice for the host when one is configured. Pick a distinct, consistent voice for each other meaningful speaker. Leave speech-free scenes without narration. Keep the picture caption timeline separate from spoken turn timings. Check planned text, voice identities, and billing authorization before paid generation. Use a clean ambience stem and optionally mix a user-supplied music bed. See [Audio](references/audio.md).
5. **Render and check the decoded export.** Use the validated, full-length clean picture, ASS captions and aligned final audio mix. Supply a transparent PNG and the measured original watermark rectangle only when appropriate. Preserve native frame timing; check all subtitle changes, blank intervals, repaired moving edges, speech assignment and audio peaks. Keep the approved MP4 and its matching English SRT for delivery. Record any remaining defects or unverified stages.

## Episode covers

Deliver a separate landscape YouTube thumbnail and portrait TikTok cover asset using [Cover design](references/covers.md). Inspect actual episode frames before choosing the dish, action, location and headline. Use only English cover text and check the background at full size for Chinese captions, signs and packaging. Prefer warm documentary food photography, a clear human action, and bold white type with a restrained yellow accent. Compose each aspect ratio independently. Keep the cover artwork alongside the video. Posting to a platform is a separate user action.

## Final delivery

Create one folder per episode directly under the user's Downloads directory, named `The China Food Show - <episode name>`. When a worker machine renders the episode, transfer the finished files to the user's delivery computer. Place the approved MP4, matching English SRT, both final JPEG covers, `Title.txt` and `Description.txt` together at the top level of that folder. Name each cover for its platform and aspect ratio.

Use the approved English YouTube title and posting description, including the selected hashtags and paragraph breaks. If copy has yet to be written, draft it from the facts of this episode. Keep the title and description files ready to paste. Leave production materials in the workspace. For a revision, update the affected files in the same delivery folder. Verify the contents against the approved versions, reveal the folder in Finder on macOS, and return its path.
