"""panel-icons: scene icons for the home panel (see brief.md). Run:
    uv run python assets/panel-icons/draw.py [name...]

Drawn straight in SITE letters like assets/recipes-icon/draw.py. Writes out/<name>.png (RGBA, for the light window),
out/<name>_dark.png (outer outline plum, for the dark window), out/<name>.txt (the grid) and out/sheet.png: every icon
at 2x on the panel's light and dark windows, and at 6x.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image


from pc98 import palette as P
from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow, shrink

OUT = Path(__file__).parent / 'out'
LEG = 'site+'
WINDOWS = [(0xff, 0xff, 0xff), (0x22, 0x22, 0x33)]   # the panel's light (morning, day) and dark (evening, night) windows


def shade(g, m, lit='u', dark='K'):
    """The set's outline: plum on the lit top/left, black on the shadow bottom/right (as room-icon/draw2.py)."""
    g.edge(m, lit, 'tl')
    g.edge(m, dark, 'br')


# The Dinnertime bowl: recipes-icon's runner-up donburi, copied from assets/recipes-icon/draw.py.

def steam(g, x, y, h=10):
    """A rising wisp: a 1 px S-curve, white at the bottom thinning to dots at the top."""
    pts = []
    for k in range(h):
        dx = [0, 1, 1, 1, 0, -1, -1, -1][k % 8]
        pts.append((x + dx, y - k))
    for k, (px, py) in enumerate(pts):
        if 0 <= px < g.w and 0 <= py < g.h:
            if k < h * 0.6 or k % 2 == 0:
                g[px, py] = 'W'


