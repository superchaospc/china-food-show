#!/usr/bin/env python3
"""Typeset a pair of episode posters on the approved Wayne's Price Tag portrait."""
import argparse
import os
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ASSETS = Path(__file__).resolve().parents[1] / "assets"
FONTS = Path("/System/Library/Fonts/Supplemental")
CREAM, GOLD, MATTE = "#FFF0CE", "#E6BB72", "#151310"


def font(name, size):
    native = FONTS / name
    if native.is_file():
        return ImageFont.truetype(str(native), size)
    fallback = {
        "DIN Alternate Bold.ttf": "DejaVuSans-Bold.ttf",
        "DIN Condensed Bold.ttf": "DejaVuSansCondensed-Bold.ttf",
        "Georgia Italic.ttf": "DejaVuSerif-Italic.ttf",
        "Arial.ttf": "DejaVuSans.ttf",
    }
    return ImageFont.truetype(fallback[name], size)


def lettering(text, face, color):
    box = face.getbbox(text)
    glyph = Image.new("RGBA", (box[2] - box[0] + 4, box[3] - box[1] + 4))
    ImageDraw.Draw(glyph).text((2 - box[0], 2 - box[1]), text, font=face, fill=color)
    return glyph.crop(glyph.getbbox())


def draw_poster(face, height, location, dish, lead, unit, original, offer=""):
    short = height == 1440
    photo = face.crop((0, 0, 1254, 1254) if short else (154, 0, 1110, 1254))
    photo_height = round(photo.height * 1080 / photo.width)
    poster = Image.new("RGB", (1080, height), MATTE)
    poster.paste(photo.resize((1080, photo_height), Image.Resampling.LANCZOS))
    draw = ImageDraw.Draw(poster)
    panel, pad = height - photo_height, 54
    kicker = lettering(location.strip().upper(), font("DIN Alternate Bold.ttf", 30 if short else 35), GOLD)
    if kicker.width > 1080 - 2 * pad:
        raise ValueError("Shorten the location to fit the poster")
    y = photo_height + round(panel * .10)
    poster.paste(kicker, (pad, y), kicker)
    if pad + kicker.width + 22 < 1080 - pad:
        draw.line((pad + kicker.width + 22, y + kicker.height // 2, 1080 - pad, y + kicker.height // 2), fill="#866D4E", width=2)
    face_type = font("DIN Condensed Bold.ttf", 245)
    if unit:
        label = unit.upper()
        left = face_type.getbbox(lead, anchor="ls")
        right = face_type.getbbox(label, anchor="ls")
        label_x = left[2] + 40 - right[0]
        top = min(left[1], right[1])
        bottom = max(left[3], right[3])
        line = Image.new("RGBA", (label_x + right[2] - left[0], bottom - top))
        title = ImageDraw.Draw(line)
        title.text((-left[0], -top), lead, font=face_type, fill=GOLD, anchor="ls")
        title.text((label_x - left[0], -top), label, font=face_type, fill=CREAM, anchor="ls")
        line = line.crop(line.getbbox())
    else:
        line = lettering(lead, face_type, GOLD)
    scale = min((930 if short else 1080 - 2 * pad) / line.width, round(panel * (.49 if short else .40)) / line.height)
    line = line.resize((max(1, round(line.width * scale)), max(1, round(line.height * scale))), Image.Resampling.LANCZOS)
    if line.height < 64:
        raise ValueError("Shorten the headline so it stays readable on a phone")
    title_y = photo_height + round(panel * (.235 if short else .30))
    poster.paste(line, (pad, title_y), line)
    if offer:
        if dish or original:
            raise ValueError("The two-line headline uses the footer space. Omit --dish and --original.")
        second = lettering(offer.upper(), font("DIN Condensed Bold.ttf", 96 if short else 139), CREAM)
        bottom = height - (23 if short else 41)
        available = bottom - (title_y + line.height + 8)
        factor = min(1, (1080 - 2 * pad) / second.width, available / second.height)
        if round(second.height * factor) < 45:
            raise ValueError("Shorten the offer so both headline lines stay readable")
        if factor < 1:
            second = second.resize((round(second.width * factor), round(second.height * factor)), Image.Resampling.LANCZOS)
        poster.paste(second, (pad, bottom - second.height), second)
        return poster
    y = photo_height + round(panel * (.875 if short else .81))
    dish_font = font("Georgia Italic.ttf", 43 if short else 50)
    price_font = font("Arial.ttf", 33 if short else 37)
    if dish_font.getlength(dish) + price_font.getlength(original) + 30 > 1080 - 2 * pad:
        raise ValueError("Shorten the dish name or the original-currency label")
    draw.text((pad, y), dish, font=dish_font, fill=CREAM, anchor="lm")
    draw.text((1080 - pad, y), original, font=price_font, fill=GOLD, anchor="rm")
    return poster


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=ASSETS / "wayne-price-tag-profile.png",
                        help="Approved square portrait artwork")
    parser.add_argument("--location", required=True)
    parser.add_argument("--dish", default="", help="Optional short dish caption in the footer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--usd", help="verified, unrounded US dollar amount")
    group.add_argument("--headline", help="short factual headline for episodes without a price")
    parser.add_argument("--unit", default="")
    parser.add_argument("--original", default="")
    parser.add_argument("--offer", default="", help="Second headline line, such as ALL YOU CAN EAT")
    parser.add_argument("--usd-decimals", type=int, choices=(0, 1, 2),
                        help="Poster price precision; default is whole dollars")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.usd is not None:
        value = Decimal(args.usd)
        if not value.is_finite() or value < 0 or not args.unit.strip():
            parser.error("--usd requires a nonnegative, finite amount and a --unit")
        precision = Decimal(1).scaleb(-(args.usd_decimals or 0))
        amount = value.quantize(precision, rounding=ROUND_HALF_UP)
        price = format(amount, "f")
        lead = "$" + (price.rstrip("0").rstrip(".") if "." in price else price)
    else:
        if args.unit or args.original or args.usd_decimals is not None:
            parser.error("Price labels require --usd")
        lead = args.headline.strip().upper()
    if not all(text.strip() for text in (lead, args.location)):
        parser.error("Location and headline must contain text")
    if not args.profile.is_file():
        parser.error("Supply an approved square portrait with --profile")
    with Image.open(args.profile) as source:
        face = ImageOps.exif_transpose(source).convert("RGB")
    if face.width != face.height:
        parser.error("Supply a square crop of the approved portrait")
    if face.size != (1254, 1254):
        face = face.resize((1254, 1254), Image.Resampling.LANCZOS)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output_dir) as tmp:
        files = []
        for name, height in (("Poster-3x4.jpg", 1440), ("Poster-9x16.jpg", 1920)):
            target = args.output_dir / name
            if target.exists():
                raise FileExistsError(f"Use an empty staging directory: {target}")
            image = draw_poster(face, height, args.location, args.dish, lead, args.unit, args.original, args.offer.strip())
            stage = Path(tmp) / name
            image.save(stage, quality=97, subsampling=0, optimize=True)
            files.append((stage, target))
        published = []
        try:
            for stage, target in files:
                os.link(stage, target)
                published.append(target)
        except OSError:
            for target in published:
                target.unlink()
            raise


if __name__ == "__main__":
    try:
        main()
    except (ValueError, InvalidOperation, OSError) as exc:
        raise SystemExit(str(exc))
