# Price posters

Use the same approved square portrait artwork for both posters. For Wayne’s Price Tag, use the existing portrait with the red sign. Add only the episode copy and keep the face and sign visible in both crops. Supply your own image with `--profile`, or install the artwork locally at `assets/wayne-price-tag-profile.png`.

Lead with what the money buys. Verify the price, exchange rate and portion, then round USD to a whole dollar with decimal half-up rounding. For ¥35 per slice of pork worth US$5.22, use **$5 FOR ONE SLICE OF PORK**. The price and its label share a baseline. The vertical stroke of the dollar sign extends below it. The original currency can appear in small secondary type. The dialogue subtitles retain the precise conversion. Use the requested capitalization for the comma-separated location. A dish already named in the headline needs no separate footer caption.

```sh
python3 scripts/profile_posters.py --profile portrait.png \
  --location 'chengdu, sichuan, china' --usd 5.22 \
  --unit 'FOR ONE SLICE OF PORK' --original '¥35' --output-dir posters
```

The command writes `Poster-3x4.jpg` (1080×1440) and `Poster-9x16.jpg` (1080×1920). Use a fresh staging directory for revisions. For an episode without a price, supply a short factual `--headline` instead of price arguments. The macOS layout uses DIN, Georgia and Arial system fonts. On other systems install the DejaVu family including its condensed and italic faces. Check the rendered wording at phone size before replacing delivered files.
