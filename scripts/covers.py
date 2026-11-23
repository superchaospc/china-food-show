#!/usr/bin/env python3
"""Compose independent English YouTube and TikTok cover images from clean episode stills."""
import argparse
import io
import os
from pathlib import Path
import tempfile
import unicodedata

from PIL import Image, ImageDraw, ImageFont, ImageOps


def english_copy(value):
    value = ' '.join(value.split())
    for ch in value:
        if ch.isascii() or 'LATIN' in unicodedata.name(ch, '') or ch in '’‘“”–—…é':
            continue
        raise argparse.ArgumentTypeError('use English copy, Latin letters and ordinary English punctuation')
    if not value or not any(ch.isalnum() for ch in value):
        raise argparse.ArgumentTypeError('supply a short English title or location')
    return value


def focal_point(value):
    try:
        x, y = (float(part) for part in value.split(','))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('use normalized source coordinates X,Y') from exc
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise argparse.ArgumentTypeError('both focal coordinates must be between 0 and 1')
    return x, y


def select_font(requested):
    choices = [str(requested)] if requested else [
        'DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        'LiberationSans-Bold.ttf', 'arialbd.ttf']
    for choice in choices:
        try:
            ImageFont.truetype(choice, 32)
            return choice
        except OSError:
            pass
    raise ValueError('pass --font with a locally installed bold TTF or OTF file')


def crop_scene(path, size, focus, anchor):
    with Image.open(path) as file:
        photo = ImageOps.exif_transpose(file).convert('RGB')
    w, h = photo.size
    scale = max(size[0] / w, size[1] / h)
    cw, ch = min(w, size[0] / scale), min(h, size[1] / scale)
    left = min(max(focus[0] * w - anchor[0] * cw, 0), w - cw)
    top = min(max(focus[1] * h - anchor[1] * ch, 0), h - ch)
    return photo.resize(size, Image.Resampling.LANCZOS, box=(left, top, left + cw, top + ch))


def title_block(text, face, width, height, ceiling):
    words = text.split()
    for px in range(ceiling, round(ceiling * .52) - 1, -2):
        font = ImageFont.truetype(face, px)
        if any(font.getlength(word) > width for word in words):
            continue
        lines = []
        for word in words:
            if lines and font.getlength(lines[-1] + ' ' + word) <= width:
                lines[-1] += ' ' + word
            else:
                lines.append(word)
        advance = round(px * 1.10)
        if len(lines) <= 3 and advance * len(lines) <= height:
            return font, lines, advance
    raise ValueError('the hook is too long for a thumbnail; shorten it or supply a separate portrait hook')


def shade(photo, portrait):
    # A one-dimensional mask creates a soft fade and leaves the subject end of the still clean.
    ramp = Image.new('L', (256, 1))
    def opacity(i):
        position = i / 255 if portrait else 1 - i / 255
        return round(224 * min(1, max(0, (position - .19) / .66)) ** 1.5)
    ramp.putdata([opacity(i) for i in range(256)])
    if portrait:
        ramp = ramp.transpose(Image.Transpose.ROTATE_270)
    return Image.composite(Image.new('RGB', photo.size, '#151614'), photo, ramp.resize(photo.size))


def compose(path, title, location, face, focus, portrait):
    size = (1080, 1440) if portrait else (3840, 2160)
    w, h = size
    if portrait:
        anchor = (.50, .34)
        x, bottom = round(w*.075), round(h*.865)
        width, height, ceiling = round(w*.85), round(h*.32), round(w*.114)
        label_size, gap = round(w*.040), round(h*.022)
    else:
        anchor = (.72, .48)
        x, bottom = round(w*.056), round(h*.805)
        width, height, ceiling = round(w*.53), round(h*.56), round(h*.131)
        label_size, gap = round(h*.036), round(h*.025)
    canvas = shade(crop_scene(path, size, focus, anchor), portrait)
    draw = ImageDraw.Draw(canvas)
    font, lines, advance = title_block(title, face, width, height, ceiling)
    top = bottom - len(lines)*advance
    warm_yellow, ivory = '#ffcb4f', '#fffaf0'
    for index, line in enumerate(lines):
        ink = warm_yellow if index == 0 else ivory
        draw.text((x, top + index*advance), line, font=font, anchor='lt', fill=ink)
    rule_y = bottom + gap // 6
    draw.rectangle((x, rule_y, x + label_size * 2, rule_y + max(2, label_size // 14)), fill=ivory)
    if location:
        label = location.upper()
        small = ImageFont.truetype(face, label_size)
        if small.getlength(label) > width:
            raise ValueError('the location label is too long; use a short place name')
        y = top - gap - label_size
        draw.text((x, y), label, font=small, anchor='lt', fill=ivory)
    return canvas


def encode(canvas):
    # Leave room under the mobile thumbnail size limit while keeping full pixel dimensions.
    for quality in range(92, 33, -4):
        buffer = io.BytesIO()
        canvas.save(buffer, 'JPEG', quality=quality, optimize=True, progressive=True)
        if buffer.tell() <= 2_000_000:
            return buffer.getvalue()
    raise ValueError('this frame needs too much JPEG compression; choose a cleaner still')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--still', required=True, type=Path, help='clean episode still for the landscape cover')
    p.add_argument('--portrait-still', type=Path, help='optional separate source for the portrait cover')
    p.add_argument('--hook', required=True, type=english_copy, help='short English headline')
    p.add_argument('--portrait-hook', type=english_copy, help='optional English headline for the narrower layout')
    p.add_argument('--location', type=english_copy, help='optional short location label')
    p.add_argument('--wide-focus', type=focal_point, default=(.72,.48), help='landscape source focus X,Y in [0,1]')
    p.add_argument('--portrait-focus', type=focal_point, default=(.50,.34), help='portrait source focus X,Y in [0,1]')
    p.add_argument('--font', type=Path, help='local bold TTF or OTF file')
    p.add_argument('--output-dir', required=True, type=Path)
    a = p.parse_args()
    face = select_font(a.font)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    designs = [('youtube-16x9.jpg', a.still, a.hook, a.wide_focus, False),
               ('tiktok-3x4.jpg', a.portrait_still or a.still, a.portrait_hook or a.hook, a.portrait_focus, True)]
    with tempfile.TemporaryDirectory(dir=a.output_dir) as scratch:
        for name, source, title, focus, portrait in designs:
            if (a.output_dir / name).exists():
                raise ValueError(f'output already exists: {name}')
            photo = compose(source, title, a.location, face, focus, portrait)
            (Path(scratch) / name).write_bytes(encode(photo))
        published = []
        try:
            for name, *_ in designs:
                target = a.output_dir / name
                os.link(Path(scratch) / name, target)
                published.append(target)
        except OSError:
            for path in published:
                path.unlink()
            raise
    for path in published:
        print(path)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
