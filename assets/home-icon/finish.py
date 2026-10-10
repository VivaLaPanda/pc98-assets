"""home-icon, step 4: the chosen redraw (polish.py snap of fal3_draft_0: the rendered kotatsu, polished on fal beside
the real icons) finished by hand. At 48px its mikan were peach on a peach board and ran into it, so the board becomes
tan wood (its lit lip peach) and the three mikan are redrawn as outlined fruit; strays of pink on the board go. Writes
out/home_recolor.png (shown on the site) and out/home.png (the Windows-98-palette original, the pair convention).
Run:
    uv run python assets/home-icon/finish.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

from pc98 import palette as P
from pc98.pixel import Grid, poly

HERE = Path(__file__).parent
LEG = P.get('site+')
TO_VGA = {'K': 'K', 'W': 'W', 'p': 'S', 'u': 'G', 'a': 'S', 'b': 'n', 'k': 'm', 'h': 'R', 'y': 'y', 'e': 'y',
          'n': 'o', 'r': 'r', 'm': 'c', 't': 't'}
MIKAN = '''
..rrr..
.ryyer.
ryWyeer
ryyeeer
reeeenr
.rennr.
..rrr..
'''


def load(path):
    a = np.asarray(Image.open(path).convert('RGBA'))
    inv = {tuple(v[:3]): k for k, v in LEG.items() if k != '.'}
    g = Grid(48, 48)
    for y in range(48):
        for x in range(48):
            if a[y, x, 3]:
                g[x, y] = inv[tuple(a[y, x, :3])]
    return g


def finish(g):
    # the board: its top as the redraw has it (corners: back-left, back, right, front), cleared to tan wood
    BL, BK, RT, FR = (7, 17), (22, 9), (41, 15), (26, 24)
    top = poly(g, [BL, BK, RT, FR])
    edge = top & ~np.roll(top, 1, 0) | top & ~np.roll(top, -1, 0) | top & ~np.roll(top, 1, 1) | top & ~np.roll(top, -1, 1)
    yy, xx = np.mgrid[0:48, 0:48]
    on = lambda a, b: (xx >= min(a[0], b[0])) & (xx <= max(a[0], b[0])) & \
        (np.abs(yy - (a[1] + (xx - a[0]) * (b[1] - a[1]) / (b[0] - a[0]))) < 0.75)
    for y, x in zip(*np.nonzero(top & ~edge)):
        g[x, y] = 'n'
    for y, x in zip(*np.nonzero(on(BL, BK) | on(BK, RT))):
        g[x, y] = 'u' if g[x, y] != 'K' else 'K'                    # the back edges: the set's lit-side outline
    for y, x in zip(*np.nonzero(on((BL[0] + 1, BL[1] - 1), (BK[0], BK[1] + 1)) & top)):
        g[x, y] = 'e'                                                 # the lit back-left lip
    # the front edges and the board's thickness below them: lit on the left, in shade on the right
    left = on(BL, FR); right = on(FR, RT)
    below = lambda line, k: np.roll(line, k, 0)
    for y, x in zip(*np.nonzero(left)):
        g[x, y] = 'e'
    for k in (1, 2):
        for y, x in zip(*np.nonzero(below(left, k) & ~top)):
            g[x, y] = 'n' if k == 1 else 'r'
    for y, x in zip(*np.nonzero(right)):
        g[x, y] = 'r'
    for k in (1, 2):
        for y, x in zip(*np.nonzero(below(right, k) & ~top)):
            g[x, y] = 'r' if k == 1 else 'K'
    # three mikan, back first, each with a leaf
    sprite = Grid.parse(MIKAN)
    for (x, y), lf in (((20, 9), (24, 9)), ((15, 12), (19, 12)), ((25, 12), (29, 12))):
        g.paste(sprite, x, y)
        g[lf[0], lf[1]] = 't'; g[lf[0] + 1, lf[1] - 1] = 't'
    return g


if __name__ == '__main__':
    g = finish(load(HERE / 'out' / 'fal3_draft_0_recolor.png'))
    used = {k: LEG[k] for k in g.colors()}
    ok, probs = P.is_pc98(used)
    if not ok:
        raise SystemExit(f'not PC-98: {probs}')
    g.save(HERE / 'out' / 'home_recolor.png', 'site+')
    g.recolor(TO_VGA).save(HERE / 'out' / 'home.png', 'vga', mode='P')
    print('wrote', HERE / 'out' / 'home_recolor.png')
