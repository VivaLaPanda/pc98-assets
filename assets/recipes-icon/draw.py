"""recipes-icon: the sidebar nav icon for the recipes page (/recipes.html, "Panda's Recipe Book": buttermilk pancakes
and katsudon). Run:
    uv run python assets/recipes-icon/draw.py [candidate...]

Drawn straight in the frame palette (SITE letters), like assets/room-icon/draw2.py and draw3.py (the installed
homefolder2): periwinkle bodies, plum shadow and lit-side outline, black shadow-side outline, white highlights, mauve
half-light, pink / hot pink / yellow / peach / tan / rust accents; light from the top left, one mid tone plus the 50%
checker, three-quarter volume. Judged at 72 px (48 at 1.5x, smooth-scaled) in the sidebar's bottom-left slot, beside
the home folder (a four-row, 60 px sidebar was planned and dropped).

Candidates:
  book      Panda's Recipe Book: a hardback cookbook, pink cloth with a hot-pink spine, a label and a steaming
            donburi on the cover, a ribbon bookmark.
  donburi   a steaming katsudon bowl: periwinkle bowl with a pink band, katsu, egg and scallion on rice, chopsticks
            resting across the rim.
  pancakes  a stack of buttermilk pancakes on a plate, a pat of butter on top, syrup running down the sides.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / 'room-icon'))
from draw2 import shade, TO_VGA, LEG                                       # noqa: E402

from pc98 import palette as P                                              # noqa: E402
from pc98 import sheet as S                                                # noqa: E402
from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow      # noqa: E402
from pc98.config import SITE                                               # noqa: E402

OUT = Path(__file__).parent / 'out'
# the sidebar after the user's reshuffle (2026-10-06): globe | envelope / CD | newspaper / RECIPES | home folder; the
# computer (index) icon is gone. Three rows of two, 72 px.
NEIGHBOURS = ['globe_map', 'envelope_closed', 'cd_audio', 'blog', 'room']
SHOWN = 72


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


# ---------------------------------------------------------------------------------------------------------------
# A small donburi, shared by the book's cover and drawn big for the bowl candidate.
# ---------------------------------------------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------------------------------------------
# A. book: a hardback standing a little toward us, front cover and the fore-edge (pages) on the right, the page
#    block's foot along the bottom; pink cloth, hot-pink spine strip with yellow bands, a white label with type, a
#    steaming donburi, a hot-pink ribbon out of the bottom.
# ---------------------------------------------------------------------------------------------------------------

def book():
    g = Grid(48, 48)
    # back board and page block (behind / right of the cover)
    pages = poly(g, [(36, 5), (42, 9), (42, 45), (36, 42)]) | poly(g, [(6, 42), (36, 42), (42, 45), (12, 45)])
    g.fill(pages, 'W')
    for y in range(11, 44, 3):
        g.fill(line(g, 37, y - 1, 41, y + 1) & pages, 'a')
    g.fill(line(g, 9, 44, 39, 44) & pages, 'a')
    back = poly(g, [(42, 9), (44, 10), (44, 47), (12, 47), (12, 46), (42, 46)])
    g.fill(back, 'h'); g.edge(back, 'K', 'br')
    g.edge(pages, 'K', 'br')
    # front cover
    cover = rect(g, 4, 2, 37, 42)
    g.fill(cover, 'k')
    g.dither(rect(g, 30, 3, 37, 42), 'k', 'h', pattern='q1')
    g.dither(rect(g, 5, 37, 37, 42), 'k', 'h', pattern='q1')
    spine = rect(g, 4, 2, 9, 42)
    g.fill(spine, 'h'); g.fill(rect(g, 9, 2, 9, 42), 'u')
    g.fill(rect(g, 5, 3, 5, 41), 'k')
    for y in (6, 38):
        g.fill(rect(g, 4, y, 8, y + 1), 'y')
    g.fill(rect(g, 10, 3, 36, 3), 'W'); g.fill(rect(g, 10, 3, 10, 41), 'W')
    shade(g, cover)
    # label with the title as type
    lab = rect(g, 13, 7, 34, 15)
    g.fill(lab, 'W'); g.dither(rect(g, 31, 8, 34, 15), 'W', 'a'); g.edge(lab, 'u', 'tl'); g.edge(lab, 'K', 'br')
    g.fill(rect(g, 15, 9, 19, 10) | rect(g, 21, 9, 26, 10) | rect(g, 28, 9, 31, 10), 'u')
    g.fill(rect(g, 17, 12, 23, 13) | rect(g, 25, 12, 29, 13), 'h')
    # the donburi on the cover, steaming
    inner, _ = bowl(g, 11, 23, 36, 39, 7)
    katsudon(g, inner)
    for x in (17, 23, 29):
        steam(g, x, 21, 5)
    # ribbon bookmark
    rib = poly(g, [(28, 44), (31, 44), (31, 47), (30, 46), (29, 47), (28, 47)])
    g.fill(rib, 'y'); g.edge(rib, 'K', 'r')
    return g


# ---------------------------------------------------------------------------------------------------------------
# B. donburi: the bowl big, seen a little from above so the katsudon shows; chopsticks across the rim; steam.
# ---------------------------------------------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------------------------------------------
# C. pancakes: a plate, a stack of four, butter on top, syrup running down.
# ---------------------------------------------------------------------------------------------------------------

def pancakes():
    g = Grid(48, 48)
    # plate
    plate = ellipse(g, 1, 33, 46, 47)
    g.fill(plate, 'p'); g.fill(ellipse(g, 6, 35, 41, 45), 'W'); g.dither(ellipse(g, 6, 35, 41, 45) & rect(g, 26, 0, 47, 47), 'W', 'a')
    g.dither(plate & ~ellipse(g, 6, 35, 41, 45) & rect(g, 30, 0, 47, 47), 'p', 'u')
    g.edge(plate, 'u', 'tl'); g.edge(plate, 'K', 'br')
    # the stack: a cylinder, x 6..41, top ellipse at y 12..22, four cakes 5 px thick
    cx0, cx1 = 6, 41
    top_y0, top_y1 = 11, 21
    th = 5
    ncakes = 4
    bot_y0, bot_y1 = top_y0 + th * ncakes, top_y1 + th * ncakes
    side = (rect(g, cx0, (top_y0 + top_y1) // 2, cx1, (bot_y0 + bot_y1) // 2) | ellipse(g, cx0, bot_y0, cx1, bot_y1))
    g.fill(side, 'e')
    g.dither(side & rect(g, 30, 0, 47, 47), 'e', 'n')
    g.fill(side & rect(g, 37, 0, 47, 47), 'n')
    for k in range(1, ncakes + 1):
        e = ellipse(g, cx0, top_y0 + th * k, cx1, top_y1 + th * k)
        lower = e & ~ellipse(g, cx0, top_y0 + th * k - 1, cx1, top_y1 + th * k - 1)
        g.fill(lower & side, 'r' if k < ncakes else 'r')
    g.edge(side, 'W', 'l')
    g.edge(side, 'K', 'br')
    # top: golden
    top = ellipse(g, cx0, top_y0, cx1, top_y1)
    g.fill(top, 'n'); g.dither(top & ~ellipse(g, cx0 + 3, top_y0 + 1, cx1 - 3, top_y1 - 1), 'n', 'e')
    g.dither(ellipse(g, cx0 + 4, top_y0 + 2, cx1 - 8, top_y1 - 3), 'n', 'e', pattern='q1')
    g.edge(top, 'e', 'tl'); g.edge(top & rect(g, 0, (top_y0 + top_y1) // 2, 47, 47), 'r', 'b')
    # syrup: a glossy rust pool on top, running down the front in drips
    pool = ellipse(g, 12, 13, 34, 20)
    drips = rect(g, 12, 17, 14, 29) | rect(g, 19, 19, 21, 36) | rect(g, 28, 19, 30, 26) | rect(g, 33, 16, 34, 31)
    syr = (pool | (drips & side))
    g.fill(syr, 'r')
    g.fill(rect(g, 15, 14, 20, 14) | rect(g, 13, 15, 13, 16), 'e')                # gloss
    for x, y in ((13, 22), (20, 25), (29, 21), (33, 20)):
        g[x, y] = 'e'
    for x, y1 in ((12, 29), (19, 36), (28, 26), (33, 31)):
        g.fill(rect(g, x, y1 + 1, x + (2 if x != 33 else 1), y1 + 1) & side, 'r')       # the drip's bead
        g.fill(rect(g, x, 21, x, y1) & side & (g.a == 'r'), 'e')                          # lit left edge
    g.edge(syr & side, 'K', 'r')
    # butter: a pale yellow pat, a little three-quarter cube, white top highlight
    btop = poly(g, [(20, 10), (27, 9), (31, 12), (24, 13)])
    bfront = poly(g, [(20, 10), (24, 13), (24, 16), (20, 13)])
    bside = poly(g, [(24, 13), (31, 12), (31, 15), (24, 16)])
    g.fill(btop, 'W'); g.fill(bfront, 'y'); g.fill(bside, 'y'); g.dither(bside, 'y', 'e')
    g.edge(btop | bfront | bside, 'K', 'br'); g.edge(btop, 'y', 'tl')
    return g


CANDIDATES = {'book': book, 'donburi': donburi, 'pancakes': pancakes}


def export(name, rc):
    used = {k: P.get(LEG)[k] for k in rc.colors()}
    ok, probs = P.is_pc98(used)
    if not ok:
        raise SystemExit(f'{name}: not PC-98: {probs}')
    OUT.mkdir(parents=True, exist_ok=True)
    rc.save(OUT / f'{name}_recolor.png', LEG)
    rc.dump(OUT / f'{name}_recolor.txt')
    rc.recolor(TO_VGA).save(OUT / f'{name}.png', 'vga', mode='P')
    return OUT / f'{name}_recolor.png'


def review(names):
    S.ICON_SHOWN_PX = SHOWN
    site = [(n, SITE / f'img/icons/{n}_recolor.png') for n in NEIGHBOURS]
    return S.icon_sheet(site + [(n, OUT / f'{n}_recolor.png') for n in names], OUT / 'review' / 'sheet_all.png',
                        title=f'recipes icon: candidates beside the sidebar\'s five other icons (as shown = {SHOWN}px)')


if __name__ == '__main__':
    names = sys.argv[1:] or list(CANDIDATES)
    for n in names:
        print('wrote', export(n, CANDIDATES[n]()))
    print('wrote', review(list(CANDIDATES)))
