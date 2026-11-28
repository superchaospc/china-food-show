# Price posters

Use the same approved square portrait artwork for both posters. For Wayne’s Price Tag, use the existing portrait with the red sign. Add only the episode copy and keep the face and sign visible in both crops. Supply your own image with `--profile`, or install the artwork locally at `assets/wayne-price-tag-profile.png`.

Verify the price, exchange rate and portion. The standard headline states the price and food, for example **$5 FOR ONE SLICE OF PORK**. For a per-person buffet, use **$1.5 PER PERSON** on the first line and **ALL YOU CAN EAT** on the second. Check that the footage supports the offer. Align the first line on one typographic baseline and leave the dollar sign’s descender intact. Use an uppercase location, such as **CHONGQING**. Omit footer copy by default.

```sh
python3 scripts/profile_posters.py --profile portrait.png \
  --location 'Chongqing' --usd 1.5028 --usd-decimals 1 \
  --unit 'PER PERSON' --offer 'ALL YOU CAN EAT' --output-dir posters
```

`--usd` takes the verified conversion. `--usd-decimals` selects zero (default), one or two places with decimal half-up rounding. The renderer drops trailing fractional zeros. Use the precision requested for this episode. The subtitle track keeps the amount to cents. Use the single-line layout if the unit already conveys the offer. Supply an optional footer only when requested for a single-line design.

The command writes `Poster-3x4.jpg` (1080×1440) and `Poster-9x16.jpg` (1080×1920). Use a fresh staging directory for revisions. For an episode without a price, supply a short factual `--headline` instead of price arguments. The macOS layout uses DIN, Georgia and Arial system fonts. On other systems install the DejaVu family including its condensed and italic faces. Check the rendered wording at phone size before replacing delivered files.
