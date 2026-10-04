"""8x8 tile patterns, the way PC-98 paint tools and the GRCG tile register laid them.

A pattern is an 8x8 boolean array: True is where the second ("ink") colour goes, False keeps the
first ("ground") colour. Patterns are anchored to the screen, not to the shape being filled:
pixel (x, y) uses pattern[y % 8, x % 8], exactly like the hardware tile register, so two fills
that meet line up and a pattern never "slips" at a shape's edge.

The library is deliberately small. Period art used a handful of tiles again and again: the 50%
checkerboard above all, then the 25% / 75% dot grids and 12.5% sparse dots, plus line tiles for
materials. Ask for them by name; build custom ones with `parse`.
"""

import numpy as np

# Bayer 4x4 thresholds (0..15). Level n/16 inks the cells whose threshold < n.
_BAYER4 = np.array([[0, 8, 2, 10],
                    [12, 4, 14, 6],
                    [3, 11, 1, 9],
                    [15, 7, 13, 5]])
_BAYER8 = np.array([[0, 32, 8, 40, 2, 34, 10, 42],
                    [48, 16, 56, 24, 50, 18, 58, 26],
                    [12, 44, 4, 36, 14, 46, 6, 38],
                    [60, 28, 52, 20, 62, 30, 54, 22],
                    [3, 35, 11, 43, 1, 33, 9, 41],
                    [51, 19, 59, 27, 49, 17, 57, 25],
                    [15, 47, 7, 39, 13, 45, 5, 37],
                    [63, 31, 55, 23, 61, 29, 53, 21]])


def parse(text):
    """An 8x8 (or 4x4 / 2x2, tiled up to 8x8) pattern from rows of '#' (ink) and '.' (ground)."""
    rows = [r.strip() for r in text.strip().splitlines() if r.strip()]
    a = np.array([[c == '#' for c in r] for r in rows], dtype=bool)
    h, w = a.shape
    if 8 % h or 8 % w:
        raise ValueError('pattern sides must divide 8')
    return np.tile(a, (8 // h, 8 // w))


def bayer(n, size=4):
    """The ordered-dither tile for n/16 (size 4) or n/64 (size 8) coverage."""
    m = _BAYER4 if size == 4 else _BAYER8
    return np.tile(m < n, (8 // size, 8 // size))


LIB = {
    'none': np.zeros((8, 8), bool),
    'solid': np.ones((8, 8), bool),
    # the period workhorses
    '1/16': bayer(1),           # a lone dot per 4x4: sparse sparkle, the faintest tint
    '1/8': bayer(2),            # staggered sparse dots
    '1/4': bayer(4),            # dot grid (every other pixel of every other row)
    '3/8': bayer(6),
    '1/2': bayer(8),            # the checkerboard (市松)
    '5/8': bayer(10),
    '3/4': bayer(12),           # inverse dot grid
    '7/8': bayer(14),
    '15/16': bayer(15),
    # material tiles
    'hline': parse('#\n.'),                     # every other row: CRT scanlines, blinds, cloth weave
    'vline': parse('#.'),                       # every other column: grain, ribbing
    'hline4': parse('#\n.\n.\n.'),              # sparse rows: paper lines, louvres
    'vline4': parse('#...'),
    'grid4': parse('####\n#...\n#...\n#...'),   # tiles, grilles, keyboard gaps
    'diag': parse('#...\n.#..\n..#.\n...#'),    # hatch: glass, sheen, rain
    'antidiag': parse('...#\n..#.\n.#..\n#...'),
    'brick': parse('########\n#.......\n#.......\n#.......\n########\n....#...\n....#...\n....#...'),
}

# the order tile gradients step through: banded, the way period artists stepped tones by hand
STEPS = ['none', '1/4', '1/2', '3/4', 'solid']
STEPS_FINE = ['none', '1/16', '1/8', '1/4', '3/8', '1/2', '5/8', '3/4', '7/8', 'solid']


def get(p):
    """A pattern by name, an 8x8 array as-is, or a string to parse."""
    if isinstance(p, np.ndarray):
        return p.astype(bool)
    if p in LIB:
        return LIB[p]
    if isinstance(p, str) and ('#' in p or '.' in p):
        return parse(p)
    raise KeyError(f'unknown pattern {p!r}; known: {", ".join(LIB)}')


def field(p, w, h, ox=0, oy=0):
    """The pattern tiled over a w x h area whose top-left is screen pixel (ox, oy)."""
    pat = get(p)
    ys = (np.arange(h) + oy) % 8
    xs = (np.arange(w) + ox) % 8
    return pat[np.ix_(ys, xs)]
