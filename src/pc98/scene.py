"""Scenes and frame art: pc98ify (a reference -> a 16-colour, ordered-dithered picture at true resolution) and compose
(sprites pasted into a site image, e.g. new objects in the frame's striped panels).

pc98ify is the first pass, not the picture. What makes PC-98 art is what comes after: clean dark lines along forms,
flat areas where the original has noise, dither patterns chosen per material (sky, skin, metal), highlights placed by
hand. Load the result as a Grid (Grid.from_image(png, legend_json)) and paint over it in code, the way
assets/blog-icon/draw.py paints icons.

Sizes, measured on the site (Oct 2026):
- the frame (img/background-frame*.png) is a 640x400 PC-98 screen shown at 2x; sprites in it are drawn at 640x400;
- explore scenes (img/explore/places/) are 416x224 to 640x400 originals, drawn into the 740x528 main window with
  background-size: cover, i.e. smooth-scaled ~1.2-1.8x. 480x340 (about 740x528 / 1.55) keeps a new scene's pixels
  close to the old scenes'. Check every scene in place with `pc98 preview --page ... --override ...`.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import palette as P
from .pixel import Grid


def fit(img, size, mode='cover'):
    """Resize to (w, h): 'cover' crops to fill, 'contain' letterboxes, 'stretch' ignores aspect. Uses Lanczos: this is
    the reference being prepared, not the art."""
    w, h = size
    if mode == 'stretch':
        return img.resize((w, h), Image.LANCZOS)
    k = (max if mode == 'cover' else min)(w / img.width, h / img.height)
    im = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), Image.LANCZOS)
    if mode == 'cover':
        x, y = (im.width - w) // 2, (im.height - h) // 2
        return im.crop((x, y, x + w, y + h))
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return out


def auto_spread(legend):
    """Ordered-dither strength from the palette: about half the median distance between neighbouring colours."""
    pal = np.array(list(P.get(legend).values()), dtype=float)
    if len(pal) < 2:
        return 32.0
    d = np.sqrt(((pal[:, None] - pal[None]) ** 2).sum(-1))
    d[d == 0] = np.inf
    return float(np.median(d.min(1)) * 0.5)


def pc98ify(src, out, size=None, colors=16, palette=None, dither='bayer4', spread=None, keep=None, mode='cover'):
    """Returns (Grid, legend). Writes out (indexed PNG), out.json (the legend) and out@2x.png (as shown on a 2x frame)."""
    img = Image.open(src).convert('RGBA')
    if size:
        img = fit(img, size, mode)
    legend = P.get(palette) if palette else P.pick16(img, colors, keep=keep)
    spread = auto_spread(legend) if spread is None and dither else spread
    g = Grid(1, 1)
    g.a = P.quantize(img, legend, dither=dither, spread=spread or 0)
    out = Path(out)
    used = {k: legend[k] for k in g.colors()}
    g.save(out, used, mode='P')
    Path(str(out.with_suffix('')) + '.json').write_text(json.dumps({k: list(v) for k, v in used.items()}))
    im = g.image(used)
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(str(out.with_suffix('')) + '@2x.png')
    ok, probs = P.is_pc98(used)
    return g, used, ok, probs


def compose(base, out, puts):
    """Paste images onto a base at exact pixel positions (alpha respected, no resampling). puts: [(path, x, y)]."""
    b = Image.open(base).convert('RGBA')
    for path, x, y in puts:
        b.alpha_composite(Image.open(path).convert('RGBA'), (int(x), int(y)))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    b.save(out)
    return out
