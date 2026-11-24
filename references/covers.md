# Episode posters

Deliver two JPEGs for the vertical episode package. Use 1080 × 1440 for 3:4 and 1080 × 1920 for 9:16. Use a single UTF-8 `Title and Description.txt` alongside them.

## Select the selling point before designing the poster

Read the episode title, description and relevant dialogue, then state in one sentence what the viewer can see here that is unusual. Inspect a contact sheet across the whole episode. Compare the reveal with nearby frames at full resolution. If the claim is size, show the item next to a hand, plate or wok for scale. For an unusual location, keep enough of the surroundings to explain where the stall is. For an unfamiliar technique, find the instant the tool, ingredient and result are distinguishable. For a comparison, show the contrasting portions or ingredients. Product placements, generic tasting shots and empty plates usually tell a different story.

A single shot works when the hook is visible on its own. When establishing the location or showing a transformation takes two moments, use two real frames from the same episode. Keep the same visual story in both ratios and compose each crop separately. Retain the actual extent of the portion and the setting. Check at phone size that someone can identify the hook before reading the headline.

Use English copy and the approved series identity. Check source pixels for captions, signs, packaging and watermarks. Use a clean crop or a nearby sharp frame. For prices use the episode's verified USD conversion and preserve the unit. On text-only revisions keep the approved photograph and arrangement. On image-selection revisions compare new candidates and update both posters.

## Render and verify

`scripts/covers.py --still chosen.jpg --hook 'Ten Eggs, No Flour' --location 'China' --output-dir covers` renders both portrait formats. Use `--portrait-focus X,Y` for the subject, and `--only 9x16` or `--only 3x4` for a missing size. A composition with multiple photos can use an episode-specific publishing template. Legacy landscape sizes remain available by explicit request. When updating a delivered poster, render in a staging directory, compare both final crops, and replace the corresponding file in place.

Open both exported images. Confirm the episode, crop, type, price and portion, focus, clean edges and actual pixel dimensions. The 9:16 title needs enough room to read without covering the evidence in the photo.
