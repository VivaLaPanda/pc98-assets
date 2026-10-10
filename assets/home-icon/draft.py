"""home-icon, step 1 of 3: rough blockouts ("draw to evoke") for the sidebar's Home icon, which opens the living room.
The user on the folder that was there (round 3 of assets/room-icon): "I don't love the folder/etc", and "try to avoid
the home icon looking clip-art-ish. It should fit well w/ the other icons" (2026-10-09). These drafts only fix the
object, its pose and its colours in the set's palette; polish.py has an image model redraw each one beside the real
icons (so it takes their pixel grid, outlines and shading), then snaps it back to the palette. Run:
    uv run python assets/home-icon/draft.py

  kotatsu    the living room's kotatsu: a plaid quilt draped from a wooden board, a bowl of mikan on top
  house      a little house in the computer's three-quarter view: a pink tiled roof, warm windows, a door
  cozyhouse  the same house with one big window glowing, the kotatsu and its mikan inside
"""
import sys
from pathlib import Path

from pc98.pixel import Grid, rect, ellipse, poly, line

OUT = Path(__file__).parent / 'out' / 'draft'
LEG = 'site+'


def shade(g, m, lit='u', dark='K'):
    g.edge(m, lit, 'tl')
    g.edge(m, dark, 'br')


def mikan(g, cx, cy):
    m = ellipse(g, cx - 3, cy - 3, cx + 3, cy + 2)
    g.fill(m, 'n'); g.dither(m & rect(g, cx - 3, cy - 3, cx, cy), 'n', 'e')
    g[cx - 1, cy - 2] = 'y'; shade(g, m, 'r', 'r')
    g[cx, cy - 3] = 't'; g[cx + 1, cy - 4] = 't'


def kotatsu():
    g = Grid(48, 48)
    # the quilt: a front face and a right side in shade, its hem waving at the floor
    front = poly(g, [(3, 20), (39, 20), (41, 43), (36, 45), (28, 43), (20, 45), (12, 43), (4, 45), (2, 42)])
    side = poly(g, [(39, 20), (45, 13), (46, 37), (41, 43)])
    for m in (front, side):
        g.fill(m, 'k')
    for x in range(6, 46, 9):
        g.fill(rect(g, x, 12, x + 1, 46) & (front | side), 'h')
    for y in range(26, 46, 8):
        g.fill(rect(g, 0, y, 47, y) & (front | side), 'h')
    g.fill(rect(g, 0, 30, 47, 30) & (front | side), 'y')
    g.dither(side, 'k', 'u')
    g.dither(rect(g, 0, 40, 47, 47) & front, 'k', 'u', pattern='q1')
    shade(g, front); shade(g, side)
    # the board on top: tan, lit edge, a rust front lip
    board = poly(g, [(9, 11), (45, 11), (40, 19), (3, 19)])
    g.fill(board, 'n'); g.dither(rect(g, 0, 11, 47, 13) & board, 'n', 'e')
    g.fill(rect(g, 3, 20, 40, 21) & ~front | line(g, 3, 20, 40, 20), 'r')
    shade(g, board, 'e', 'K')
    # a bowl of mikan
    bowl = ellipse(g, 16, 9, 32, 17)
    g.fill(bowl & rect(g, 0, 13, 47, 17), 'p'); g.edge(bowl & rect(g, 0, 13, 47, 17), 'K', 'br')
    g.fill(line(g, 17, 13, 31, 13), 'W')
    for cx, cy in ((20, 11), (27, 11), (24, 8)):
        mikan(g, cx, cy)
    return g


def house_body(g):
    front = rect(g, 6, 22, 29, 44)
    side = poly(g, [(30, 22), (44, 15), (44, 38), (30, 44)])
    g.fill(front, 'p'); g.fill(rect(g, 7, 23, 28, 23), 'W'); g.fill(rect(g, 7, 23, 7, 43), 'W')
    g.fill(side, 'p'); g.dither(side, 'p', 'u')
    shade(g, front); shade(g, side)
    gable = poly(g, [(5, 22), (18, 8), (31, 22)])
    g.fill(gable, 'p'); shade(g, gable)
    roof = poly(g, [(18, 7), (33, 1), (46, 15), (31, 22)])
    g.fill(roof, 'k')
    for k in range(4, 20, 4):
        g.fill(line(g, 18 + k * 0.55, 7 + k * 0.7, 33 + k * 0.6, 1 + k * 0.7), 'h')
    g.fill(line(g, 18, 7, 31, 22), 'W'); g.fill(line(g, 33, 1, 46, 15), 'K')
    shade(g, roof, 'u', 'K')
    ch = rect(g, 36, 2, 39, 8)
    g.fill(ch, 'a'); shade(g, ch)
    door = rect(g, 20, 31, 26, 44)
    g.fill(door, 'n'); shade(g, door, 'e', 'r'); g[25, 38] = 'y'
    return front, side


def house():
    g = Grid(48, 48)
    house_body(g)
    win = rect(g, 9, 28, 17, 36)
    g.fill(win, 'y'); g.dither(rect(g, 13, 32, 17, 36), 'y', 'e')
    g.fill(line(g, 13, 28, 13, 36) | line(g, 9, 32, 17, 32), 'W'); shade(g, win, 'K', 'u')
    w2 = poly(g, [(34, 25), (40, 22), (40, 29), (34, 32)])
    g.fill(w2, 'y'); g.dither(w2, 'y', 'e'); shade(g, w2, 'K', 'u')
    gw = ellipse(g, 15, 13, 21, 19)
    g.fill(gw, 'y'); shade(g, gw, 'K', 'u')
    return g


def cozyhouse():
    g = Grid(48, 48)
    house_body(g)
    win = rect(g, 8, 26, 18, 38)
    g.fill(win, 'e'); g.dither(rect(g, 8, 26, 18, 31), 'y', 'e')
    k = poly(g, [(9, 34), (17, 34), (18, 38), (8, 38)])
    g.fill(k, 'k'); g.fill(line(g, 9, 34, 17, 34), 'n')
    g[11, 33] = 'n'; g[13, 33] = 'n'; g[15, 33] = 'n'; g[12, 32] = 'e'; g[14, 32] = 'e'
    g.fill(line(g, 13, 26, 13, 33), 'W'); shade(g, win, 'K', 'u')
    w2 = poly(g, [(34, 25), (40, 22), (40, 29), (34, 32)])
    g.fill(w2, 'y'); g.dither(w2, 'y', 'e'); shade(g, w2, 'K', 'u')
    return g


DRAFTS = {'kotatsu': kotatsu, 'house': house, 'cozyhouse': cozyhouse}

if __name__ == '__main__':
    for n in sys.argv[1:] or list(DRAFTS):
        g = DRAFTS[n]()
        g.save(OUT / f'{n}.png', LEG)
        print('wrote', OUT / f'{n}.png')
