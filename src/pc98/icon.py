"""Icon export and review, the way the site's nav icons are built.

Each nav icon exists twice in img/icons/: `<name>.png`, a Windows 98 style original in the VGA palette (indexed, colour 0
transparent), and `<name>_recolor.png`, the same drawing moved into the frame's PC-98 palette (RGBA), which is what the
sidebar shows. export() writes both from one grid: draw in VGA letters, recolour with a character map (plus any
per-pixel fixes the recolour needs), and check the recolour is legal PC-98 (12-bit, at most 16 colours).
"""
from pathlib import Path

import numpy as np

from . import palette as P
from .pixel import Grid, rect
from .sheet import icon_sheet

NEIGHBOURS = ['computer', 'cd_audio', 'envelope_closed', 'globe_map']
PAPER = {'W': 'p', 'S': 'a'}       # paper white -> periwinkle, its silver shading -> mauve (as envelope_closed)


def recolor(g, base=None, regions=()):
    """VGA grid -> SITE grid: palette.VGA_TO_SITE plus `base` overrides for the whole icon, then each
    (mask, mapping) region recoloured with its own mapping (e.g. a feather that stays white on periwinkle paper)."""
    out = g.recolor({**P.VGA_TO_SITE, **(base or {})})
    for m, mp in regions:
        sub = g.recolor({**P.VGA_TO_SITE, **mp})
        out.a[m] = sub.a[m]
    return out


def words(g, x0, x1, y, rng, c='G', h=1, gap=1, lens=(2, 6), indent=0):
    """A line of type, the Windows 98 way: words of random length (seeded rng) with 1 px gaps, x0 (+indent) to <= x1.
    Returns the mask it drew."""
    m = np.zeros((g.h, g.w), bool)
    x = x0 + indent
    while x <= x1 - 1:
        n = int(rng.integers(lens[0], lens[1] + 1))
        e = min(x + n - 1, x1)
        if e - x < 1:
            break
        m |= rect(g, x, y, e, y + h - 1)
        x = e + 1 + gap
    g.fill(m, c)
    return m


def place(g, size=48, dx=0, dy=0):
    """Centre a drawing on the icon canvas, bottom-aligned like the site's icons, nudged by dx, dy."""
    c = Grid(size, size)
    x0, y0, x1, y1 = g.bbox()
    w, h = x1 - x0 + 1, y1 - y0 + 1
    c.paste(g.crop(x0, y0, x1, y1), (size - w) // 2 + dx, size - h - 1 + dy)
    return c


def export(name, g, rc, out_dir, site_legend='site+'):
    """Write <name>.png (VGA, indexed, colour 0 transparent, like the site's originals), <name>_recolor.png (RGBA,
    what the sidebar shows) and both grids as ASCII. Refuses a recolour that isn't legal PC-98 (12-bit, <= 16)."""
    out_dir = Path(out_dir)
    used = {k: P.get(site_legend)[k] for k in rc.colors()}
    ok, probs = P.is_pc98(used)
    if not ok:
        raise SystemExit(f'{name}_recolor is not PC-98: {probs}')
    orig = g.save(out_dir / f'{name}.png', 'vga', mode='P')
    g.dump(out_dir / f'{name}.txt')
    rc_path = rc.save(out_dir / f'{name}_recolor.png', site_legend)
    rc.dump(out_dir / f'{name}_recolor.txt')
    return orig, rc_path


def review(out_dir, names, site_icons=NEIGHBOURS, title=None):
    """A sheet of the candidates beside the site's four icons, originals and recolours."""
    from .config import SITE
    out_dir = Path(out_dir)
    rc = [(n, SITE / f'img/icons/{n}_recolor.png') for n in site_icons] + \
         [(n, out_dir / f'{n}_recolor.png') for n in names]
    og = [(n, SITE / f'img/icons/{n}.png') for n in site_icons] + [(n, out_dir / f'{n}.png') for n in names]
    a = icon_sheet(rc, out_dir / 'sheet_recolor.png', title=title or 'recolour (what the site shows)')
    b = icon_sheet(og, out_dir / 'sheet_original.png', title='original (Windows 98 VGA)', bg=(0, 128, 128))
    return a, b
