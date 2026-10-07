"""room-icon, round 3: the user on round 2's tucked-in bed (installed): "I feel like the bed evokes sleepytime, not:
- home - directory - bedroom" (2026-10-06). So no bed. The icon has to say Panda's home, a directory of Panda's places,
and Panda's own room. Run:
    uv run python assets/room-icon/draw3.py [candidate...]

Same rules as round 2 (draw2.py): drawn straight in the frame palette (SITE letters), periwinkle bodies, plum shadow
and lit-side outline, black shadow-side outline, white highlights, mauve half-light, pink and hot pink accents, light
from the top left, one mid tone plus the 50% checker.

Candidates:
  homefolder   a Windows 98 folder in the set's colours, papers peeking out, Panda's face on a badge on the front:
               "Panda's home directory", one of the desktop-icon family (My Computer, CD, envelope, globe).
  homefolder2  the same folder with a little house on the badge instead, its window lit (variant).
  door         Panda's bedroom door, nearly closed, warm light round its edge: a panda nameplate and stickers.
  house        a little house at night, one warm window with Panda's silhouette in it, a crescent moon.
  cutaway      a three-quarter cutaway of a tiny room: a moonlit window, a glowing CRT on a desk, Panda on the rug.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from draw2 import shade, panda_head_small, TO_VGA, NEIGHBOURS, LEG          # noqa: E402

from pc98 import palette as P                                              # noqa: E402
from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow      # noqa: E402
from pc98.sheet import icon_sheet                                          # noqa: E402
from pc98.config import SITE                                               # noqa: E402

OUT = Path(__file__).parent / 'out3'
OUT2 = Path(__file__).parent / 'out2'


def star(g, x, y, c='y', hi='W'):
    g.patch(x - 1, y - 1, f'''
        .{c}.
        {c}{hi}{c}
        .{c}.
    ''')


# ---------------------------------------------------------------------------------------------------------------
# 1. homefolder: the Windows 98 closed folder (tab at the back left, the front flap a touch lower and wider), in the
#    set's periwinkle with mauve shade; two sheets peeking out of the top; a round pink badge on the front with Panda.
# ---------------------------------------------------------------------------------------------------------------

def folder_base(g):
    back = rect(g, 3, 10, 41, 40) | poly(g, [(3, 6), (16, 6), (19, 10), (3, 10)])
    g.fill(back, 'p')
    g.dither(back, 'p', 'u', pattern='q1')
    g.dither(rect(g, 30, 7, 41, 40) & back, 'p', 'u')
    g.fill(rect(g, 4, 7, 15, 7), 'W')
    shade(g, back)
    # papers in the folder: white, edges in mauve, slightly fanned
    p1 = poly(g, [(8, 7), (35, 5), (36, 16), (9, 18)])
    p2 = rect(g, 12, 9, 40, 18)
    g.fill(p2, 'W'); g.fill(rect(g, 40, 9, 40, 18), 'a'); g.edge(p2, 'u', 'tl'); g.edge(p2, 'K', 'r')
    for y in (11, 13):
        g.dither(line(g, 15, y, 36, y), 'a', 'W', pattern='v')
    g.fill(p1 & ~p2, 'W'); g.edge(p1 & ~p2, 'u', 'tl')
    g.fill(polyline(g, [(8, 7), (35, 5)]), 'u'); g.fill(line(g, 35, 5, 36, 9), 'K')
    # front flap: periwinkle, lit along its top, darkening to the bottom right
    front = poly(g, [(2, 16), (44, 16), (45, 44), (3, 44)])
    g.fill(front, 'p')
    g.fill(line(g, 3, 17, 43, 17), 'W')
    g.dither(rect(g, 0, 38, 47, 43) & front, 'p', 'a')
    g.dither(rect(g, 38, 18, 47, 43) & front, 'p', 'u', pattern='q1')
    shade(g, front)
    return front


def homefolder():
    g = Grid(48, 48)
    folder_base(g)
    # badge: a round pink plate with Panda's head, a hot-pink rim
    badge = ellipse(g, 13, 21, 34, 42)
    g.fill(badge, 'k'); g.dither(badge & ~ellipse(g, 12, 20, 32, 40), 'k', 'h')
    g.edge(badge, 'W', 'tl'); g.edge(badge, 'h', 'br')
    g.paste(panda_head_small(), 16, 25)
    return g


def homefolder2():
    g = Grid(48, 48)
    folder_base(g)
    # badge: a little house, pink roof, white walls, its window lit, a moon over it
    roof = poly(g, [(23, 20), (36, 30), (10, 30)])
    g.fill(roof, 'h'); g.dither(roof & rect(g, 23, 20, 36, 30), 'h', 'u', pattern='q1')
    g.fill(polyline(g, [(10, 30), (23, 20)]), 'k'); g.edge(roof, 'K', 'br')
    walls = rect(g, 12, 31, 34, 41)
    g.fill(walls, 'W'); g.dither(rect(g, 28, 31, 34, 41), 'W', 'a'); shade(g, walls, 'a', 'K')
    win = rect(g, 13, 32, 23, 40)
    g.fill(win, 'y'); g.edge(win, 'u')
    g.patch(15, 33, '''
        K.....K
        .WWWWW.
        WKKWKKW
        WWWKWWW
        .WWWWW.
    ''')
    door = rect(g, 26, 33, 31, 41)
    g.fill(door, 'u'); g.edge(door, 'K', 'br'); g[30, 37] = 'y'
    ch = rect(g, 30, 22, 32, 27)
    g.fill(ch, 'u'); g.edge(ch, 'K', 'br')
    return g


# ---------------------------------------------------------------------------------------------------------------
# 2. door: Panda's bedroom door, square to us, almost closed: a crack of warm light down the latch side and a wedge
#    of it on the floor. Periwinkle casing and leaf with two panels; a pink nameplate with Panda's face; stickers.
# ---------------------------------------------------------------------------------------------------------------

def door():
    g = Grid(48, 48)
    casing = rect(g, 5, 1, 42, 46)
    g.fill(casing, 'p'); shade(g, casing)
    g.fill(rect(g, 6, 2, 41, 2), 'W'); g.fill(rect(g, 6, 2, 6, 45), 'W')
    g.dither(rect(g, 40, 3, 41, 45), 'p', 'u')
    opening = rect(g, 9, 5, 38, 46)
    g.edge(opening, 'u', 'tl', inside=False)
    # the light beyond, through the crack on the latch side
    g.fill(rect(g, 35, 5, 38, 46), 'y'); g.dither(rect(g, 37, 5, 38, 46), 'y', 'e')
    # the leaf, opened a little inward: its latch edge set back, so a sliver of its thickness shows
    leaf = rect(g, 9, 5, 34, 46)
    g.fill(leaf, 'p')
    g.dither(rect(g, 30, 5, 34, 46), 'p', 'a')
    g.fill(rect(g, 9, 5, 34, 5), 'W'); g.fill(rect(g, 9, 5, 9, 46), 'W')
    g.edge(leaf, 'K', 'r')
    g.fill(line(g, 35, 5, 35, 46), 'u')
    for pnl in (rect(g, 12, 25, 31, 33), rect(g, 12, 36, 31, 44)):
        g.edge(pnl, 'u', 'tl'); g.edge(pnl, 'W', 'br')
    g.fill(rect(g, 30, 27, 31, 29) & ~rect(g, 31, 27, 31, 27), 'y')               # knob, lit
    g[31, 29] = 'n'; g[29, 29] = 'u'
    # nameplate: a pink plaque on a cord, Panda's face on it
    g.fill(polyline(g, [(15, 11), (21, 6), (27, 11)]), 'K')
    g[21, 6] = 'y'
    plate = rect(g, 12, 10, 30, 22)
    g.fill(plate, 'k'); g.dither(rect(g, 12, 19, 30, 22), 'k', 'h', pattern='q1')
    g.edge(plate, 'W', 'tl'); g.edge(plate, 'h', 'br'); g.edge(plate, 'K', 'br', inside=False)
    g.paste(panda_head_small(), 14, 10)
    # stickers: a star, a heart, a crescent
    g.patch(25, 26, '''
        ..y..
        .yyy.
        yyWyy
        .yyy.
        .y.y.
    ''')
    g.patch(13, 37, '''
        .hh.hh.
        hkhhhhh
        hhhhhhh
        .hhhhh.
        ..hhh..
        ...h...
    ''')
    g.patch(24, 37, '''
        .WWW
        WW..
        W...
        WW..
        .WWW
    ''')
    g.edge(rect(g, 24, 37, 27, 41) & (g.a == 'W'), 'a', 'r') if False else None
    # light spilling onto the floor from the crack
    wedge = poly(g, [(35, 46), (38, 46), (47, 47), (36, 47)])
    g.fill(wedge, 'y')
    g.dither(poly(g, [(39, 47), (47, 47), (47, 47)]) | rect(g, 42, 47, 47, 47), 'y', '.', pattern='checker')
    return g


# ---------------------------------------------------------------------------------------------------------------
# 3. house: a little house at night, three-quarter (gable to the front left, the long side receding right), a pink
#    roof, periwinkle walls, one big warm window on the side with Panda's silhouette in it; a crescent moon above.
# ---------------------------------------------------------------------------------------------------------------

def house():
    g = Grid(48, 48)
    # moon, top right, clear of the roof
    moon = ellipse(g, 35, 0, 45, 10) & ~ellipse(g, 32, -2, 42, 8)
    g.fill(moon, 'y'); g.edge(moon, 'W', 'tr')
    star(g, 30, 3)
    # side wall (shadowed periwinkle), receding to the right
    side = poly(g, [(23, 26), (44, 20), (44, 42), (23, 46)])
    g.fill(side, 'p'); g.dither(side, 'p', 'u', pattern='q1')
    g.edge(side, 'K', 'br')
    # front gable (lit)
    front = rect(g, 2, 26, 23, 46) | poly(g, [(2, 26), (12, 15), (23, 26)])
    g.fill(front, 'p'); g.dither(rect(g, 2, 42, 23, 46) & front, 'p', 'a')
    g.edge(front, 'W', 'tl'); g.edge(front, 'K', 'b')
    g.fill(line(g, 23, 26, 23, 46), 'u')
    # roof plane over the side wall, and the bargeboard along the gable
    A, E = (12, 13), (24, 25)
    D = (20, -6)
    A2, E2 = (A[0] + D[0], A[1] + D[1]), (E[0] + D[0], E[1] + D[1])
    roof = poly(g, [A, A2, E2, E])
    g.fill(roof, 'k')
    for k in range(3, 17, 3):
        g.dither(line(g, A[0] + (E[0] - A[0]) * k // 16, A[1] + (E[1] - A[1]) * k // 16,
                      A2[0] + (E2[0] - A2[0]) * k // 16, A2[1] + (E2[1] - A2[1]) * k // 16) & roof, 'h', 'k', pattern='v')
    g.fill(line(g, A[0], A[1], A2[0], A2[1]), 'W')
    g.edge(roof, 'K', 'br')
    barge = polyline(g, [(0, 27), A, E]) | polyline(g, [(1, 27), (A[0], A[1] + 1), (E[0] - 1, E[1])])
    g.fill(barge, 'h'); g.fill(polyline(g, [(0, 27), A]), 'k')
    g.fill(polyline(g, [(1, 28), (A[0], A[1] + 2), (E[0] - 2, E[1])]), 'u')
    # chimney
    ch = rect(g, 33, 4, 36, 11)
    g.fill(ch, 'a'); g.fill(rect(g, 35, 4, 36, 11), 'u'); g.fill(rect(g, 32, 3, 37, 4), 'p'); shade(g, ch | rect(g, 32, 3, 37, 4))
    # the big lit window on the side wall, following its slope, with Panda's silhouette
    win = poly(g, [(27, 28), (40, 25), (40, 38), (27, 41)])
    g.fill(win, 'y'); g.dither(poly(g, [(35, 26), (40, 25), (40, 38), (35, 39)]), 'y', 'e', pattern='q1')
    g.edge(win, 'K')
    g.patch(28, 28, '''
        .KK.....KK.
        KKKWWWWWKKK
        .KWWWWWWWK.
        .WKKWWWKKW.
        .WKKWWWKKW.
        .WWWWKWWWW.
        ..kWKKKWk..
        ...WWWWW...
        .KKKKKKKKK.
        KKKKKKKKKKK
    ''')
    g.edge(win, 'K')
    g.fill(line(g, 27, 34, 40, 31) & ~(g.a == 'K') & win, 'u') if False else None
    # door in the gable, with a lit knob, and a round gable window
    dr = rect(g, 9, 34, 16, 45)
    g.fill(dr, 'h'); g.fill(rect(g, 10, 35, 15, 35), 'k'); g.edge(dr, 'K'); g[15, 40] = 'y'
    gw = ellipse(g, 10, 19, 15, 24)
    g.fill(gw, 'y'); g.edge(gw, 'K'); g[11, 20] = 'W'
    # ground
    g.fill(rect(g, 0, 47, 47, 47) & ~(g.a != '.'), 'u') if False else None
    return g


# ---------------------------------------------------------------------------------------------------------------
# 4. cutaway: a corner of a tiny room, three-quarter: back wall with a moonlit window, the left wall, the floor; a desk
#    with a glowing CRT; a pink rug. The walls' cut edges are white (a dollhouse cut).
# ---------------------------------------------------------------------------------------------------------------

def cutaway():
    g = Grid(48, 48)
    # floor: a rhombus, the walls' feet meeting at the back corner
    floor = poly(g, [(1, 33), (24, 22), (47, 33), (24, 46)])
    g.fill(floor, 'a'); g.dither(floor & rect(g, 0, 38, 47, 47), 'a', 'u', pattern='q1')
    rug = poly(g, [(12, 36), (24, 30), (36, 36), (24, 42)])
    g.fill(rug, 'k'); g.dither(rug & rect(g, 24, 30, 47, 47), 'k', 'h', pattern='q1'); g.edge(rug, 'h')
    # walls: left lit, right in shade
    lw = poly(g, [(1, 9), (24, 0), (24, 22), (1, 33)])
    g.fill(lw, 'p')
    rw = poly(g, [(24, 0), (47, 9), (47, 33), (24, 22)])
    g.fill(rw, 'p'); g.dither(rw, 'p', 'u', pattern='q1')
    # the cut: thick white edges along the tops and ends, black under the floor
    g.fill(polyline(g, [(1, 33), (1, 9), (24, 0), (47, 9), (47, 33)]), 'W')
    g.fill(polyline(g, [(2, 33), (2, 10), (24, 1), (46, 10), (46, 33)]), 'W')
    g.fill(line(g, 24, 1, 24, 22), 'u')
    g.fill(polyline(g, [(1, 33), (24, 46), (47, 33)]), 'K')
    g.fill(polyline(g, [(1, 34), (24, 47), (47, 34)]), 'u')
    # a big night window on the left wall, slanted with it: navy, a moon, the city's lights
    win = poly(g, [(5, 12), (20, 6), (20, 20), (5, 26)])
    g.fill(win, 'b')
    for x, y in ((7, 22), (9, 22), (11, 20), (14, 19), (17, 17), (18, 18), (8, 24)):
        g[x, y] = 'y'
    g.fill(rect(g, 16, 9, 17, 11), 'y'); g[18, 9] = 'y'; g[15, 12] = 'y'
    g[9, 15] = 'W'; g[12, 11] = 'W'
    g.edge(win, 'W'); g.fill(line(g, 12, 9, 12, 23), 'W')
    # moonlight falling on the floor
    g.dither(poly(g, [(6, 32), (17, 27), (22, 29), (11, 35)]) & floor & ~rug, 'a', 'W')
    # a desk on the right wall with a big glowing CRT
    top = poly(g, [(27, 25), (42, 18), (45, 20), (30, 27)])
    g.fill(top, 'n'); g.edge(top, 'r', 'b')
    g.fill(rect(g, 29, 27, 30, 34) | rect(g, 43, 20, 44, 28), 'r')
    crt = poly(g, [(29, 13), (41, 8), (41, 20), (29, 25)])
    g.fill(crt, 'a'); g.edge(crt, 'W', 'tl'); g.edge(crt, 'K', 'br')
    scr = poly(g, [(31, 14), (39, 11), (39, 18), (31, 22)])
    g.fill(scr, 'm'); g.fill(line(g, 32, 16, 37, 14) | line(g, 32, 19, 36, 17), 'W')
    g.dither(grow(crt, 2) & ~crt & rw & ~top, 'p', 'm', pattern='q1')
    # Panda's plush on the rug
    g.paste(panda_head_small(), 14, 26)
    return g


CANDIDATES = {'homefolder': homefolder, 'homefolder2': homefolder2, 'door': door, 'house': house, 'cutaway': cutaway}


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
    site = [(n, SITE / f'img/icons/{n}_recolor.png') for n in NEIGHBOURS]
    return icon_sheet(site + [(n, OUT / f'{n}_recolor.png') for n in names] +
                      [('r2 ajar', OUT2 / 'ajar_recolor.png'), ('now: tuckedin', SITE / 'img/icons/room_recolor.png')],
                      OUT / 'review' / 'sheet_all.png', title='room icon round 3 (home + directory + bedroom)')


if __name__ == '__main__':
    names = sys.argv[1:] or list(CANDIDATES)
    for n in names:
        print('wrote', export(n, CANDIDATES[n]()))
    print('wrote', review(list(CANDIDATES)))
