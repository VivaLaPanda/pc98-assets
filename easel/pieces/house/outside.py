"""The city outside both rooms' windows, per time of day: city_overlook (the bedroom's night view) segmented into sky,
skyline buildings, windows, street lights and signs, then re-rendered for each phase."""
import numpy as np
from PIL import Image

import os
SRC = os.path.join(os.environ.get('PC98_SITE', '/home/panda/code/vivalapanda.moe'), 'img/explore/places/city_overlook.png')
W = 336  # left of the overlook's own window frame


def load() -> np.ndarray:
    return np.asarray(Image.open(SRC).convert('RGB'))[:, :W].astype(int)


def classes(a: np.ndarray) -> dict[str, np.ndarray]:
    def is_(hexs: str) -> np.ndarray:
        return (a == [int(hexs[i:i + 2], 16) for i in (0, 2, 4)]).all(-1)
    grey = is_('424242')
    black = is_('000000')
    h, w = grey.shape
    # haze: the grey checker and its black dots; close the checker horizontally and vertically
    g = grey.copy()
    g[:, 1:-1] |= grey[:, :-2] & grey[:, 2:]
    g[1:-1] |= grey[:-2] & grey[2:]
    haze = g | grey
    haze[60:] = False  # the haze band is the skyline's; grey lower down is the overlook's frame and furniture
    # sky: haze, and everything above it in each column until a building starts (black above the haze top is sky)
    sky = haze.copy()
    for x in range(w):
        col = haze[:, x]
        if col.any():
            top = np.argmax(col)
            sky[:top, x] = True
    band_bottom = np.zeros(w, int)
    for x in range(w):
        ys = np.nonzero(haze[:, x])[0]
        band_bottom[x] = ys.max() if len(ys) else 0
    windows = is_('5263bd') | is_('adbdff')
    lamps = is_('ffad00')
    signs = is_('de0042') | is_('52bd73') | is_('106342') | is_('738c9c')
    return {'sky': sky, 'haze': haze, 'windows': windows, 'lamps': lamps, 'signs': signs, 'black': black,
            'band_bottom': band_bottom}


if __name__ == '__main__':
    a = load()
    c = classes(a)
    vis = np.zeros(a.shape, np.uint8)
    vis[c['sky']] = (90, 120, 200)
    vis[~c['sky']] = (30, 30, 30)
    vis[c['windows']] = (220, 220, 255)
    vis[c['lamps']] = (255, 170, 0)
    vis[c['signs']] = (255, 60, 90)
    Image.fromarray(vis).resize((W * 3, 256 * 3), Image.NEAREST).save('/home/panda/.claude/jobs/8fa989b7/tmp/city_classes.png')
    print(c['band_bottom'][::10])


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
CUTS = np.array([0, 2, 4, 8, 12, 14, 16])  # the period's tile levels


