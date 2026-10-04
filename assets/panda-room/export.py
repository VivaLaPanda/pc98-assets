"""Export Panda's Room for the site: paint the scene (paint.py), then write out/final/:

  room.png            the scene, indexed, 16 colours, native 448x320 (the page shows it at 740x528, ~1.65x)
  masks/<obj>.png     where each object is, exclusive (front objects win where they overlap), white on transparent
  lit/<obj>.png       each object's hover state on the full canvas: one step brighter along its own ramps, with a
                      1 px warm rim outside it; transparent everywhere else, so the page just overlays it
  hotspots.json       per object: rank, account, polygons (outer contours from the masks, simplified), bbox
  twinkle.png/.json   the city's palette-cycle as overlay frames: only the lights that change are opaque
  review/             the scene in the real site frame, every lit state, zooms beside real PC-98 crops, lint

Run: uv run python assets/panda-room/export.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import paint as PT
from pc98.pixel import grow

HERE = Path(__file__).parent
OUT = HERE / 'out' / 'final'
W, H = PT.W, PT.H
LEG = PT.LEGEND
ROOT = HERE.parents[1]
SITE = Path.home() / 'git' / 'vivalapanda.moe'

# front to back: where two objects overlap, the earlier one owns the pixels
ORDER = ['plush', 'phone', 'newspaper', 'pc', 'butterfly', 'tv', 'bookshelf', 'window']
INFO = {
    'window': (1, 'Twitter'), 'phone': (2, 'Signal / Discord'), 'pc': (3, 'GitHub'), 'newspaper': (4, 'Substack'),
    'bookshelf': (5, 'Reading list'), 'butterfly': (6, 'Bluesky'), 'tv': (7, 'Letterboxd'), 'plush': (8, 'none (a knick-knack)'),
}
# hover: one step up each ramp (ink lines stay ink)
BRIGHTER = {'K': 'K', 'n': 'N', 'N': 'v', 'v': 'V', 'V': 'l', 'l': 'L', 'L': 'W', 'W': 'W', 'c': 'C', 'C': 'W',
            'r': 'b', 'b': 'o', 'o': 'y', 'y': 'W', 'h': 'L', 'g': 'C'}
RIM = 'y'


def save_indexed(a, path):
    used = [k for k in LEG if (a == k).any()]
    idx = np.zeros(a.shape, np.uint8)
    for i, k in enumerate(used):
        idx[a == k] = i
    im = Image.fromarray(idx, 'P')
    im.putpalette([c for k in used for c in LEG[k]])
    im.save(path)
    return used


def rgba(a, mask=None):
    out = np.zeros((H, W, 4), np.uint8)
    for k, rgb in LEG.items():
        sel = a == k
        if mask is not None:
            sel &= mask
        out[sel] = (*rgb, 255)
    return Image.fromarray(out, 'RGBA')


# ---- contours: Moore-neighbour boundary tracing + Douglas-Peucker, per connected component --------------------------

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
    # walk the edges between filled and empty cells (corner coordinates), starting at the top-left corner of (x0, y0)
    start = (x0, y0)
    pos, d = start, (1, 0)               # heading right along the top edge
    pts = [start]
    filled = lambda x, y: pad[y + 1, x + 1]
    for _ in range(4 * m.size):
        x, y = pos
        # cells around the corner: TL (x-1,y-1), TR (x,y-1), BL (x-1,y), BR (x,y); keep filled on the right
        dirs = {(1, 0): ((0, -1), (0, 0)), (0, 1): ((0, 0), (-1, 0)), (-1, 0): ((-1, 0), (-1, -1)), (0, -1): ((-1, -1), (0, -1))}
        # try turning right, straight, left, back: the shape stays on the right, so this walks the outer edge clockwise
        moved = False
        for nd in [(-d[1], d[0]), d, (d[1], -d[0]), (-d[0], -d[1])]:
            left, right = dirs[nd]
            lc = filled(x + left[0], y + left[1])
            rc = filled(x + right[0], y + right[1])
            if rc and not lc:
                pos = (x + nd[0], y + nd[1])
                d = nd
                moved = True
                break
        if not moved:
            break
        if pos == start:
            break
        pts.append(pos)
    return pts


def simplify(pts, eps=1.2):
    pts = np.array(pts, float)
    if len(pts) < 4:
        return pts.tolist()

    def rdp(a, b):
        if b <= a + 1:
            return [a]
        p0, p1 = pts[a], pts[b]
        seg = p1 - p0
        L = np.hypot(*seg) or 1e-9
        rel = pts[a + 1:b] - p0
        d = np.abs(seg[0] * rel[:, 1] - seg[1] * rel[:, 0]) / L
        i = int(np.argmax(d))
        if d[i] > eps:
            return rdp(a, a + 1 + i) + rdp(a + 1 + i, b)
        return [a]
    idx = rdp(0, len(pts) - 1) + [len(pts) - 1]
    return [[int(round(x)), int(round(y))] for x, y in pts[idx]]


# ---- city twinkle ----------------------------------------------------------------------------------------------------

DIM = {'L': 'l', 'l': 'V', 'y': 'o', 'C': 'c', 'W': 'L', 'o': 'b', 'V': 'v', 'h': 'V'}


def twinkle(a, S, frames=8):
    """Overlay frames for the city: a sixth of the lit windows wink (dim for a frame or two, each on its own phase)
    and the red-pink aircraft lights on the tower tops blink. Only pixels that change are opaque."""
    rng = np.random.default_rng(11)
    glass = S['glass']
    ys, xs = np.nonzero(glass)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    lights = [l for l in S['lights'] if l[4] in DIM]
    pick = rng.choice(len(lights), size=max(1, len(lights) // 6), replace=False)
    phases = rng.integers(0, frames, size=len(pick))
    lens = rng.integers(1, 3, size=len(pick))
    beacons = [(x, y) for y, x in zip(*np.nonzero(glass & (a == 'h'))) if y < 80]
    strip = Image.new('RGBA', ((x1 - x0 + 1) * frames, y1 - y0 + 1), (0, 0, 0, 0))
    for f in range(frames):
        fr = np.zeros((y1 - y0 + 1, x1 - x0 + 1, 4), np.uint8)
        for j, li in enumerate(pick):
            lx, ly, lw, lh, c = lights[li]
            off = (f - phases[j]) % frames < lens[j]
            ink = DIM[c] if off else c
            fr[ly - y0:ly - y0 + lh, lx - x0:lx - x0 + lw] = (*LEG[ink], 255)
        for bx, by in beacons:
            on = (f // 2) % 2 == 0
            fr[by - y0, bx - x0] = (*LEG['h' if on else 'n'], 255)
        strip.paste(Image.fromarray(fr, 'RGBA'), ((x1 - x0 + 1) * f, 0))
    strip.save(OUT / 'twinkle.png')
    spec = {'x': int(x0), 'y': int(y0), 'w': int(x1 - x0 + 1), 'h': int(y1 - y0 + 1), 'frames': frames, 'fps': 2,
            'how': 'overlay twinkle.png on the scene at (x, y) in native pixels and step through its frames '
                   '(CSS: background-position steps(frames)); only the changing lights are opaque. Equivalent to '
                   'PC-98 palette cycling, without needing an indexed canvas.',
            'twinkling_windows': int(len(pick)), 'blinking_beacons': len(beacons)}
    (OUT / 'twinkle.json').write_text(json.dumps(spec, indent=1))
    return spec


# ---- review ----------------------------------------------------------------------------------------------------------

def font(n):
    try:
        return ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', n)
    except OSError:
        return ImageFont.load_default()


def lint(path):
    r = subprocess.run(['uv', 'run', 'python', str(ROOT / 'filter' / 'pc98lint.py'), str(path)],
                       capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip()


def review(scene_png, lit_dir, masks, spec):
    rv = OUT / 'review'
    rv.mkdir(parents=True, exist_ok=True)
    scene = Image.open(scene_png).convert('RGBA')
    # 1. the scene in the real site frame (contact page's scene window, its image overridden)
    shown = OUT / '_shown_740.png'
    scene.convert('RGB').save(shown)
    r = subprocess.run(['uv', 'run', 'pc98', 'preview', str(rv / 'site'), '--page', 'contact.html',
                        '--override', f'img/mail.png={shown}', '--dialog',
                        "Oh, you made it! Come in, mind the cables."], capture_output=True, text=True, cwd=ROOT)
    print(r.stdout[-400:], r.stderr[-400:])
    # 2. every lit state, as the hover would show it (2x crops around each object)
    tiles = []
    for name in ORDER:
        lit = Image.open(lit_dir / f'{name}.png')
        comp = scene.copy(); comp.alpha_composite(lit)
        ys, xs = np.nonzero(masks[name])
        bx0, by0 = max(0, xs.min() - 10), max(0, ys.min() - 10)
        bx1, by1 = min(W, xs.max() + 11), min(H, ys.max() + 11)
        a = scene.crop((bx0, by0, bx1, by1)); b = comp.crop((bx0, by0, bx1, by1))
        z = max(1, min(3, 220 // max(a.width, a.height)))
        t = Image.new('RGB', (a.width * z * 2 + 6, a.height * z + 18), (24, 24, 24))
        t.paste(a.resize((a.width * z, a.height * z), Image.NEAREST), (0, 18))
        t.paste(b.resize((b.width * z, b.height * z), Image.NEAREST), (a.width * z + 6, 18))
        ImageDraw.Draw(t).text((2, 2), f'{INFO[name][0]} {name} -> {INFO[name][1]}   (rest | hover)', font=font(11),
                                fill=(255, 200, 120))
        tiles.append(t)
    cols = 2
    cw = max(t.width for t in tiles); rh = max(t.height for t in tiles)
    sheet = Image.new('RGB', (cw * cols + 10, rh * ((len(tiles) + 1) // cols) + 10), (16, 16, 16))
    for i, t in enumerate(tiles):
        sheet.paste(t, (5 + (i % cols) * cw, 5 + (i // cols) * rh))
    sheet.save(rv / 'lit_states.png')
    # 3. 3x zooms beside real PC-98 crops: our window and city vs city_overlook, our shelf vs bedroom.png
    pairs = [((20, 30, 120, 110), SITE / 'img/explore/places/city_overlook.png', (0, 0, 100, 80)),
             ((270, 80, 360, 160), SITE / 'img/explore/places/night_musician_bedroom.png', (10, 80, 100, 160)),
             ((300, 196, 380, 262), SITE / 'img/explore/places/bedroom.png', (380, 260, 460, 326))]
    rows = []
    for ours, ref, rbox in pairs:
        a = scene.crop(ours).convert('RGB'); b = Image.open(ref).convert('RGB').crop(rbox)
        z = 3
        t = Image.new('RGB', (a.width * z + b.width * z + 8, max(a.height, b.height) * z + 18), (24, 24, 24))
        t.paste(a.resize((a.width * z, a.height * z), Image.NEAREST), (0, 18))
        t.paste(b.resize((b.width * z, b.height * z), Image.NEAREST), (a.width * z + 8, 18))
        ImageDraw.Draw(t).text((2, 2), f'ours {ours}   |   real PC-98: {ref.name} {rbox}', font=font(11), fill=(160, 200, 255))
        rows.append(t)
    zs = Image.new('RGB', (max(r.width for r in rows) + 10, sum(r.height for r in rows) + 10 * len(rows)), (16, 16, 16))
    y = 5
    for r_ in rows:
        zs.paste(r_, (5, y)); y += r_.height + 10
    zs.save(rv / 'zoom_vs_real.png')
    # 4. lint numbers, ours beside two references
    text = '\n\n'.join(lint(p) for p in [scene_png, SITE / 'img/explore/places/city_overlook.png',
                                         SITE / 'img/explore/places/night_musician_bedroom.png'])
    (rv / 'lint.txt').write_text(text + '\n')
    print(text)
    shown.unlink()


def main():
    g, M, S = PT.paint()
    a = g.a.copy()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'masks').mkdir(exist_ok=True); (OUT / 'lit').mkdir(exist_ok=True)
    used = save_indexed(a, OUT / 'room.png')
    Image.open(OUT / 'room.png').convert('RGB').resize((W * 2, H * 2), Image.NEAREST).save(OUT / 'room@2x.png')
    # exclusive masks, front to back
    taken = np.zeros((H, W), bool)
    masks = {}
    for name in ORDER:
        m = M[name] & ~taken
        masks[name] = m
        taken |= m
        out = np.zeros((H, W, 4), np.uint8); out[m] = (255, 255, 255, 255)
        Image.fromarray(out, 'RGBA').save(OUT / 'masks' / f'{name}.png')
        # lit state: brighter ramp inside, a warm rim just outside (not over objects in front of it)
        lit = np.vectorize(lambda c: BRIGHTER.get(c, c))(a)
        rim = grow(m, 1) & ~m & ~(taken & ~m)
        la = np.where(m, lit, a)
        la = np.where(rim, RIM, la)
        rgba(la, m | rim).save(OUT / 'lit' / f'{name}.png')
    # hotspots
    hs = {}
    for name in ORDER:
        m = masks[name]
        ys, xs = np.nonzero(m)
        polys = [simplify(trace(c)) for c in components(m) if c.sum() >= 12]
        hs[name] = {'rank': INFO[name][0], 'account': INFO[name][1], 'bbox': [int(xs.min()), int(ys.min()),
                    int(xs.max()), int(ys.max())], 'area': int(m.sum()), 'polygons': polys}
    meta = {'scene': 'room.png', 'native_size': [W, H], 'shown_size': [740, 528], 'scale': round(740 / W, 4),
            'z_order_front_to_back': ORDER, 'objects': hs,
            'note': 'polygons are in native pixel-corner coordinates; multiply by scale for the 740x528 window. '
                    'Masks are exclusive, so hit-testing in z order never double-counts.'}
    (OUT / 'hotspots.json').write_text(json.dumps(meta, indent=1))
    spec = twinkle(a, S)
    print('room.png', W, 'x', H, len(used), 'inks; objects', {k: v['area'] for k, v in hs.items()})
    print('twinkle', spec['twinkling_windows'], 'windows,', spec['blinking_beacons'], 'beacons')
    review(OUT / 'room.png', OUT / 'lit', masks, spec)


if __name__ == '__main__':
    main()
