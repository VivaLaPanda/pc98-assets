"""NAME: drawn by hand in code. Run: uv run pc98 render NAME [candidate...]

Draw in VGA letters at 48x48 (K black, W white, S silver, G grey, y yellow, c cyan, R red, r maroon, n navy, ...: see
pc98/palette.py), light from the top left, Windows 98 outlines (G on the lit side, K on the shadow side), the 50%
checker between tones. Then recolour into the site's PC-98 palette: icon.recolor() with a base map for the whole icon
and (mask, map) regions for parts that must differ (a white feather on periwinkle paper). See
assets/blog-icon/draw.py for three worked examples, and the README's "Nav icons" section for the rules.
"""
import sys
from pathlib import Path

import numpy as np

from pc98.pixel import Grid, rect, ellipse, poly, line, polyline, grow, shrink
from pc98 import icon
from pc98.icon import PAPER, recolor, words, place

OUT = Path(__file__).parent / 'out'


def candidate_a():
    g = Grid(48, 48)
    m = {}
    body = rect(g, 6, 6, 41, 43)
    g.fill(body, 'W')
    g.dither(rect(g, 36, 7, 40, 42), 'W', 'S')           # shading toward the shadow side
    g.edge(body, 'G', 'tl'); g.edge(body, 'K', 'br')
    rng = np.random.default_rng(1)
    for i, y in enumerate(range(12, 38, 3)):
        words(g, 10, 36, y, rng, indent=2 if i == 0 else 0)
    m['body'] = body
    return g, m


def candidate_a_rc(g, m):
    return recolor(g, PAPER)


CANDIDATES = {
    'candidate_a': (candidate_a, candidate_a_rc),
}


if __name__ == '__main__':
    names = sys.argv[1:] or list(CANDIDATES)
    for n in names:
        draw, rc = CANDIDATES[n]
        g, m = draw()
        print('wrote', *icon.export(n, g, rc(g, m), OUT))
    for p in icon.review(OUT, list(CANDIDATES)):
        print('wrote', p)
    # next: uv run pc98 compare out.png blog assets/NAME/out/candidate_a_recolor.png
