---
name: china-food-show
description: Produce an English edition of a Chinese street-food, restaurant or market video from a link or local file, with speaker-aware dubbing, English dialogue captions matched to the final dub, optional music and a channel badge, delivered as matching 4:3 and black-padded 9:16 videos plus two portrait posters.
metadata:
  version: "1.3.0"
---

# The China Food Show

Use this workflow when a user wants a finished English edition of a food video. If the user supplies only a link in a project that uses this workflow by default, inspect the title or sample first. Respect requests to download, analyze, or revise only one element separately.

1. **Prepare the source.** Run `scripts/episode.py URL` to locate the workspace. Obtain the authorized video through the user's downloader, or reuse an existing source. Bind the local file with `scripts/episode.py URL --source FILE`. Record geometry, display rotation, timestamps and audio streams. Use the same workspace when resuming. For links with multiple parts, process the requested part.
2. **Lock the edit and composition.** For sources over 3:00, edit to 2:59 before scoring. Otherwise use the source duration unless the user specifies another target. Preserve the order, price, defining action and outcome. Use a fixed, symmetric center crop for 4:3, checking the hands, food and captions across shots. Place an opaque approved badge in the upper-right of the cropped picture, then create the vertical version with equal black bars. See [Finishing](references/finish.md) and [Video geometry](references/vertical.md).
3. **Map the original captions.** Record the source words and their first and last visible frames. Use each measured Chinese interval for its English cue, including every cut and blank frame. Create paired intervals when both languages need new captions. Place English above the original Chinese. See [Captions](references/captions.md).
4. **Cast the speakers you hear.** Use the creator's authorized voice for the host when one is configured. Pick a distinct, consistent voice for each other meaningful speaker. Leave speech-free scenes without narration. Use the words of the final English performance for both burned-in dialogue captions and the English SRT. Group replies inside the corresponding Chinese display interval. Update both after any shortening, substitution or new take. Every price, including a repeated quote, must carry its USD equivalent immediately after the source amount on the same English subtitle line in the MP4 and SRT. Keep the pair together when wrapping. Remove any separate corner price overlay. Check planned text, voice identities, and billing authorization before paid generation. Apply the locked picture cuts to the isolated voices, clean ambience and captions first. Lay a continuous licensed or ElevenLabs score on that timeline, duck under dialogue and check every edit and loop. Use one final AAC mix for both videos. See [Audio](references/audio.md).
5. **Render and check the decoded export.** Use the validated, edit-locked 4:3 picture, ASS captions and aligned final audio mix. Measure the old mark in the cropped picture and cover it including its shadow with the approved opaque badge. Keep the existing bilingual caption treatment, with English above Chinese. Preserve native frame timing; check all subtitle changes, blank intervals, repaired moving edges, speech assignment and audio peaks. Compare the caption words in order with the final recorded turns, including short replies. Check every rendered cue and SRT boundary against the independently measured Chinese frames. Require zero frames of difference at appearances, switches, disappearances and gaps. Correct timing and price-placement failures before delivery. Keep the matching English SRT in the episode workspace for verification and revisions. Record any remaining defects or unverified stages.

## Publishing folder

Deliver exactly four files per episode.

| File | Specification |
| --- | --- |
| Episode 4:3 MP4 | Fixed center crop at source quality. A 1920×1080 source yields 1440×1080. |
| Episode 9:16 MP4 | Center the same complete picture with equal pure-black padding above and below. A 1440×1080 picture fills the width of a 1440×2560 canvas, with 740 black rows above and below. |
| `Poster-3x4.jpg` | 1080×1440, using the creator’s approved portrait artwork. |
| `Poster-9x16.jpg` | 1080×1920, using the same portrait and episode copy. |

On both posters, put the uppercase location above the headline. State the price with its unit on a common baseline. For a buffet, put the verified offer on the next line, for example **$1.5 PER PERSON** above **ALL YOU CAN EAT**. Use the episode’s approved decimal precision, with whole dollars as the default. Leave original-currency and redundant dish footers off by default. See [Poster layout and rendering](references/covers.md).

Keep the source, SRT, edit list, audio stems, English title and description, previews and superseded exports in the workspace. Decode both final MP4s and compare frame timing, captions and AAC packets. Open both JPEGs at phone size. Return the verified delivery folder.
