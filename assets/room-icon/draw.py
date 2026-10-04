"""room-icon: the sidebar icon for Panda's Room (/room.html, the "find me online" page). Run:
    uv run pc98 render room-icon [candidate...]

Drawn by hand in code at 48x48 in VGA letters (the Windows 98 convention of the site's original icons), then
recoloured into the frame's PC-98 palette, the same way as assets/blog-icon (the approved newspaper). Light from the
top left; Windows 98 outlines (grey on the lit side, black on the shadow side); one mid tone plus the 50% checker.

Candidates:
  house  a little house at night in three-quarter view, a lit window and a door: "come over to my place".
  bed    a bed with Panda's plush on the pillow: the room itself, and the plush from the scene.
  door   a door left open, warm light spilling out onto the floor: "come in".
"""
import sys
from pathlib import Path

import numpy as np

from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow, shrink
from pc98 import icon
from pc98.icon import PAPER, recolor

OUT = Path(__file__).parent / 'out'


# ---------------------------------------------------------------------------------------------------------------
# A. house: gable end facing front-left, the long side receding to the right (the computer's and globe's
#    three-quarter view). Pink roof, periwinkle walls, a warm lit window on the side, a door in the gable.
# ---------------------------------------------------------------------------------------------------------------

def house():
    g = Grid(48, 48)
    m = {}
    A, E = (14, 11), (26, 25)                     # gable apex, front-right eave
    D = (17, -6)                                  # depth: front corner -> back corner
    A2, E2 = (A[0] + D[0], A[1] + D[1]), (E[0] + D[0], E[1] + D[1])
    # side wall (in shadow), receding to the right
    side = poly(g, [(25, 25), (42, 19), (42, 39), (25, 45)])
    g.fill(side, 'S')
    g.dither(side, 'S', 'G')
    # front gable wall (lit)
    front = rect(g, 4, 25, 25, 45) | poly(g, [(4, 25), (14, 14), (25, 25)])
    g.fill(front, 'W')
    g.dither(rect(g, 4, 41, 25, 45) & front, 'W', 'S')       # a little shade at the foot of the wall
    g.edge(front, 'G', 'tl')
    g.edge(front, 'K', 'b')
    g.fill(line(g, 25, 25, 25, 45), 'K')                     # the corner, where the lit wall turns away
    g.edge(side, 'K', 'br')
    m['walls'] = front | side
    # roof: the plane over the side wall, and the gable's bargeboard over the front
    roof = poly(g, [A, A2, E2, E])
    g.fill(roof, 'R')
    for k in range(3, 18, 3):                                # rows of tiles, parallel to the eave
        g.fill(line(g, A[0] + (E[0] - A[0]) * k // 17, A[1] + (E[1] - A[1]) * k // 17,
                    A2[0] + (E2[0] - A2[0]) * k // 17, A2[1] + (E2[1] - A2[1]) * k // 17) & roof, 'r')
    g.edge(roof, 'K', 'br')
    g.fill(line(g, A[0], A[1], A2[0], A2[1]), 'W')           # the ridge catches the light
    barge = polyline(g, [(2, 26), A, E]) | polyline(g, [(3, 26), (A[0], A[1] + 1), (E[0] - 1, E[1])])
    g.fill(barge, 'R')
    g.fill(polyline(g, [(2, 26), A]), 'W')                   # lit edge of the bargeboard
    g.fill(polyline(g, [(A[0] + 1, A[1]), E]), 'r')
    g.fill(polyline(g, [(3, 27), (A[0], A[1] + 2), (E[0] - 2, E[1])]), 'K')   # its shadow on the gable
    m['roof'] = roof | barge
    # chimney on the roof plane, toward the back
    ch = rect(g, 31, 3, 35, 11)
    g.fill(ch, 'S')
    g.fill(rect(g, 34, 3, 35, 11), 'G')
    g.fill(rect(g, 30, 2, 36, 3), 'G')
    g.edge(ch | rect(g, 30, 2, 36, 3), 'K')
    m['chimney'] = ch | rect(g, 30, 2, 36, 3)
    # warm window on the side wall (a parallelogram following the wall), four panes
    win = poly(g, [(29, 28), (38, 25), (38, 34), (29, 37)])
    g.fill(win, 'y')
    g.dither(poly(g, [(33, 27), (38, 25), (38, 34), (33, 36)]), 'y', 'W', pattern='q1')
    g.edge(win, 'K')
    g.fill(line(g, 33, 27, 33, 35), 'K')
    g.fill(line(g, 30, 32, 37, 30), 'K')
    m['window'] = win
    # door in the gable, with a step and a knob
    door = rect(g, 11, 33, 18, 44)
    g.fill(door, 'r')
    g.fill(rect(g, 12, 34, 17, 34) | rect(g, 12, 34, 12, 44), 'R')
    g.fill(rect(g, 13, 36, 16, 39), 'R'); g.edge(rect(g, 13, 36, 16, 39), 'K', 'br')
    g.edge(door, 'K')
    g.fill(rect(g, 16, 40, 16, 40), 'y')
    m['door'] = door
    # a small round window in the gable, lit
    gw = ellipse(g, 12, 18, 17, 23)
    g.fill(gw, 'y'); g.edge(gw, 'K')
    g.fill(rect(g, 13, 19, 14, 19), 'W')
    m['window'] |= gw
    return g, m


def house_rc(g, m):
    out = recolor(g, PAPER, [(m['roof'], {'R': 'h', 'r': 'u', 'W': 'k'}),
                             (m['door'], {'R': 'n', 'r': 'r', 'y': 'y'}),
                             (m['walls'] & ~m['window'] & ~m['door'], {'W': 'p', 'S': 'a', 'G': 'u'}),
                             (m['chimney'], {'S': 'a', 'G': 'u'})])
    return out


# ---------------------------------------------------------------------------------------------------------------
# B. bed: a single bed seen from the foot-left, headboard at the left, a pink blanket folded back, and Panda's plush
#    (the one from the room) sitting against the pillow.
# ---------------------------------------------------------------------------------------------------------------

PANDA = '''
.KKK.....KKK.
KKKKK...KKKKK
KKKWWWWWWWKKK
.KWWWWWWWWWK.
KWWWWWWWWWWWK
KWKKKWWWKKKWK
KWKWKWWWKWKWK
KWKKKWKWKKKWK
KWWWWKKKWWWWK
KSWWWWKWWWWSK
.KSWWWWWWWSK.
..KKKKKKKKK..
'''

PANDA_BODY = '''
..KKKKKKKKK..
.KKKWWWWWKKK.
KKKKWWWWWKKKK
KKKWWWWWWWKKK
KKKWWWWWWWKKK
.KKWWWWWWWKK.
.KKKSSSSSKKK.
.KKKK.K.KKKK.
'''


def bed():
    g = Grid(48, 48)
    m = {}
    # headboard (wood) at the left
    hb = rect(g, 2, 10, 9, 44)
    g.fill(hb, 'o')
    g.dither(rect(g, 7, 11, 8, 43), 'o', 'r')
    g.fill(rect(g, 2, 10, 9, 12), 'y')                       # lit top rail
    g.edge(hb, 'G', 'tl'); g.edge(hb, 'K', 'br')
    m['wood'] = hb.copy()
    # mattress / blanket: top surface and the side hanging toward us
    top = poly(g, [(9, 25), (45, 25), (45, 31), (9, 31)])
    face = rect(g, 9, 31, 45, 40)
    g.fill(top, 'm'); g.fill(face, 'p')
    g.dither(rect(g, 9, 31, 45, 32), 'm', 'p')
    m['blanket'] = top | face
    # the blanket folded back near the pillow: a white sheet band
    fold = rect(g, 20, 25, 24, 40)
    g.fill(fold, 'W'); g.dither(rect(g, 20, 31, 24, 40), 'W', 'S')
    g.fill(rect(g, 24, 25, 24, 40), 'S')
    m['sheet'] = fold
    # pillow against the headboard
    pil = ellipse(g, 9, 19, 22, 28)
    g.fill(pil, 'W'); g.dither(pil & rect(g, 9, 25, 22, 28), 'W', 'S')
    g.edge(pil, 'G', 'tl'); g.edge(pil, 'K', 'br')
    m['sheet'] |= pil
    g.edge(top | face, 'G', 'tl'); g.edge(top | face, 'K', 'br')
    g.fill(line(g, 9, 31, 45, 31), 'K')                      # the mattress edge
    g.fill(line(g, 20, 25, 20, 40) | line(g, 24, 25, 24, 40), 'G')
    # frame rail and legs
    rail = rect(g, 9, 41, 45, 43)
    g.fill(rail, 'o'); g.fill(rect(g, 9, 41, 45, 41), 'y'); g.edge(rail, 'K', 'br')
    legs = rect(g, 42, 44, 45, 46) | rect(g, 3, 45, 7, 46)
    g.fill(legs, 'r'); g.edge(legs, 'K', 'br')
    m['wood'] |= rail | legs
    # Panda's plush, sitting against the pillow, over the headboard's edge
    body = Grid.parse(PANDA_BODY)
    g.paste(body, 12, 21)
    head = Grid.parse(PANDA)
    g.paste(head, 12, 9)
    pm = np.zeros((48, 48), bool)
    pm[9:9 + head.h, 12:12 + head.w] |= head.a != '.'
    pm[21:21 + body.h, 12:12 + body.w] |= body.a != '.'
    m['panda'] = pm
    return g, m


def bed_rc(g, m):
    out = recolor(g, PAPER, [(m['blanket'], {'m': 'k', 'p': 'h', 'G': 'u', 'K': 'K'}),
                             (m['wood'], {'o': 'n', 'r': 'r', 'y': 'e', 'G': 'u'}),
                             (m['sheet'], {'W': 'W', 'S': 'a', 'G': 'u'}),
                             (m['panda'], {'W': 'W', 'S': 'a', 'K': 'K'})])
    return out


# ---------------------------------------------------------------------------------------------------------------
# C. door: a door swung open toward us on its left hinge, warm light pouring out of the room and across the floor.
# ---------------------------------------------------------------------------------------------------------------

def door():
    g = Grid(48, 48)
    m = {}
    frame = rect(g, 14, 2, 41, 42)
    opening = rect(g, 17, 5, 38, 42)
    g.fill(frame & ~opening, 'S')
    g.fill(rect(g, 39, 3, 41, 42), 'G')                       # the frame's shadow side
    g.edge(frame, 'G', 'tl'); g.edge(frame, 'K', 'br')
    g.edge(opening, 'K', 'tl', inside=False)
    m['frame'] = frame & ~opening
    # the lit room beyond: bright, with a dotted fall-off toward the top
    g.fill(opening, 'y')
    g.dither(rect(g, 17, 5, 38, 9), 'y', 'W', pattern='q1')
    g.dither(rect(g, 30, 5, 38, 42), 'y', 'W', pattern='q1')
    m['light'] = opening.copy()
    # a glimpse of the room: a window with the night city, and a lamp
    win = rect(g, 27, 10, 35, 19)
    g.fill(win, 'n'); g.edge(win, 'K')
    for x, y in ((28, 13), (30, 11), (30, 14), (32, 12), (33, 15), (29, 17), (34, 17)):
        g.a[y, x] = 'y'
    m['glimpse'] = win
    # the door leaf, swung toward us: a parallelogram hinged at the frame's left edge
    leaf = poly(g, [(17, 5), (5, 9), (5, 46), (17, 42)])
    g.fill(leaf, 'o')
    g.dither(poly(g, [(13, 6), (17, 5), (17, 42), (13, 43)]), 'o', 'r')
    g.edge(leaf, 'G', 'tl'); g.edge(leaf, 'K', 'br')
    panel1 = poly(g, [(14, 10), (8, 12), (8, 24), (14, 22)])
    panel2 = poly(g, [(14, 26), (8, 28), (8, 41), (14, 39)])
    for p in (panel1, panel2):
        g.edge(p, 'r', 'tl'); g.edge(p, 'y', 'br')
    g.fill(rect(g, 7, 30, 8, 31), 'y')                        # knob
    g.fill(rect(g, 7, 32, 8, 32), 'K')
    m['wood'] = leaf
    # the light spilling out across the floor, dotted where it thins
    spill = poly(g, [(17, 43), (38, 43), (47, 47), (14, 47)])
    g.fill(spill & ~leaf, 'y')
    g.dither(poly(g, [(36, 43), (38, 43), (47, 47), (42, 47)]), 'y', '.', pattern='checker')
    g.dither(rect(g, 14, 46, 47, 47) & spill & ~leaf, 'y', '.', pattern='q1')
    m['light'] |= spill
    return g, m


def door_rc(g, m):
    out = recolor(g, PAPER, [(m['frame'], {'S': 'p', 'G': 'u'}),
                             (m['wood'], {'o': 'n', 'r': 'r', 'y': 'e', 'G': 'u'}),
                             (m['light'], {'y': 'y', 'W': 'W'}),
                             (m['glimpse'], {'n': 'b', 'y': 'y'})])
    return out


# ---------------------------------------------------------------------------------------------------------------
# B2. bed, refined: the set's periwinkle as the mattress side (the body colour of every recoloured icon), the
#     blanket a pink top with a hot-pink hem along the front, the plush sitting on the pillow rather than above it.
# ---------------------------------------------------------------------------------------------------------------

def bed2():
    g = Grid(48, 48)
    m = {}
    # headboard (wood) at the left: a post with a lit cap
    hb = rect(g, 2, 7, 8, 44)
    g.fill(hb, 'o')
    g.dither(rect(g, 6, 9, 7, 43), 'o', 'r')
    g.fill(rect(g, 2, 7, 8, 8), 'y')
    g.edge(hb, 'G', 'tl'); g.edge(hb, 'K', 'br')
    m['wood'] = hb.copy()
    # mattress side, seen square on: periwinkle, darkening toward the floor
    side = rect(g, 9, 28, 45, 38)
    g.fill(side, 'S')
    g.dither(rect(g, 9, 35, 45, 38), 'S', 'G')
    m['mattress'] = side.copy()
    # blanket: the top, seen slightly from above, and its hem hanging over the front edge
    top = rect(g, 9, 21, 45, 27)
    g.fill(top, 'm')
    g.dither(rect(g, 9, 21, 45, 22), 'm', 'W', pattern='q1')        # light on the far side of the blanket
    hem = rect(g, 25, 27, 45, 32)
    g.fill(hem, 'p')
    g.fill(rect(g, 25, 32, 45, 32), 'K')
    for x in range(28, 45, 6):                                       # folds in the hem
        g.fill(rect(g, x, 28, x, 31), 'r')
    m['blanket'] = top | hem
    # the sheet turned down over the blanket near the pillow
    sheet = rect(g, 25, 21, 28, 32)
    g.fill(sheet, 'W'); g.fill(rect(g, 28, 21, 28, 32), 'S')
    g.fill(rect(g, 25, 32, 28, 32), 'G')
    m['sheet'] = sheet.copy()
    # pillow against the headboard
    pil = ellipse(g, 8, 15, 26, 25)
    g.fill(pil, 'W'); g.dither(pil & rect(g, 8, 22, 26, 25), 'W', 'S')
    g.edge(pil, 'G', 'tl'); g.edge(pil, 'K', 'br')
    m['sheet'] |= pil
    whole = side | top | hem
    g.edge(whole, 'G', 'tl'); g.edge(whole, 'K', 'br')
    # frame rail and legs
    rail = rect(g, 9, 39, 45, 41)
    g.fill(rail, 'o'); g.fill(rect(g, 9, 39, 45, 39), 'y'); g.edge(rail, 'K', 'br')
    legs = rect(g, 42, 42, 45, 46) | rect(g, 3, 45, 7, 46)
    g.fill(legs, 'r'); g.edge(legs, 'K', 'br')
    m['wood'] |= rail | legs
    # Panda's plush, sitting on the pillow
    body = Grid.parse(PANDA_BODY)
    head = Grid.parse(PANDA)
    bx, by = 9, 19
    g.paste(body, bx, by)
    g.paste(head, bx, by - 11)
    pm = np.zeros((48, 48), bool)
    pm[by - 11:by - 11 + head.h, bx:bx + head.w] |= head.a != '.'
    pm[by:by + body.h, bx:bx + body.w] |= body.a != '.'
    m['panda'] = pm
    return g, m


def bed2_rc(g, m):
    out = recolor(g, PAPER, [(m['mattress'], {'S': 'p', 'G': 'u'}),
                             (m['blanket'], {'m': 'k', 'W': 'W', 'p': 'h', 'r': 'u', 'K': 'K', 'G': 'u'}),
                             (m['wood'], {'o': 'n', 'r': 'r', 'y': 'e', 'G': 'u'}),
                             (m['sheet'], {'W': 'W', 'S': 'a', 'G': 'u'}),
                             (m['panda'], {'W': 'W', 'S': 'a', 'K': 'K'})])
    return out


CANDIDATES = {
    'house': (house, house_rc),
    'bed': (bed, bed_rc),
    'door': (door, door_rc),
    'bed2': (bed2, bed2_rc),
}


if __name__ == '__main__':
    names = sys.argv[1:] or list(CANDIDATES)
    for n in names:
        draw, rc = CANDIDATES[n]
        g, m = draw()
        print('wrote', *icon.export(n, g, rc(g, m), OUT))
    for p in icon.review(OUT, list(CANDIDATES)):
        print('wrote', p)
