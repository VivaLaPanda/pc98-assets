"""Export Panda's Room as a live scene for the site's renderer (js/house-render.js): the same day/night cycle as the
living room, and the stand lamp mirroring Panda's real bedroom lamp (Bedroom Lamp A/B). Nothing else in the bedroom
follows the house.

Writes easel/pieces/panda-room/out/site-house/ (gitignored: the room is third-party based), native 500x357:
  scene.json            registers per time of day (the night is the room as it was drawn), day inks, the stand lamp,
                        the glass and its view per phase, each hotspot's mask and lit rect, the hover ramp
  idx.png               the room's index map (grey = index * 16 + 8)
  outside.png           the balcony door's glass and the low city behind the balusters
  outside-<phase>.png   the view at each time of day but night (the night is the room's own skyline and moon)
  light-stand.png       the stand lamp's traced field; mask-shade-stand.png its shade
  mask-obj-<id>.png     each hotspot object (exclusive, front first), for hover states drawn in the current light
Run: uv run python easel/pieces/panda-room/export_house.py
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'src'))
sys.path.insert(0, str(HERE.parent / 'house'))
import easel  # noqa: E402
import fields  # noqa: E402
import outside  # noqa: E402
import phases  # noqa: E402

_spec = importlib.util.spec_from_file_location('room_export', HERE / 'export.py')
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

OUT = HERE / 'out' / 'site-house'
# the room's inks by day (mahou_bedroom's own colours; the three light registers keep the computer's light)
DAY = dict(paper='#fff', desk='#fca', curtain='#cde', screen='#cff', glow='#bcd', bedspread='#e92', wall='#aa9',
           wall_shade='#897', desk_shade='#c77', wood='#743', floor='#46d', slate='#557', red='#c14', dark='#344',
           white='#fff', black='#111')
LIGHTS = {'Bedroom Lamp A': 'stand', 'Bedroom Lamp B': 'stand'}
LAMP_BY_PHASE = {'noon': 0.25, 'morning': 0.35, 'afternoon': 0.35, 'evening': 0.65, 'sunset': 0.75, 'dusk': 0.9,
                 'dawn': 0.9, 'night': 1.0}
KNICK = ['stand_lamp', 'desk_lamp']


def grey_png(a, path):
    Image.fromarray(a.astype(np.uint8), 'L').save(path, optimize=True)


def hexrgb(h):
    return np.array([int(c, 16) * 17 for c in h.lstrip('#')], np.uint8)


def glass_mask(cv, ns):
    """The panes above the rail and the low city between the balusters: the pixels the night drew as city."""
    T = ns['TOP']
    names = cv.names
    city = [names[k] for k in ('black', 'slate', 'glow', 'screen', 'white', 'red', 'paper', 'floor', 'dark')]
    g = np.zeros(cv.idx.shape, bool)
    g[T + 30:T + 118, 191:235] = True
    g[T + 30:T + 118, 240:284] = True
    low = np.zeros(cv.idx.shape, bool)
    low[T + 134:T + 173, 188:230] = True
    low[T + 134:T + 173, 237:284] = True
    for x in (194, 208, 221, 245, 258, 271):               # the balusters stay (mahou-pc 00's POSTS)
        low[:, x:x + 5] = False
    g |= low
    g &= np.isin(cv.idx, city)
    g &= ~R.grow(cv.masks['butterfly'], 1) & ~R.grow(cv.masks['linkedin'], 1)
    return g


def view(cv, ns, phase):
    """The city at `phase` where the glass is (mahou-pc 00's crops of city_overlook, re-rendered)."""
    T = ns['TOP']
    city = outside.render(phase)
    out = np.zeros(cv.idx.shape + (3,), np.uint8)
    for i, (x0, x1) in enumerate([(191, 235), (240, 284)]):
        out[T + 30:T + 118, x0:x1] = city[16:104, 30 + i * 60:30 + i * 60 + (x1 - x0)]   # mahou row - 14
    out[T + 134:T + 173, 188:284] = city[172:211, 162:258]
    return out


def gbuffer(cv, ns):
    """The bedroom as planes, roughly: the back wall, the side walls, the floor; the bed's top as its own plane."""
    VP, D = ns['VP'], ns['D']
    h, w = cv.h, cv.w
    YY, XX = np.mgrid[0:h, 0:w].astype(float)
    rx, ry = (XX - VP[0]) / D, -(YY - VP[1]) / D
    P = np.zeros((h, w, 3))
    N = np.zeros((h, w, 3))
    back_z = 226.0
    floor_y = -141.0
    P[:] = np.stack([rx * back_z, ry * back_z, np.full_like(rx, back_z)], -1)
    N[:] = (0, 0, -1)
    with np.errstate(divide='ignore', invalid='ignore'):
        left = XX < 46
        Zl = np.where(rx < -1e-3, -230 / rx, back_z)
        P[left] = np.stack([rx * Zl, ry * Zl, Zl], -1)[left]
        N[left] = (1, 0, 0)
        Zf = np.where(ry < -1e-3, floor_y / ry, 1e3)
        fl = (Zf < back_z) & (YY > VP[1])
        P[fl] = np.stack([rx * Zf, ry * Zf, Zf], -1)[fl]
        N[fl] = (0, 1, 0)
        bed = np.isin(cv.idx, [cv.names['bedspread'], cv.names['desk']]) & (XX < 175) & (YY > 160)
        Zb = np.where(ry < -1e-3, -113 / ry, 1e3)
        bedm = bed & (Zb < back_z)
        P[bedm] = np.stack([rx * Zb, ry * Zb, Zb], -1)[bedm]
        N[bedm] = (0, 1, 0)
    return fields.GBuffer(P, N)


def main():
    cv, _ = easel.run('panda-room')
    ns = cv.ns
    names = dict(cv.names)
    night = [cv.hex(i) for i in range(16)]
    day = list(night)
    for n, hx in DAY.items():
        day[names[n]] = hx
    keep = {names['screen'], names['white'], names['glow']}
    pals = {ph: phases.palette(day, night, ph, keep=keep) for ph in phases.PHASES}
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    grey_png(cv.idx.astype(int) * 16 + 8, OUT / 'idx.png')

    glass = glass_mask(cv, ns)
    grey_png(np.where(glass, 255, 0), OUT / 'outside.png')
    layers = {}
    for ph in phases.PHASES:
        if ph == 'night':
            continue                                       # the room's own skyline and moon
        v = view(cv, ns, ph)
        rgba = np.zeros(v.shape[:2] + (4,), np.uint8)
        rgba[..., :3] = v
        rgba[glass, 3] = 255
        Image.fromarray(rgba, 'RGBA').save(OUT / f'outside-{ph}.png', optimize=True)
        layers[ph] = f'outside-{ph}.png'

    g = gbuffer(cv, ns)
    lamp = fields.Lamp((-211, 10, 214), 'omni', 120, 1.0)
    E = fields.irradiance(g, lamp)
    grey_png(fields.to_field(E, np.percentile(E, 99.6)), OUT / 'light-stand.png')
    grey_png(np.where(cv.masks['shade_stand'], 255, 0), OUT / 'mask-shade-stand.png')
    desk = fields.Lamp((160, -6, 218), 'down', 70, 1.0)            # the arm lamp's head, turned down to the desk
    E = fields.irradiance(g, desk)
    grey_png(fields.to_field(E, np.percentile(E, 99.7)), OUT / 'light-desk.png')
    grey_png(np.where(cv.masks['shade_desk'], 255, 0), OUT / 'mask-shade-desk.png')

    hot = {}
    taken = np.zeros(cv.idx.shape, bool)
    for name in KNICK + R.ORDER:
        m = cv.masks[name] & ~taken
        taken |= m
        grey_png(np.where(m, 255, 0), OUT / f'mask-obj-{name}.png')
        ys, xs = np.nonzero(R.grow(m, 1))
        entry = {'mask': f'mask-obj-{name}.png',
                 'lit': {'x': int(xs.min()), 'y': int(ys.min()), 'w': int(xs.max() - xs.min() + 1),
                         'h': int(ys.max() - ys.min() + 1)}}
        if name in KNICK:
            comp = max(R.components(R.shrink(R.grow(m, 2), 2) | m), key=lambda c: c.sum())
            yy, xx = np.nonzero(m)
            k = int(np.argmin((yy - yy.mean()) ** 2 + (xx - xx.mean()) ** 2))
            entry['polygon'] = R.simplify(R.trace(comp), eps=0.6)
            entry['anchor'] = [int(xx[k]), int(yy[k])]
        hot[name] = entry

    LIT = ns['LIT']
    spec = {
        'size': [cv.w, cv.h], 'scale': 4, 'idx': 'idx.png', 'registers': names,
        'phases': pals, 'albedo': day,
        'outside': {'mask': 'outside.png', 'layers': layers},
        'lights': {'stand': {'field': 'light-stand.png', 'shade': 'mask-shade-stand.png', 'gain': 0.9,
                             'phaseGain': LAMP_BY_PHASE},
                   'desk': {'field': 'light-desk.png', 'shade': 'mask-shade-desk.png', 'gain': 1.0,
                            'phaseGain': LAMP_BY_PHASE}},
        'light_names': LIGHTS,
        'twinkle_phases': ['night', 'dusk'],
        'hotspots': hot, 'ramp': {str(k): int(v) for k, v in LIT.items()}, 'rim': names['glow'],
        'masks': [h['mask'] for h in hot.values()],
    }
    (OUT / 'scene.json').write_text(json.dumps(spec, indent=1))
    print(f'exported {len(list(OUT.iterdir()))} files, {sum(f.stat().st_size for f in OUT.iterdir()) // 1024} KB -> {OUT}')


if __name__ == '__main__':
    main()
