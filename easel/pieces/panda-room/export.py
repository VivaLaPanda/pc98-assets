"""Export the finished Panda's Room for the site (vivalapanda.moe/room.html) from the panda-room piece.

Writes easel/pieces/panda-room/out/site/ (gitignored: the room is third-party based):
  room.png            the scene, indexed, 16 inks, native 500x357 (the page shows it at 740x528)
  room@4x.png         nearest-neighbour 4x: the page scales it down smoothly (sharp bilinear)
  masks/<obj>.png     where each object is, exclusive (front objects win), white on transparent
  lit/<obj>@4x.png    each object's hover state, cropped to its lit rect: one step up its own ramp inside (line art
                      stays), a 1px rim of the glow outside it (never over an object in front of it)
  hotspots.json       per object: rank, account, polygon (outer contour, simplified), anchor, lit rect, padded hit
                      area for the tiny ones; all in native pixels (out/hotspots-740x528.json: the polygons at the
                      page's 740x528, beside the site folder, not in it)
  twinkle@4x.png/.json  the city's lights as an 8-frame strip, palette-cycling style: only the lights that change
                      are opaque
  review/lit_states.png  every object at rest and lit, 3x

Run: uv run python easel/pieces/panda-room/export.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'src'))
import easel  # noqa: E402

OUT = Path(__file__).parent / 'out' / 'site'
SCALE = 4

# front to back: where two objects overlap, the earlier one owns the pixels
# (the tapes stand in front of the TV's board; the duck sits on the desk in front of the monitor's foot; the newspaper
# lies on the bed by the tome and the phone, overlapping neither; the map is on the wall above the rail, behind nothing)
ORDER = ['controller', 'kitsu', 'tv', 'butterfly', 'linkedin', 'letter', 'stackoverflow', 'phone', 'lesswrong', 'plush',
         'pc', 'newspaper', 'bookshelf', 'poster', 'bump', 'window']
INFO = {'window': (1, 'Twitter'), 'phone': (2, 'Signal / Discord'), 'pc': (3, 'GitHub'), 'newspaper': (4, 'Substack'),
        'bookshelf': (5, 'Reading list'), 'butterfly': (6, 'Bluesky'), 'tv': (7, 'Letterboxd'),
        'letter': (8, 'Email'), 'controller': (9, 'Steam'), 'lesswrong': (10, 'LessWrong'),
        'linkedin': (11, 'LinkedIn'), 'kitsu': (12, 'Kitsu'), 'stackoverflow': (13, 'Stack Overflow'),
        'bump': (14, 'Bump'), 'plush': (15, 'none (a knick-knack)'), 'poster': (16, 'none (a knick-knack)')}
PAD_HIT = {'butterfly': 3, 'stackoverflow': 3}   # small objects get a padded hit area (round 4: the phone, with its
# pool, and the letter outgrew theirs; round 5: the butterfly is the duck's size again)
HULL_HIT = {'controller': 2}                          # parts spread apart (console, cord, pad): their padded hull
SITS_ON = {'butterfly': 'window'}   # resting on another object: its pad may reach over that one (the page's z-order
# gives the overlap to the front one)


def grow(m, n=1):
    g = m.copy()
    for _ in range(n):
        h = g.copy()
        h[1:] |= g[:-1]; h[:-1] |= g[1:]; h[:, 1:] |= g[:, :-1]; h[:, :-1] |= g[:, 1:]
        g = h
    return g


def shrink(m, n=1):
    return ~grow(~m, n)


# ---- contours (as the first exporter, assets/panda-room/export.py): boundary walk + Douglas-Peucker ----------------

def components(m):
    lab = np.zeros(m.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        stack = [(y, x)]
        lab[y, x] = n
        while stack:
            cy, cx = stack.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    stack.append((ny, nx))
    return [lab == i for i in range(1, n + 1)]


def trace(m):
    """Outer boundary of one component as pixel-corner coordinates, walked clockwise."""
    ys, xs = np.nonzero(m)
    y0 = ys.min(); x0 = xs[ys == y0].min()
    pad = np.pad(m, 1)
    start = (x0, y0)
    pos, d = start, (1, 0)
    pts = [start]
    filled = lambda x, y: pad[y + 1, x + 1]
    dirs = {(1, 0): ((0, -1), (0, 0)), (0, 1): ((0, 0), (-1, 0)), (-1, 0): ((-1, 0), (-1, -1)), (0, -1): ((-1, -1), (0, -1))}
    for _ in range(4 * m.size):
        x, y = pos
        moved = False
        for nd in [(-d[1], d[0]), d, (d[1], -d[0]), (-d[0], -d[1])]:
            left, right = dirs[nd]
            if filled(x + right[0], y + right[1]) and not filled(x + left[0], y + left[1]):
                pos = (x + nd[0], y + nd[1]); d = nd; moved = True
                break
        if not moved or pos == start:
            break
        pts.append(pos)
    return pts


def simplify(pts, eps=1.2):
    pts = np.array(pts, float)
    if len(pts) < 4:
        return pts.astype(int).tolist()

    def rdp(a, b):
        if b <= a + 1:
            return [a]
        p0, p1 = pts[a], pts[b]
        seg = p1 - p0
        L = np.hypot(*seg) or 1e-9
        rel = pts[a + 1:b] - p0
        dd = np.abs(seg[0] * rel[:, 1] - seg[1] * rel[:, 0]) / L
        i = int(np.argmax(dd))
        if dd[i] > eps:
            return rdp(a, a + 1 + i) + rdp(a + 1 + i, b)
        return [a]
    idx = rdp(0, len(pts) - 1) + [len(pts) - 1]
    return [[int(round(x)), int(round(y))] for x, y in pts[idx]]


# ---- images ------------------------------------------------------------------------------------------------------------

def rgba(cv, idx, mask):
    out = np.zeros(idx.shape + (4,), np.uint8)
    pal = (cv.pal.astype(int) * 17).astype(np.uint8)
    out[mask, :3] = pal[idx[mask]]
    out[mask, 3] = 255
    return Image.fromarray(out, 'RGBA')


def x4(im):
    return im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)


def hull(pts):
    """Convex hull (monotone chain) of integer points, clockwise in screen coordinates."""
    pts = sorted(set(map(tuple, pts)))
    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(p)
        return out
    lo, hi = half(pts), half(pts[::-1])
    return [list(p) for p in lo[:-1] + hi[:-1]]


def twinkle(cv, idx, front, frames=8):
    """A sixth of the city's small lights wink (a step dimmer for a frame or two, each on its own phase); isolated red
    beacons blink. Only the pixels that change are opaque."""
    ns = cv.ns
    K = {n: ns[n.upper()] for n in ('white', 'screen', 'glow', 'paper', 'curtain', 'slate', 'floor', 'red', 'dark')}
    DIM = {K['white']: K['glow'], K['screen']: K['glow'], K['glow']: K['floor'], K['paper']: K['curtain'],
           K['curtain']: K['slate']}
    T = ns['TOP']
    glass = np.zeros(idx.shape, bool)
    glass[T + 30:T + 173, 191:284] = True          # the door's panes: sky and city, down to the balusters' feet (the
    glass &= ~grow(front, 1)                       # moonlit deck below, the backlit curtain edges and the moon stay
    glass &= ~grow(ns['MOON_DISK'], 6)             # still: they carry the same inks as the lights)
    lights = []
    for c in components(glass & np.isin(idx, list(DIM))):
        ys, xs = np.nonzero(c)
        if c.sum() <= 8 and np.ptp(xs) <= 3 and np.ptp(ys) <= 4:
            lights.append(c)
    beacons = [c for c in components(glass & (idx == K['red'])) if c.sum() <= 2]
    rng = np.random.default_rng(11)
    pick = rng.choice(len(lights), size=max(1, len(lights) // 6), replace=False)
    phases = rng.integers(0, frames, size=len(pick))
    lens = rng.integers(1, 3, size=len(pick))
    allm = np.zeros(idx.shape, bool)
    for i in pick:
        allm |= lights[i]
    for b in beacons:
        allm |= b
    ys, xs = np.nonzero(allm)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    w, h = x1 - x0 + 1, y1 - y0 + 1
    strip = Image.new('RGBA', (w * frames, h), (0, 0, 0, 0))
    for f in range(frames):
        fr = idx.copy()
        show = np.zeros(idx.shape, bool)
        for j, i in enumerate(pick):
            if (f - phases[j]) % frames < lens[j]:
                m = lights[i]
                fr[m] = np.vectorize(lambda v: DIM.get(v, v))(idx[m])
                show |= m
        for b in beacons:
            if (f // 2) % 2 == 1:
                fr[b] = K['dark']
                show |= b
        im = rgba(cv, fr, show).crop((x0, y0, x1 + 1, y1 + 1))
        strip.paste(im, (w * f, 0))
    x4(strip).save(OUT / 'twinkle@4x.png')
    spec = {'x': int(x0), 'y': int(y0), 'w': int(w), 'h': int(h), 'frames': frames, 'fps': 2,
            'twinkling_lights': int(len(pick)), 'of_lights': len(lights), 'blinking_beacons': len(beacons)}
    (OUT / 'twinkle.json').write_text(json.dumps(spec, indent=1))
    return spec


def main():
    cv, _ = easel.run('panda-room')
    ns = cv.ns
    idx = cv.idx.copy()
    H, W = idx.shape
    for d in ('masks', 'lit', 'review'):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    # the scene: indexed, all 16 registers
    im = Image.fromarray(idx, 'P')
    im.putpalette([int(c) * 17 for c in cv.pal.flatten()])
    im.save(OUT / 'room.png')
    x4(im).save(OUT / 'room@4x.png')

    LIT = ns['LIT']
    up = np.arange(256, dtype=np.uint8)
    for a, b in LIT.items():
        up[a] = b
    lit_all = up[idx]
    RIM = ns['GLOW']

    taken = np.zeros((H, W), bool)
    masks, hs = {}, {}
    for name in ORDER:
        m = cv.masks[name] & ~taken
        masks[name] = m
        out = np.zeros((H, W, 4), np.uint8); out[m] = 255
        Image.fromarray(out, 'RGBA').save(OUT / 'masks' / f'{name}.png')
        rim = grow(m) & ~m & ~taken
        taken |= m
        la = np.where(m, lit_all, idx)
        la = np.where(rim, RIM, la)
        ys, xs = np.nonzero(m | rim)
        bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        x4(rgba(cv, la, m | rim).crop((bx0, by0, bx1, by1))).save(OUT / 'lit' / f'{name}@4x.png')
        hs[name] = {'lit': {'x': int(bx0), 'y': int(by0), 'w': int(bx1 - bx0), 'h': int(by1 - by0)}}
    # polygons and hit areas, once every object's pixels are known. Round 4: each is kept off every other object's
    # pixels (a 1px margin), so no hit area overlaps another object's: the outline is the mask closed by 2px (an
    # object's parts make one shape) but never across a neighbour; a tiny object's pad and the console's hull are cut
    # the same way. (An object sitting on another, the butterfly on the curtain, is a hole in the window's outline:
    # the page's z-order gives it to the butterfly.)
    for name in ORDER:
        m = masks[name]
        others = np.zeros((H, W), bool)
        for o in ORDER:
            if o != name and SITS_ON.get(name) != o:
                others |= masks[o]
        fence = grow(others, 1)
        closed = (shrink(grow(m, 2), 2) & ~fence) | m
        comp = max(components(closed), key=lambda c: c.sum())
        poly = simplify(trace(comp), eps=0.5)
        # anchor: the object's pixel nearest its centroid
        mys, mxs = np.nonzero(m)
        cy, cx = mys.mean(), mxs.mean()
        k = int(np.argmin((mys - cy) ** 2 + (mxs - cx) ** 2))
        rec = {'rank': INFO[name][0], 'account': INFO[name][1], 'area': int(m.sum()),
               'bbox': [int(mxs.min()), int(mys.min()), int(mxs.max()), int(mys.max())],
               'polygon': poly, 'anchor': [int(mxs[k]), int(mys[k])], 'lit': hs[name]['lit']}
        region = None
        if name in PAD_HIT:
            region = grow(m, PAD_HIT[name])
        if name in HULL_HIT:
            gy, gx = np.nonzero(grow(m, HULL_HIT[name]))
            hp = hull(np.stack([np.r_[gx, gx + 1, gx, gx + 1], np.r_[gy, gy, gy + 1, gy + 1]], 1).tolist())
            im = Image.new('L', (W, H), 0)
            ImageDraw.Draw(im).polygon([tuple(q) for q in hp], fill=1)
            region = np.array(im, bool)
        if region is not None:
            region = (region & ~fence) | m
            comp = max(components(region), key=lambda c: c.sum())
            rec['hit'] = simplify(trace(comp), eps=0.5)
        hs[name] = rec
    spec = twinkle(cv, idx, masks['butterfly'] | masks['linkedin'])
    meta = {'scene': 'room.png', 'native_size': [W, H], 'shown_size': [740, 528], 'scale': SCALE,
            'z_order_front_to_back': ORDER, 'objects': hs, 'twinkle': spec,
            'note': 'native pixel-corner coordinates; lit sprites are cropped @4x to their lit rect'}
    (OUT / 'hotspots.json').write_text(json.dumps(meta, indent=1))
    sx, sy = 740 / W, 528 / H                       # the page's scene window: the same polygons at its own scale
    shown = {k: {'rank': v['rank'], 'account': v['account'],
                 'polygon': [[round(x * sx, 1), round(y * sy, 1)] for x, y in v['polygon']],
                 **({'hit': [[round(x * sx, 1), round(y * sy, 1)] for x, y in v['hit']]} if 'hit' in v else {})}
             for k, v in hs.items()}
    (OUT.parent / 'hotspots-740x528.json').write_text(json.dumps({'shown_size': [740, 528], 'objects': shown}, indent=1))

    # review: every object at rest and lit, 3x
    scene = Image.open(OUT / 'room.png').convert('RGBA')
    tiles = []
    for name in ORDER:
        L = hs[name]['lit']
        sprite = Image.open(OUT / 'lit' / f'{name}@4x.png').resize((L['w'], L['h']), Image.NEAREST)
        comp = scene.copy(); comp.alpha_composite(sprite, (L['x'], L['y']))
        b = (max(0, L['x'] - 8), max(0, L['y'] - 8), min(W, L['x'] + L['w'] + 8), min(H, L['y'] + L['h'] + 8))
        z = max(1, min(4, 240 // max(b[2] - b[0], b[3] - b[1])))
        a1 = scene.crop(b).resize(((b[2] - b[0]) * z, (b[3] - b[1]) * z), Image.NEAREST)
        a2 = comp.crop(b).resize(a1.size, Image.NEAREST)
        t = Image.new('RGB', (a1.width * 2 + 6, a1.height + 16), (20, 20, 20))
        t.paste(a1, (0, 16)); t.paste(a2, (a1.width + 6, 16))
        ImageDraw.Draw(t).text((2, 2), f"{INFO[name][0]} {name}: rest | lit", fill=(255, 200, 120))
        tiles.append(t)
    cw, rh = max(t.width for t in tiles), max(t.height for t in tiles)
    sheet = Image.new('RGB', (cw * 2 + 10, rh * ((len(tiles) + 1) // 2) + 10), (12, 12, 12))
    for i, t in enumerate(tiles):
        sheet.paste(t, (5 + (i % 2) * cw, 5 + (i // 2) * rh))
    sheet.save(OUT / 'review' / 'lit_states.png')
    print(f'room {W}x{H}; objects', {k: v['area'] for k, v in hs.items()})
    print('twinkle', spec)


if __name__ == '__main__':
    main()
