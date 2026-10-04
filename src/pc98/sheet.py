"""Contact sheets for judging icons: each one at 1x, at the size the site shows it (72 px wide, smooth-scaled like
Chrome does, since the site doesn't set image-rendering), and enlarged with hard pixels and a faint grid."""
from pathlib import Path

from PIL import Image, ImageDraw

from .config import SIDEBAR_BG, ICON_SHOWN_PX, font


def _on(bg, im, size=None, resample=Image.NEAREST, grid=False):
    im = im.convert('RGBA')
    if size:
        w = size
        h = round(im.height * w / im.width)
        im = im.resize((w, h), resample)
    tile = Image.new('RGBA', im.size, bg + (255,))
    tile.alpha_composite(im)
    if grid:                       # faint pixel grid, drawn on a layer so it darkens rather than replaces
        k = im.width // max(1, grid)
        lines = Image.new('RGBA', tile.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lines)
        for i in range(1, grid):
            d.line([(i * k, 0), (i * k, tile.height)], fill=(0, 0, 0, 28))
        for j in range(1, tile.height // k):
            d.line([(0, j * k), (tile.width, j * k)], fill=(0, 0, 0, 28))
        tile.alpha_composite(lines)
    return tile


def icon_sheet(items, out, title=None, big=6, bg=SIDEBAR_BG, label_bg=(24, 24, 24)):
    """items: [(label, path), ...]. Writes a sheet with three rows: 1x, as shown (72 px smooth), and big x hard."""
    ims = [(lab, Image.open(p)) for lab, p in items]
    colw = max(max(im.width * big, ICON_SHOWN_PX, 120) for _, im in ims) + 16
    rows = [
        ('1x', lambda im: _on(bg, im)),
        (f'as shown ({ICON_SHOWN_PX}px)', lambda im: _on(bg, im, ICON_SHOWN_PX, Image.BILINEAR)),
        (f'{big}x', lambda im: _on(bg, im, im.width * big, Image.NEAREST, grid=im.width)),
    ]
    rendered = [[f(im) for _, im in ims] for _, f in rows]
    rowh = [max(t.height for t in r) + 16 for r in rendered]
    head = 34 if title else 0
    lab_h = 22
    W = 110 + colw * len(ims)
    H = head + lab_h + sum(rowh)
    sheet = Image.new('RGB', (W, H), label_bg)
    d = ImageDraw.Draw(sheet)
    f = font(16)
    if title:
        d.text((10, 8), title, fill=(255, 255, 255), font=f)
    for i, (lab, _) in enumerate(ims):
        d.text((110 + i * colw + 8, head + 2), lab[:16], fill=(0xff, 0xaa, 0xbb), font=f)
    y = head + lab_h
    for (rlab, _), r, h in zip(rows, rendered, rowh):
        d.text((8, y + 8), rlab, fill=(200, 200, 200), font=font(12))
        for i, t in enumerate(r):
            x = 110 + i * colw + 8
            sheet.paste(Image.new('RGB', (colw - 8, h - 8), bg), (x - 4, y + 2))
            sheet.paste(t.convert('RGB'), (x + (colw - 16 - t.width) // 2, y + 6))
        y += h
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def image_sheet(paths, out, w=320, cols=4, labels=True):
    """A plain grid of images (generated references, traces), labelled with file names."""
    ims = [Image.open(p).convert('RGB') for p in paths]
    th = [round(im.height * w / im.width) for im in ims]
    rows = (len(ims) + cols - 1) // cols
    rh = [max(th[r * cols:(r + 1) * cols] or [0]) + (20 if labels else 0) for r in range(rows)]
    sheet = Image.new('RGB', (cols * (w + 8), sum(rh) + 8), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    y = 4
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            if i >= len(ims):
                break
            x = 4 + c * (w + 8)
            sheet.paste(ims[i].resize((w, th[i]), Image.LANCZOS), (x, y))
            if labels:
                d.text((x, y + th[i] + 3), Path(paths[i]).name[:40], fill=(220, 220, 220), font=font(12))
        y += rh[r]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def zoom_grid(src, out, box, z=4, beside=None):
    """A gridded zoom of a region, labelled in native pixel coordinates: lines every 8 px (brighter every 32), numbers
    every 16. For tracing: read a contour's vertices straight off the grid and type them into draw code. `beside`
    puts the same region of a second image (the painting, say) next to it at the same zoom."""
    from PIL import ImageDraw, ImageFont
    x0, y0, x1, y1 = box
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 10)
    except OSError:
        font = ImageFont.load_default()

    def one(path):
        big = Image.open(path).convert('RGB').crop(box)
        big = big.resize((big.width * z, big.height * z), Image.NEAREST)
        d = ImageDraw.Draw(big)
        for X in range((x0 + 7) // 8 * 8, x1, 8):
            x = (X - x0) * z
            d.line([(x, 0), (x, big.height)], fill=(255, 255, 0) if X % 32 == 0 else (100, 100, 0))
            if X % 16 == 0:
                d.text((x + 2, 2), str(X), font=font, fill=(255, 255, 0))
        for Y in range((y0 + 7) // 8 * 8, y1, 8):
            y = (Y - y0) * z
            d.line([(0, y), (big.width, y)], fill=(255, 255, 0) if Y % 32 == 0 else (100, 100, 0))
            if Y % 16 == 0:
                d.text((2, y + 2), str(Y), font=font, fill=(255, 255, 0))
        return big

    a = one(src)
    if beside:
        b = one(beside)
        sheet = Image.new('RGB', (a.width * 2 + 8, a.height), (30, 30, 30))
        sheet.paste(a, (0, 0)); sheet.paste(b, (a.width + 8, 0))
        a = sheet
    a.save(out)
    return out