def hexrgb(h: str) -> np.ndarray:
    h = h.lstrip('#')
    return np.array([int(c, 16) * 17 for c in h], float) if len(h) == 3 else np.array(
        [int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def tiles(t: np.ndarray, a: np.ndarray, b: np.ndarray, ox: int = 0, oy: int = 0) -> np.ndarray:
    """Banded tile gradient between two inks: t 0 -> a, 1 -> b, in the period's levels (screen-anchored)."""
    h, w = t.shape
    lv = CUTS[np.abs(np.clip(t, 0, 1)[..., None] * 16 - CUTS).argmin(-1)]
    ys, xs = np.mgrid[0:h, 0:w]
    on = BAYER[(ys + oy) % 4, (xs + ox) % 4] < lv
    return np.where(on[..., None], b, a)


# Each phase: sky stops top -> horizon, haze over the plain (far, near), building face (lit, shade), windows
# (unlit, lit), share of windows lit, street lamps on, sign brightness.
PHASES = {
    'noon':      dict(sky=['#69e', '#9be', '#cdf'], plain=['#bcd', '#99a'], face=['#eef', '#aab'], win=['#557', '#ffd'], lit=0.0, lamps=False),
    'morning':   dict(sky=['#7ad', '#ace', '#eed'], plain=['#cce', '#99b'], face=['#ffe', '#99b'], win=['#557', '#ffd'], lit=0.03, lamps=False),
    'afternoon': dict(sky=['#68d', '#9bd', '#dde'], plain=['#bbc', '#998'], face=['#eed', '#a9a'], win=['#556', '#ffd'], lit=0.0, lamps=False),
    'evening':   dict(sky=['#68b', '#a9b', '#fc9'], plain=['#b9a', '#876'], face=['#fdb', '#977'], win=['#545', '#fd8'], lit=0.15, lamps=False),
    'sunset':    dict(sky=['#549', '#b68', '#f96'], plain=['#a67', '#644'], face=['#e97', '#755'], win=['#433', '#fc6'], lit=0.35, lamps=True),
    'dusk':      dict(sky=['#225', '#447', '#a68'], plain=['#335', '#223'], face=['#446', '#224'], win=['#223', '#fd8'], lit=0.7, lamps=True),
    'night':     None,  # the overlook itself
    'dawn':      dict(sky=['#336', '#868', '#eab'], plain=['#867', '#545'], face=['#a89', '#545'], win=['#434', '#fd9'], lit=0.25, lamps=True),
}


def sky_rows(n: int, stops: list[str]) -> np.ndarray:
    """A colour per row: the stops spread top -> bottom."""
    s = [hexrgb(c) for c in stops]
    t = np.linspace(0, 1, n)
    seg = np.minimum((t * (len(s) - 1)).astype(int), len(s) - 2)
    f = t * (len(s) - 1) - seg
    return np.array([s[i] * (1 - ff) + s[i + 1] * ff for i, ff in zip(seg, f)])


def snap(rgb: np.ndarray) -> np.ndarray:
    return (np.round(rgb / 17) * 17).clip(0, 255)


def banded(rows: np.ndarray, w: int) -> np.ndarray:
    """A vertical gradient as PC-98 bands: each row between its two nearest grid colours, tiled."""
    h = len(rows)
    lo = np.floor(rows / 17) * 17
    hi = np.minimum(lo + 17, 255)
    span = np.where(hi > lo, (rows - lo) / np.maximum(hi - lo, 1), 0).mean(-1)
    t = np.repeat(span[:, None], w, 1)
    a = np.repeat(lo[:, None, :], w, 1)
    b = np.repeat(hi[:, None, :], w, 1)
    ys, xs = np.mgrid[0:h, 0:w]
    lv = CUTS[np.abs(t[..., None] * 16 - CUTS).argmin(-1)]
    return np.where((BAYER[ys % 4, xs % 4] < lv)[..., None], b, a)


def render(phase: str, seed: int = 3) -> np.ndarray:
    a = load()
    if PHASES[phase] is None:
        return a.astype(np.uint8)
    p = PHASES[phase]
    c = classes(a)
    h, w = a.shape[:2]
    out = np.zeros((h, w, 3), float)
    horizon = int(np.median(c['band_bottom'][c['band_bottom'] < 120])) if (c['band_bottom'] < 120).any() else 40
    sky = banded(sky_rows(horizon + 8, p['sky']), w)
    out[:horizon + 8] = sky
    sky_m = c['sky'].copy()
    sky_m[horizon + 8:] = False
    # the plain: haze bands, far (light) at the horizon to near (darker) at the bottom
    plain = banded(sky_rows(h, [p['plain'][0], p['plain'][0], p['plain'][1]]), w)
    out[~sky_m] = plain[~sky_m]
    out[sky_m] = np.vstack([sky, np.zeros((h - len(sky), w, 3))])[sky_m]
    # skyline buildings (the band, not sky): faces, a shade side on every other run
    band = ~sky_m & (np.arange(h)[:, None] <= c['band_bottom'][None, :] + 2)
    face = np.where(np.arange(w)[None, :] % 7 < 5, 0, 1)
    out[band & (face == 0)] = hexrgb(p['face'][0])
    out[band & (face == 1)] = hexrgb(p['face'][1])
    # the low city by day: each cluster of the night's windows is a building; drawn as a clean block (its cluster's
    # bounding box): a lit face, a shade side (the right third), a lighter roofline, its windows as darker panes
    win0 = c['windows'] & ~band & ~sky_m
    grown = win0.copy()
    for _ in range(2):
        g = grown.copy()
        g[1:] |= grown[:-1]; g[:-1] |= grown[1:]; g[:, 1:] |= grown[:, :-1]; g[:, :-1] |= grown[:, 1:]
        grown = g
    lab = np.zeros(grown.shape, int)
    nlab = 0
    for y0, x0 in zip(*np.nonzero(grown)):
        if lab[y0, x0]:
            continue
        nlab += 1
        st = [(y0, x0)]; lab[y0, x0] = nlab
        while st:
            cy, cx = st.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and grown[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = nlab; st.append((ny, nx))
    face_lit, face_sh = hexrgb(p['face'][0]), hexrgb(p['face'][1])
    haze_far = hexrgb(p['plain'][0])
    for k in range(1, nlab + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < 6:
            continue
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        depth = np.clip((y0 - horizon) / max(h - horizon, 1), 0, 1)       # far (0) .. near (1): haze fades far ones
        lit_c = face_lit * (0.55 + 0.45 * depth) + haze_far * (0.45 - 0.45 * depth)
        sh_c = face_sh * (0.55 + 0.45 * depth) + haze_far * (0.45 - 0.45 * depth)
        split = x0 + int((x1 - x0 + 1) * 0.68)
        out[y0:y1 + 1, x0:split] = lit_c
        out[y0:y1 + 1, split:x1 + 1] = sh_c
        out[y0, x0:x1 + 1] = np.minimum(lit_c + 34, 255)                 # the roofline
    # streets by day: the night's lamp trails as a darker line in the haze
    if not p['lamps']:
        out[c['lamps'] & (lab == 0)] = hexrgb(p['plain'][1])
    # clouds by day: a few flat PC-98 clouds (white tops, lavender undersides) in the sky above the skyline
    if p['lit'] < 0.3:
        rng_c = np.random.default_rng(seed + 11)
        yy_, xx_ = np.mgrid[0:h, 0:w]
        for _ in range(5):
            cx_, cy_ = rng_c.uniform(0, w), rng_c.uniform(2, max(horizon - 14, 4))
            for j in range(4):
                bx, by = cx_ + rng_c.uniform(-14, 14), cy_ + rng_c.uniform(-2, 2)
                rx, ry = rng_c.uniform(6, 14), rng_c.uniform(2.5, 4.5)
                blob = ((xx_ - bx) / rx) ** 2 + ((yy_ - by) / ry) ** 2 < 1
                blob &= sky_m
                out[blob] = hexrgb(p['sky'][2]) * 0.3 + np.array([255, 255, 255]) * 0.7
                under = blob & (yy_ > by + ry * 0.35)
                out[under] = hexrgb(p['sky'][1]) * 0.5 + np.array([230, 225, 250]) * 0.5
    # windows: dark panes by day, some lit as it gets dark
    rng = np.random.default_rng(seed)
    win = c['windows']
    lit = win & (rng.random(win.shape) < p['lit'])
    out[win & ~lit] = hexrgb(p['win'][0])
    out[lit] = hexrgb(p['win'][1])
    if p['lamps']:
        out[c['lamps']] = a[c['lamps']]
    sg = c['signs'] & ~sky_m
    out[sg] = a[sg] * (0.6 if not p['lamps'] else 1.0) + (out[sg] * 0.4 if not p['lamps'] else 0)
    return snap(out).astype(np.uint8)


def sky_above(phase: str, n: int, w: int) -> np.ndarray:
    """n rows of sky to stack above the overlook's top row (the view through a tall window)."""
    if PHASES[phase] is None:
        top = ['#000', '#001', '#112']
    else:
        top = [PHASES[phase]['sky'][0]] * 2 + [PHASES[phase]['sky'][0]]
    return snap(banded(sky_rows(n, top), w)).astype(np.uint8)


def sheet() -> None:
    order = ['night', 'dawn', 'morning', 'noon', 'afternoon', 'evening', 'sunset', 'dusk']
    tiles_ = [Image.fromarray(render(p)[0:150]) for p in order]
    w, h = tiles_[0].size
    s = Image.new('RGB', (w * 2, h * 4))
    for i, t in enumerate(tiles_):
        s.paste(t, ((i % 2) * w, (i // 2) * h))
    s.resize((s.width * 2, s.height * 2), Image.NEAREST).save(os.path.join(os.environ.get('SHEET_DIR', '/tmp'), 'city_phases.png'))