def bowl(g, x0, y0, x1, y1, rim_h, band=True):
    """A three-quarter bowl in the box (x0..x1, y0..y1): the rim an ellipse rim_h tall at the top, the body a half
    ellipse below it, a foot ring. Returns (rim_inside_mask, body_mask)."""
    cx = (x0 + x1) / 2
    rim = ellipse(g, x0, y0, x1, y0 + rim_h)
    inner = ellipse(g, x0 + 2, y0 + 1, x1 - 2, y0 + rim_h - 1)
    body = ellipse(g, x0, y0 - (y1 - y0 - rim_h // 2), x1, y1) & rect(g, 0, y0 + rim_h // 2, 47, 47)
    foot = rect(g, int(cx - (x1 - x0) * 0.22), y1 - 1, int(cx + (x1 - x0) * 0.22), y1 + 1)
    g.fill(foot, 'u'); g.edge(foot, 'K', 'br')
    g.fill(body, 'p')
    g.dither(body & rect(g, int(cx + (x1 - x0) * 0.18), 0, 47, 47), 'p', 'u', pattern='q1')
    g.dither(body & rect(g, int(cx + (x1 - x0) * 0.34), 0, 47, 47), 'p', 'u')
    g.fill(body & rect(g, x0, 0, int(x0 + (x1 - x0) * 0.16), 47) & ~rim, 'W') if False else None
    if band:
        bh = max(2, (y1 - y0 - rim_h) // 3)
        by = y0 + rim_h + 1
        b = body & rect(g, 0, by, 47, by + bh - 1) & ~rim
        g.fill(b, 'k'); g.dither(b & rect(g, int(cx + (x1 - x0) * 0.25), 0, 47, 47), 'k', 'h')
    # the bowl's lit flank, top left
    g.edge(body & ~rim, 'W', 'l')
    g.edge(body, 'K', 'br')
    g.fill(rim, 'W'); g.dither(rim & rect(g, int(cx + (x1 - x0) * 0.2), 0, 47, 47), 'W', 'a')
    g.edge(rim, 'u', 'tl'); g.edge(rim & rect(g, 0, y0 + rim_h // 2, 47, 47), 'K', 'b')
    return inner, body


def katsudon(g, inner):
    """Rice, a sliced katsu cutlet laid across, egg between the slices, a few bits of scallion, inside the rim mask."""
    x0, y0, x1, y1 = _bbox(inner)
    w, h = x1 - x0 + 1, y1 - y0 + 1
    g.fill(inner, 'W'); g.dither(inner, 'W', 'a', pattern='q1')            # rice
    egg = ellipse(g, x0 + 1, y0, x1 - 1, y1) & inner
    g.fill(egg, 'y'); g.dither(egg & rect(g, x0 + w * 2 // 3, 0, 47, 47), 'y', 'e', pattern='q1')
    n = 4 if w >= 30 else 3
    span = w - 6
    sw = span // n
    for k in range(n):
        sx = x0 + 3 + k * sw
        sl = rect(g, sx, y0 + 1 + (k % 2), sx + sw - 3, y1 - 1 - ((k + 1) % 2)) & inner
        g.fill(sl, 'n')
        g.fill(sl & rect(g, 0, y0 + 1 + (k % 2), 47, y0 + 1 + (k % 2)), 'e')         # lit top crust
        g.edge(sl, 'r', 'br')
    for k in range(3):
        px, py = x0 + 4 + k * (w // 3), y0 + 1 + (k * 2) % max(1, h - 2)
        if inner[py, px]:
            g[px, py] = 't'


def _bbox(m):
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def donburi():
    g = Grid(48, 48)
    inner, body = bowl(g, 2, 17, 45, 45, 14)
    katsudon(g, inner)
    # chopsticks, hot-pink lacquer with peach tips, resting across the rim from back left to front right
    # two sticks resting on the back of the rim, overhanging both sides: hot-pink lacquer, lit top, shadow under
    for (a, b, c, d) in ((0, 20, 47, 13), (3, 22, 47, 16)):
        st = line(g, a, b, c, d) | line(g, a, b - 1, c, d - 1)
        g.edge(st, 'K', 'b', inside=False)
        g.fill(st, 'h'); g.fill(line(g, a, b - 1, c, d - 1), 'k')
        g.fill(st & rect(g, 0, 0, 5, 47), 'e')                               # unlacquered tips
    for x in (14, 22, 30):
        steam(g, x, 12, 11)
    return g


def flame(g, x, y, h):
    """A candle flame with its tip at (x, y), h tall: peach outside, yellow inside, a white core low down."""
    w = max(3, h // 2)
    outer = ellipse(g, x - w // 2, y + h // 3, x + w // 2, y + h) | poly(g, [(x, y), (x - w // 2, y + h * 2 // 3),
                                                                           (x + w // 2, y + h * 2 // 3)])
    g.fill(outer, 'e')
    inner = shrink(outer, 1) & rect(g, 0, y + 2, 47, 47)
    g.fill(inner, 'y')
    core = shrink(inner, 1) & rect(g, 0, y + h // 2, 47, 47)
    g.fill(core, 'W')
    g.edge(outer, 'h', 'br')
    return outer


def candle():
    g = Grid(48, 48)
    # saucer: a shallow dish, periwinkle, seen from a little above
    dish = ellipse(g, 5, 36, 42, 46)
    g.fill(dish, 'p')
    well = ellipse(g, 10, 37, 37, 43)
    g.fill(well, 'W'); g.dither(well & rect(g, 25, 0, 47, 47), 'W', 'a')
    g.dither(dish & ~well & rect(g, 30, 0, 47, 47), 'p', 'u')
    g.fill(dish & rect(g, 0, 44, 47, 47) & ~well, 'u')
    shade(g, dish)
    g.edge(well, 'u', 'tl')
    # the candle: a white pillar, a mauve half-light down the right, a melted top with a drip
    body = rect(g, 17, 17, 30, 40) | ellipse(g, 17, 37, 30, 42)
    g.fill(body, 'W')
    g.dither(body & rect(g, 25, 0, 47, 47), 'W', 'a')
    g.fill(body & rect(g, 28, 0, 47, 47), 'a')
    top = ellipse(g, 17, 14, 30, 20)
    g.fill(top, 'W'); g.fill(ellipse(g, 19, 15, 28, 19), 'a'); g.fill(ellipse(g, 20, 16, 26, 18), 'W')
    drip = rect(g, 19, 19, 20, 25) | rect(g, 19, 26, 19, 27)
    g.fill(drip, 'W')
    shade(g, body | top)
    g.fill(line(g, 18, 21, 18, 36), 'W')                                     # lit flank
    # wick and flame
    g.fill(rect(g, 23, 12, 23, 16), 'K')
    flame(g, 23, 1, 13)
    # a few glow pixels (the panel is often dark when this shows)
    for px, py in ((16, 4), (31, 5), (14, 10), (33, 11), (18, 0), (29, 0)):
        g[px, py] = 'y'
    return g


def sunrise():
    g = Grid(48, 48)
    horizon = 31
    # rays: short wedges around the half sun
    cx, cy, r = 23.5, horizon, 13
    for k in range(9):
        a = np.pi * (k / 8)
        x0, y0 = cx - np.cos(a) * (r + 3), cy - np.sin(a) * (r + 3)
        x1, y1 = cx - np.cos(a) * (r + 8), cy - np.sin(a) * (r + 8)
        ray = line(g, x0, y0, x1, y1) | line(g, x0 + 1, y0, x1 + 1, y1)
        g.fill(ray & rect(g, 0, 0, 47, horizon - 1), 'y' if k % 2 == 0 else 'e')
    sun = ellipse(g, 10, horizon - r, 37, horizon + r) & rect(g, 0, 0, 47, horizon - 1)
    g.fill(sun, 'y')
    g.dither(sun & ~ellipse(g, 8, horizon - r - 3, 33, horizon + r - 4), 'y', 'e')
    g.fill(ellipse(g, 15, horizon - r + 3, 20, horizon - r + 7) & sun, 'W')   # highlight, top left
    g.edge(sun, 'h', 'tl'); g.edge(sun, 'r', 'r')
    # the sea: periwinkle bands with white glints, darker toward the bottom right
    sea = rect(g, 2, horizon, 45, 44) & ellipse(g, -8, 20, 55, 60)
    g.fill(sea, 'p')
    g.dither(sea & rect(g, 0, 39, 47, 47), 'p', 'u')
    g.dither(sea & rect(g, 30, horizon + 1, 47, 47), 'p', 'u', pattern='q1')
    for (x0, x1, y) in ((12, 35, horizon + 2), (15, 32, horizon + 4), (18, 29, horizon + 6), (20, 27, horizon + 8)):
        g.fill(rect(g, x0, y, x1, y) & sea, 'y' if y < horizon + 5 else 'W')
    g.fill(rect(g, 2, horizon, 45, horizon) & sea, 'W')
    shade(g, sea)
    return g


def door():
    g = Grid(48, 48)
    # the frame: tan wood, with the doorway open onto daylight (mint sky, a strip of yellow ground)
    frame = rect(g, 9, 1, 40, 46)
    g.fill(frame, 'n'); g.dither(rect(g, 36, 2, 40, 46), 'n', 'r')
    way = rect(g, 13, 5, 36, 46)
    g.fill(way, 'W'); g.dither(rect(g, 13, 6, 36, 20), 'W', 'p', pattern='q1')   # pale sky, bluer up high
    g.fill(rect(g, 13, 37, 36, 46), 'y'); g.dither(rect(g, 13, 37, 36, 38), 'W', 'y')
    g.fill(rect(g, 13, 5, 36, 5), 'K')                                        # head jamb shadow
    shade(g, frame)
    g.edge(way, 'r', 'tl')
    # the door swung out toward us on hinges at the left: a trapezoid, its free edge taller (nearer)
    leaf = poly(g, [(13, 5), (27, 1), (27, 47), (13, 46)])
    g.fill(leaf, 'p')
    g.dither(leaf & rect(g, 23, 0, 47, 47), 'p', 'u', pattern='q1')
    for (y0, y1) in ((8, 22), (26, 41)):                                      # two recessed panels
        pan = poly(g, [(16, y0 + 1), (24, y0 - 1), (24, y1), (16, y1 - 0)])
        g.edge(pan, 'u', 'tl'); g.edge(pan, 'W', 'br')
    g.fill(rect(g, 24, 24, 25, 26), 'y'); g[24, 24] = 'W'; g[25, 26] = 'r'   # knob
    shade(g, leaf)
    g.fill(line(g, 14, 6, 14, 45), 'W')                                       # lit hinge edge
    # sunlight on the floor through the doorway
    g.dither(poly(g, [(28, 44), (36, 44), (40, 47), (30, 47)]) & ~frame, 'y', 'W')
    return g


def moon():
    g = Grid(48, 48)
    disc = ellipse(g, 6, 5, 39, 38)
    bite = ellipse(g, 15, 1, 46, 32)
    cres = disc & ~bite
    g.fill(cres, 'y')
    g.dither(cres & ~ellipse(g, 4, 3, 36, 34), 'y', 'e')                    # shadow side, bottom right
    g.fill(cres & ellipse(g, 9, 10, 14, 22), 'W')                             # highlight
    g.edge(cres, 'u', 'tl'); g.edge(cres, 'K', 'br')
    # stars: a big four-point one and two small
    g.patch(31, 15, '''
        ...K...
        ...y...
        ..yWy..
        KyWWWyK
        ..yWy..
        ...y...
        ...K...
    ''')
    g.patch(40, 30, '''
        .y.
        yWy
        .y.
    ''')
    g.patch(25, 41, '''
        .k.
        kWk
        .k.
    ''')
    return g


def futon():
    g = Grid(48, 48)
    # a futon seen from the foot, a little above: the mattress slab, a pillow at the head, the quilt pulled up
    top = poly(g, [(9, 18), (38, 18), (45, 34), (2, 34)])
    front = rect(g, 2, 35, 45, 40)
    g.fill(top, 'W'); g.fill(front, 'a'); g.dither(rect(g, 34, 35, 45, 40), 'a', 'u')
    shade(g, top | front)
    pil = ellipse(g, 14, 15, 33, 24)
    g.fill(pil, 'W'); g.dither(pil & rect(g, 27, 0, 47, 47), 'W', 'a'); shade(g, pil)
    g.fill(line(g, 17, 19, 30, 19), 'a')                                      # the pillow's seam
    # the quilt: periwinkle with the kotatsu's pink plaid, the sheet turned down over its top edge
    quilt = poly(g, [(7, 25), (40, 25), (46, 36), (46, 43), (1, 43), (1, 36)])
    g.fill(quilt, 'p')
    for x0, x1 in ((12, 9), (19, 17), (28, 30), (35, 38)):                     # plaid lines toward the viewer
        g.fill(line(g, x0, 26, x1, 36) & quilt, 'k')
        g.fill(line(g, x1, 37, x1, 42) & quilt, 'k')
    for y in (30, 39):
        g.fill(rect(g, 0, y, 47, y) & quilt, 'k')
    g.fill(g.mask('k') & rect(g, 0, 39, 47, 39) & rect(g, 0, 0, 47, 47), 'k')
    g.dither(quilt & rect(g, 33, 26, 47, 47), 'p', 'u', pattern='q1')
    g.dither(quilt & rect(g, 0, 37, 47, 43), 'p', 'u', pattern='q1')
    sheet_fold = poly(g, [(7, 25), (40, 25), (41, 27), (6, 27)])
    g.fill(sheet_fold, 'W'); g.fill(rect(g, 0, 28, 47, 28) & quilt, 'u')
    g.edge(quilt, 'u', 'tl'); g.edge(quilt, 'K', 'br')
    g.fill(rect(g, 1, 36, 46, 36) & quilt, 'u')                               # the quilt's edge over the slab
    # zzz, periwinkle with a plum shadow so they read on the light and the dark window
    for x, y, z in ((27, 1, '''
        ppppp
        ...p.
        ..p..
        .p...
        ppppp
    '''), (34, 7, '''
        pppp
        ..p.
        .p..
        pppp
    '''), (40, 12, '''
        ppp
        .p.
        ppp
    ''')):
        zg = Grid.parse(z)
        g.paste(zg.recolor({'p': 'u'}), x + 1, y + 1)
        g.paste(zg, x, y)
    return g


def wait():
    g = Grid(48, 48)
    # the Windows hourglass: two caps, two glass bulbs, sand running
    for y0 in (4, 40):
        cap = rect(g, 11, y0, 36, y0 + 3)
        g.fill(cap, 'n'); g.dither(rect(g, 30, y0, 36, y0 + 3), 'n', 'r'); shade(g, cap)
    glass = poly(g, [(14, 8), (33, 8), (33, 11), (25, 23), (25, 24), (33, 36), (33, 39), (14, 39), (14, 36),
                     (22, 24), (22, 23), (14, 11)])
    g.fill(glass, 'W'); g.dither(glass & rect(g, 27, 0, 47, 47), 'W', 'p')
    sand_top = poly(g, [(17, 14), (30, 14), (24, 22), (23, 22)])
    sand_bot = poly(g, [(16, 37), (31, 37), (31, 34), (24, 30), (23, 30), (16, 34)])
    g.fill(sand_top | sand_bot, 'y'); g.dither((sand_top | sand_bot) & rect(g, 26, 0, 47, 47), 'y', 'e')
    g.fill(rect(g, 23, 23, 24, 30), 'y')
    g.edge(glass, 'u', 'tl'); g.edge(glass, 'K', 'br')
    g.fill(line(g, 16, 10, 16, 12) | line(g, 16, 35, 16, 37), 'W')
    return g


def offline():
    g = Grid(48, 48)
    # a wall socket (left) and the plug pulled out of it (right), the cord trailing off
    plate = rect(g, 3, 10, 18, 33)
    g.fill(plate, 'W'); g.dither(rect(g, 14, 11, 18, 33), 'W', 'a'); shade(g, plate)
    for y in (16, 25):
        g.fill(rect(g, 8, y, 9, y + 3) | rect(g, 12, y, 13, y + 3), 'K')
    plug = rect(g, 26, 14, 37, 29)
    g.fill(plug, 'p'); g.dither(rect(g, 33, 15, 37, 29), 'p', 'u'); shade(g, plug)
    g.fill(rect(g, 27, 15, 27, 27), 'W')
    for y in (17, 24):
        prong = rect(g, 20, y, 25, y + 1)
        g.fill(prong, 'y'); g.edge(prong, 'r', 'b')
    cord = polyline(g, [(37, 22), (41, 22), (43, 26), (43, 34), (40, 40), (33, 43), (26, 44)])
    g.fill(grow(cord, 1) & ~plug, 'u'); g.fill(cord & ~plug, 'p')
    # sparks of the broken connection
    g.patch(19, 7, '''
        h..h
        .hh.
    ''')
    g.patch(19, 32, '''
        .hh.
        h..h
    ''')
    return g


def unknown():
    g = Grid(48, 48)
    tile = rect(g, 8, 8, 39, 39)
    g.fill(tile, 'p'); g.dither(rect(g, 33, 9, 39, 39), 'p', 'u'); g.dither(rect(g, 9, 34, 39, 39), 'p', 'u')
    shade(g, tile)
    g.fill(rect(g, 9, 9, 38, 9) | rect(g, 9, 9, 9, 38), 'W')
    q = Grid.parse('''
        ..WWWWWW..
        .WWWWWWWW.
        WWWK..KWWW
        WWK....WWW
        .......WWW
        ......WWWK
        ....WWWWK.
        ....WWWK..
        ....WWK...
        ..........
        ....WWW...
        ....WWWK..
        .....KKK..
    ''')
    g.paste(q, 19, 17)
    return g


ICONS = {f.__name__: f for f in (candle, sunrise, door, moon, futon, wait, offline, unknown)}
ICONS['bowl'] = donburi


def dark(g):
    """For the panel's #222233 window: the outer outline's black turns plum, so shadow-side edges don't dissolve."""
    outer = g.mask('K') & grow(~g.mask(), 1)
    return g.copy().fill(outer, 'u')


def sheet(names):
    """Each icon at 2x on both panel windows (what the panel shows), then at 6x on mint (for drawing)."""
    ims = [Image.open(OUT / f'{n}.png') for n in names]
    pad = 8
    cell2, cell6 = 96 + pad, 288 + pad
    W = pad + len(ims) * max(cell2, cell6)
    H = pad + 2 * cell2 + cell6
    out = Image.new('RGBA', (W, H), (0x80, 0x80, 0x80, 255))
    for i, im in enumerate(ims):
        x = pad + i * max(cell2, cell6)
        for j, bg in enumerate(WINDOWS):
            tile = Image.new('RGBA', (96, 96), (*bg, 255))
            src = im if j == 0 else Image.open(OUT / f'{names[i]}_dark.png')
            tile.alpha_composite(src.resize((96, 96), Image.NEAREST))
            out.paste(tile, (x, pad + j * cell2))
        tile = Image.new('RGBA', (288, 288), (0x00, 0xee, 0xbb, 255))
        tile.alpha_composite(im.resize((288, 288), Image.NEAREST))
        out.paste(tile, (x, pad + 2 * cell2))
    out.save(OUT / 'sheet.png')
    return OUT / 'sheet.png'


if __name__ == '__main__':
    names = sys.argv[1:] or list(ICONS)
    OUT.mkdir(exist_ok=True)
    for n in names:
        g = ICONS[n]()
        used = {k: P.get(LEG)[k] for k in g.colors()}
        ok, probs = P.is_pc98(used)
        if not ok:
            raise SystemExit(f'{n}: {probs}')
        g.save(OUT / f'{n}.png', LEG)
        dark(g).save(OUT / f'{n}_dark.png', LEG)
        g.dump(OUT / f'{n}.txt')
    print('wrote', sheet(list(ICONS)))
