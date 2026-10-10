"""home-icon, steps 2 and 3: an image model redraws each draft beside the site's real icons, then the redraw comes back
to a 48x48 icon in the frame palette. Run:
    uv run python assets/home-icon/polish.py grid <draft>       # writes the 3x2 sheet the model edits (.scratch)
    uv run python assets/home-icon/polish.py snap <fal.png> <name>   # the redraw's draft cell -> out/<name>_recolor.png

The sheet is five real recoloured icons (computer, cd_audio, globe_map, blog, recipes) and the draft, each at 8x on
the sidebar's mint, so the model sees the set's pixel grid, outlines, checker shading and palette and copies them. The
snap reads each 8x8 cell of the draft's slot (the median of its middle), maps it to the nearest frame colour, clears
the mint, and redraws the outline the set uses (plum on the lit top/left, black on the bottom/right).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from pc98 import palette as P
from pc98.config import ROOT, SITE

HERE = Path(__file__).parent
SCR = ROOT / '.scratch' / 'home-icon'
REFS = ['computer', 'cd_audio', 'globe_map', 'blog', 'recipes']
CELL, S = 384, 8
MINT = (0x00, 0xEE, 0xBB)
LEG = P.get('site+')


def cell(im):
    """An icon on a mint 384px cell, 8x nearest, centred."""
    c = Image.new('RGB', (CELL, CELL), MINT)
    big = im.convert('RGBA').resize((im.width * S, im.height * S), Image.NEAREST)
    c.paste(big, ((CELL - big.width) // 2, (CELL - big.height) // 2), big)
    return c


def grid(draft):
    ims = [Image.open(SITE / f'img/icons/{n}_recolor.png') for n in REFS] + [Image.open(HERE / 'out/draft' / f'{draft}.png')]
    sheet = Image.new('RGB', (CELL * 3, CELL * 2), MINT)
    for i, im in enumerate(ims):
        sheet.paste(cell(im), ((i % 3) * CELL, (i // 3) * CELL))
    SCR.mkdir(parents=True, exist_ok=True)
    out = SCR / f'grid_{draft}.png'
    sheet.save(out)
    return out


def largest(m):
    """The largest 4-connected part of a mask."""
    lab = np.zeros(m.shape, int)
    best, best_n, k = 0, 0, 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        k += 1
        st, n = [(y0, x0)], 0
        lab[y0, x0] = k
        while st:
            y, x = st.pop()
            n += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = k
                    st.append((yy, xx))
        if n > best_n:
            best, best_n = k, n
    return lab == best


def sample(im, x0, y0, px):
    """48x48 frame letters: each cell's middle, its median colour, the nearest frame colour ('.' for the mint)."""
    keys = [k for k in LEG if k != '.']
    pal = np.array([LEG[k][:3] for k in keys], float)
    g = np.full((48, 48), '.', dtype='<U1')
    H, W = im.shape[:2]
    for j in range(48):
        for i in range(48):
            ya, yb = int(y0 + (j + 0.3) * px), int(y0 + (j + 0.7) * px) + 1
            xa, xb = int(x0 + (i + 0.3) * px), int(x0 + (i + 0.7) * px) + 1
            if ya < 0 or xa < 0 or yb > H or xb > W:
                continue
            c = np.median(im[ya:yb, xa:xb].reshape(-1, 3), 0)
            k = keys[int(np.argmin(((pal - c) ** 2).sum(1)))]
            g[j, i] = '.' if k == 'm' else k
    return g


def snap(src, name, fit=False):
    """fit: size the object to the icon (its widest side to 46px, standing on the bottom row) rather than keep the
    slot's own scale, for an object the model drew smaller than its neighbours."""
    im = np.asarray(Image.open(src).convert('RGB')).astype(float)
    H, W = im.shape[:2]
    cw, ch = W / 3, H / 2                                  # the draft's slot: bottom right
    x0, y0, px = 2 * cw, ch, cw / 48
    g = sample(im, x0, y0, px)
    if fit:
        ys, xs = np.nonzero(largest(g != '.'))
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        f = 46 / max(bw, bh)
        npx = px / f
        x0 = x0 + xs.min() * px - (48 - bw * f) / 2 * npx
        y0 = y0 + (ys.max() + 1) * px - 47 * npx
        g = sample(im, x0, y0, npx)
        g[~largest(g != '.')] = '.'
    # the set's outline round the silhouette: plum where the light comes from (top/left), black where it doesn't
    solid = g != '.'
    pad = np.pad(solid, 1)
    up, down = pad[:-2, 1:-1], pad[2:, 1:-1]
    left, right = pad[1:-1, :-2], pad[1:-1, 2:]
    edge = solid & ~(up & left & down & right)
    g[edge & (~down | ~right)] = 'K'
    g[edge & down & right & (~up | ~left)] = 'u'
    out = np.zeros((48, 48, 4), np.uint8)
    for k in LEG:
        if k != '.':
            out[g == k] = (*LEG[k][:3], 255)
    dst = HERE / 'out' / f'{name}_recolor.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out, 'RGBA').save(dst)
    return dst


if __name__ == '__main__':
    if sys.argv[1] == 'grid':
        print(grid(sys.argv[2]))
    else:
        print(snap(sys.argv[2], sys.argv[3], fit='--fit' in sys.argv))
