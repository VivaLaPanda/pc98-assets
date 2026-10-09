"""Export the living room for the site (vivalapanda.moe/living-room.html), as a scene the page renders live.

Writes easel/pieces/living-room/out/site/ (gitignored: the room is third-party based), all at native 500x357 (the
easel canvas without its TOP rows):
  scene.json              registers per time of day, the day inks (what lamplight falls on), lamps, blinds, devices,
                          hotspots (polygon, anchor, lit rect), the ramp hover states step along
  idx.png                 the room's index map (grey = index * 16 + 8)
  outside.png             where the glass is (white)
  outside-<phase>.png     the view through it at each time of day: the city (the bedroom's skyline), the balcony's
                          railing and floor, in that phase's registers
  light-<lamp>.png        each lamp's traced field (grey 0..255 at full brightness)
  mask-<name>.png         a lamp's shade (what glows), the TV's screen, the thermostat's face, the speakers' LEDs, each
                          hotspot object (for hover states)
  tv-backdrop@4x.png      the TV on, idle (the Chromecast's ambient photo)
  tv-play@4x.png          the TV playing: a 6-frame strip
  note@4x.png             a music note (rises off a speaker while music plays)
Run: uv run python easel/pieces/living-room/export.py
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

_spec = importlib.util.spec_from_file_location('room_export', HERE.parent / 'panda-room' / 'export.py')
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)                        # the bedroom's helpers: grow, components, trace, simplify

OUT = HERE / 'out' / 'site'
# the bedroom's registers at night, as Panda's Room has them (panda-room's piece.json): the house's night
NIGHT = ['#78b', '#767', '#67b', '#cff', '#9be', '#653', '#558', '#457', '#646', '#324', '#239', '#336', '#614',
         '#225', '#fff', '#112']
LIGHTS = {'Dining Room Light': 'dining', 'Corner Table Lamp': 'corner', 'Windowside Table': 'window',
          'The Sun': 'sun'}
# a lamp's light against the day: faint at noon (the room is already bright), full at night
LAMP_BY_PHASE = {'noon': 0.12, 'morning': 0.18, 'afternoon': 0.18, 'evening': 0.5, 'sunset': 0.6, 'dusk': 0.85,
                 'dawn': 0.85, 'night': 1.0}
# the day through the glass: how strong, and the sky's colour at each time of day (night: none)
DAY_BY_PHASE = {'noon': 0.8, 'morning': 0.72, 'afternoon': 0.75, 'evening': 0.6, 'sunset': 0.65, 'dusk': 0.22,
                'dawn': 0.26, 'night': 0.0}
# the room's ambient by day, a little under its full colours, so the light through the glass gives it a direction
AMBIENT = {'noon': 0.84, 'morning': 0.85, 'afternoon': 0.84, 'evening': 0.88, 'sunset': 0.9, 'dusk': 0.96, 'dawn': 0.96,
           'night': 1.0}
DAY_COLOR = {'noon': '#fff8f0', 'morning': '#f2f4ff', 'afternoon': '#fff0dc', 'evening': '#ffd6a0',
             'sunset': '#ff9a60', 'dusk': '#a898ff', 'dawn': '#ffc0c8', 'night': '#000000'}
BLINDS = {'Living Room Blinds': (399, 471), 'Dining Room Blinds': (479, 499)}
# hotspot objects, front to back (where they overlap, the earlier one owns the pixels)
ORDER = ['lamp_dining', 'lamp_window', 'speaker_r', 'kotatsu', 'lamp_sun', 'lamp_corner', 'speaker_l', 'thermostat',
         'tv', 'blind_living', 'blind_dining', 'door_bedroom', 'door_outside']
PAD = {'thermostat': 3, 'speaker_l': 2, 'speaker_r': 2, 'lamp_corner': 1, 'lamp_window': 1, 'lamp_sun': 2,
       'blind_living': 3, 'blind_dining': 3}


def grey_png(a, path):
    Image.fromarray(a.astype(np.uint8), 'L').save(path, optimize=True)


def mask_png(m, path):
    grey_png(np.where(m, 255, 0), path)


def hexrgb(h):
    return np.array([int(c, 16) * 17 for c in h.lstrip('#')], np.uint8)


def gbuffer(cv, ns):
    """Every canvas pixel as a room point and its normal (approximate: planes for the room, the built surfaces'
    own depth and normals where they are)."""
    VP, D = ns['VP'], ns['D']
    h, w = cv.h, cv.w
    YY, XX = np.mgrid[0:h, 0:w].astype(float)
    rx, ry = (XX - VP[0]) / D, -(YY - VP[1]) / D
    P = np.full((h, w, 3), np.nan)
    N = np.zeros((h, w, 3))

    def plane(mask, Z, n):
        P[mask] = np.stack([rx * Z, ry * Z, Z], -1)[mask]
        N[mask] = n

    back_z = ns['BACK_Z']
    plane(np.ones((h, w), bool), np.full((h, w), back_z - 6), (0, 0, -1))
    with np.errstate(divide='ignore', invalid='ignore'):
        Zl = -322 / np.where(rx != 0, rx, np.nan)
        plane(ns['REGION']['left'] | (XX < 57), np.clip(np.nan_to_num(Zl, nan=1e3), 50, 1e3), (1, 0, 0))
        Zr = 178 / np.where(rx != 0, rx, np.nan)
        right = (XX > 382) & ~ns['FLOOR_M']
        plane(right, np.clip(np.nan_to_num(Zr, nan=1e3), 50, 1e3), (-1, 0, 0))
        ceil_y = (VP[1] - 78) * back_z / D
        Zc = ceil_y / np.where(ry > 0, ry, np.nan)
        plane(ns['REGION']['ceil'], np.clip(np.nan_to_num(Zc, nan=1e3), 50, 1e3), (0, -1, 0))
    fl = ns['FLOOR_M']
    Zf = D * ns['EYE'] / np.maximum(YY - VP[1], 1e-3)
    plane(fl, Zf, (0, 1, 0))
    KQ = ns['KQ']
    q = KQ.mask()
    P[q] = np.stack([rx * KQ.depth, ry * KQ.depth, KQ.depth], -1)[q]
    n = KQ.n.copy()
    n[n[..., 2] > 0] *= -1
    N[q] = n[q]
    board = ns['KT_BOARD']
    plane(board, np.full((h, w), ns['KT_C'][2]), (0, 1, 0))
    quilt_extra = cv.masks['kotatsu'] & ~q & ~board          # the redrawn quilt's spread past 06's mesh
    plane(quilt_extra, np.clip(D * ns['EYE'] / np.maximum(YY - VP[1], 1e-3), 60, 400), (0, 0.7, -0.7))
    couch = ns['COUCH'] | cv.masks['couch']                 # the redrawn sofa's own outline (07b), not just 07's boxes
    Zc = 125 / np.where(rx > 0.01, rx, np.nan)
    plane(couch, np.clip(np.nan_to_num(Zc, nan=200), 60, 400), tuple(np.array([-0.55, 0.83, 0]) / 1.0))
    return fields.GBuffer(P, N), ceil_y


def view(ns, phase, pal_idx_rgb, T):
    """The outside through the living room's glass at `phase`, as RGB (canvas coords)."""
    VP, D = ns['VP'], ns['D']
    h, w = ns['cv'].h, ns['cv'].w
    city = outside.render(phase)
    sky = outside.sky_above(phase, 120, city.shape[1])
    tall = np.concatenate([sky, city], 0)                 # rows: -120 .. 255 of the overlook
    YY, XX = np.mgrid[0:h, 0:w]
    out = np.zeros((h, w, 3), np.uint8)
    col = np.clip(XX - 399 + 210, 0, city.shape[1] - 1)
    row = np.clip(YY - T - 90 + 120, 0, tall.shape[0] - 1)
    out[:] = tall[row, col]
    # the balcony: its railing along the façade (X 298), the rail at 110cm, the floor a step down
    with np.errstate(divide='ignore'):
        Z = D * 298 / np.maximum(XX - VP[0], 1e-3)
    y_rail = VP[1] + D * 6 / Z
    y_floor = VP[1] + D * 130 / Z
    house = np.full((h, w), 255, np.int16)                 # house inks where the balcony is (255: the city)
    below = (YY >= y_rail + 3) & (YY < y_floor)
    house[(YY >= y_rail) & (YY < y_rail + 3)] = ns['WOOD']
    house[(YY >= y_rail) & (YY < y_rail + 1)] = ns['DESK_SHADE']
    for zk in np.arange(214, 700, 12.0):
        xk = VP[0] + D * 298 / zk
        wk = max(1.0, D * 3 / zk)
        house[below & (XX >= xk - wk / 2) & (XX < xk + wk / 2)] = ns['DARK']
        house[below & (np.abs(XX - (xk - wk / 2)) < 0.5)] = ns['WOOD']
    house[YY >= y_floor] = ns['SLATE']
    house[(YY >= y_floor) & ((XX + YY) % 2 == 0)] = ns['CURTAIN']
    house[(YY >= y_floor) & (YY < y_floor + 1)] = ns['DARK']
    m = house != 255
    out[m] = pal_idx_rgb[house[m]]
    return out


def tv_art(screen_w, screen_h):
    """The TV's pictures (emissive: they don't take the room's light). Idle: the Chromecast's ambient photo, a lake
    under mountains. Playing: a sea at sunset, a sailboat drifting, the waves catching the light (6 frames)."""
    def rgb(hs):
        return np.array([hexrgb(h) for h in hs])
    yy, xx = np.mgrid[0:screen_h, 0:screen_w]
    # idle backdrop
    b = np.zeros((screen_h, screen_w, 3), np.uint8)
    sky = rgb(['#9ce', '#bde', '#dee'])
    b[:] = sky[np.clip(yy * 3 // max(screen_h // 2, 1), 0, 2)]
    mount = yy > (screen_h * 0.45 + 6 * np.sin(xx / 7.0) + 4 * np.sin(xx / 3.1 + 1))
    b[mount] = hexrgb('#6a8')
    b[mount & (yy > screen_h * 0.62)] = hexrgb('#486')
    lake = yy > screen_h * 0.72
    b[lake] = hexrgb('#7bd')
    b[lake & ((xx + yy * 3) % 7 == 0)] = hexrgb('#cef')
    frames = []
    for f in range(6):
        p = np.zeros((screen_h, screen_w, 3), np.uint8)
        sky = rgb(['#a69', '#e87', '#fc8'])
        p[:] = sky[np.clip(yy * 3 // max(int(screen_h * 0.55), 1), 0, 2)]
        sun = (xx - screen_w * 0.62) ** 2 + (yy - screen_h * 0.52) ** 2 < 36
        p[sun] = hexrgb('#ffd')
        sea = yy > screen_h * 0.55
        p[sea] = hexrgb('#537')
        glint = sea & ((xx * 2 + yy * 5 + f * 3) % 9 == 0) & (np.abs(xx - screen_w * 0.62) < 8)
        p[glint] = hexrgb('#fd9')
        wave = sea & ((xx + yy * 4 + f * 2) % 11 == 0)
        p[wave] = hexrgb('#759')
        bx = int(screen_w * 0.18 + f * 2)
        by = int(screen_h * 0.55)
        p[by - 6:by, bx + 2:bx + 3] = hexrgb('#223')                # the mast
        for k in range(5):
            p[by - 6 + k, bx + 3:bx + 4 + k] = hexrgb('#fff')       # the sail
        p[by:by + 2, bx - 1:bx + 7] = hexrgb('#223')                # the hull
        frames.append(p)
    return b, frames


NOTE = '''
...KK
...KWK
...K.K
...K..
.KKK..
KWWK..
KWWK..
.KK...
'''


def main():
    cv, _ = easel.run('living-room')
    ns = cv.ns
    ns['cv'] = cv
    T = ns['TOP']
    H = ns['HOUSE_NAMES']
    day = list(ns['HOUSE'])
    keep = {H['screen'], H['white']}
    pals = {ph: phases.palette(day, NIGHT, ph, keep=keep) for ph in phases.PHASES}
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    def crop(a):
        return a[T:]

    idx = crop(cv.idx)
    grey_png(idx.astype(int) * 16 + 8, OUT / 'idx.png')

    # the outside, per phase
    # the glass that is still glass: not what stands in front of it (the couch, the arc lamp, the side table)
    glass = ns['GLASS'] & np.isin(cv.idx, [ns['SCREEN'], ns['PAPER'], ns['CURTAIN'], ns['GLOW']])
    for k in ('couch', 'kotatsu', 'lamp_dining', 'lamp_window', 'speaker_r'):
        glass &= ~cv.masks[k]
    mask_png(crop(glass), OUT / 'outside.png')
    layers = {}
    for ph in phases.PHASES:
        prgb = np.array([hexrgb(h) for h in pals[ph]])
        v = view(ns, ph, prgb, T)
        rgba = np.zeros(v.shape[:2] + (4,), np.uint8)
        rgba[..., :3] = v
        rgba[glass, 3] = 255
        Image.fromarray(crop(rgba), 'RGBA').save(OUT / f'outside-{ph}.png', optimize=True)
        layers[ph] = f'outside-{ph}.png'

    # lamplight
    g, ceil_y = gbuffer(cv, ns)
    g.P[glass] = np.nan                                     # true glass takes no lamplight (its view is outside)
    F0 = ns['FLOOR_Y']
    lamps = {
        'dining': fields.Lamp((75, F0 + 118, 158), 'down', 150, 1.0),
        'corner': fields.Lamp((-10, 22, 246), 'omni', 110, 1.0),
        'window': fields.Lamp((167, -22, 245), 'omni', 100, 1.0),
        'sun': fields.Lamp((-190, F0 + 190, 250), 'up', 230, 1.0),
    }
    light_spec = {}
    for name, lamp in lamps.items():
        E = fields.ceiling_bounce(g, lamp, ceil_y) if lamp.kind == 'up' else fields.irradiance(g, lamp)
        top = fields.reference(lamp, 45.0)                  # full brightness ~45cm from the lamp, for every lamp
        f = fields.to_field(E, top)
        grey_png(crop(f), OUT / f'light-{name}.png')
        shade = ns['cv'].masks[f'shade_{name}']
        mask_png(crop(shade), OUT / f'mask-shade-{name}.png')
        light_spec[name] = {'field': f'light-{name}.png', 'shade': f'mask-shade-{name}.png', 'gain': 0.9,
                            'phaseGain': LAMP_BY_PHASE}
    # the TV's glow (when on) and the kotatsu's heater (a red glow at its hem)
    tv_l = fields.Lamp((91, -28, 236), 'omni', 120, 1.0)
    E = fields.irradiance(g, tv_l)
    grey_png(crop(fields.to_field(E, np.percentile(E[np.isfinite(g.P[..., 0])], 99.5))), OUT / 'light-tv.png')
    light_spec['tv'] = {'field': 'light-tv.png', 'shade': None, 'gain': 0.45, 'color': '#8bf', 'phaseGain': LAMP_BY_PHASE}
    kt = ns['KT_C']
    heater = fields.Lamp((kt[0], F0 + 6, kt[2]), 'omni', 60, 1.0)
    E = fields.irradiance(g, heater)
    # the heater's glow shows only where it leaks out: the floor in a ring at the quilt's hem
    hem_ring = R.grow(cv.masks['kotatsu'], 6) & ~cv.masks['kotatsu'] & ns['FLOOR_M']
    E = np.where(hem_ring, E, 0)
    grey_png(crop(fields.to_field(E, np.percentile(E[E > 0], 99) if (E > 0).any() else 1)), OUT / 'light-kotatsu.png')
    light_spec['kotatsu'] = {'field': 'light-kotatsu.png', 'shade': None, 'gain': 0.5, 'color': '#f52',
                             'phaseGain': LAMP_BY_PHASE}
    # daylight through the sliding doors: their glass as a grid of points shining into the room (-X)
    pts = [(178, y, z) for z in np.linspace(185, 262, 7) for y in np.linspace(-110, 60, 6)]
    E = fields.window(g, np.array(pts), (-1, 0, 0), 260)
    ref = fields.window(fields.GBuffer(np.array([[[130.0, F0, 225.0]]]), np.array([[[0.0, 1.0, 0.0]]])), np.array(pts),
                        (-1, 0, 0), 260)[0, 0]
    grey_png(crop(fields.to_field(E, ref)), OUT / 'light-daylight.png')
    light_spec['daylight'] = {'field': 'light-daylight.png', 'shade': None, 'gain': 1.0, 'phaseGain': DAY_BY_PHASE,
                              'phaseColor': DAY_COLOR}

    # devices
    for k in ('screen', 'thermostat_face', 'speaker_l_led', 'speaker_r_led'):
        mask_png(crop(cv.masks[k]), OUT / f'mask-{k}.png')
    sm = crop(cv.masks['screen'])
    ys, xs = np.nonzero(sm)
    scr = {'x': int(xs.min()), 'y': int(ys.min()), 'w': int(xs.max() - xs.min() + 1), 'h': int(ys.max() - ys.min() + 1)}
    backdrop, frames = tv_art(scr['w'], scr['h'])
    R.x4(Image.fromarray(backdrop)).save(OUT / 'tv-backdrop@4x.png')
    strip = np.concatenate(frames, 1)
    R.x4(Image.fromarray(strip)).save(OUT / 'tv-play@4x.png')
    rows = NOTE.strip('\n').splitlines()
    note = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == 'K':
                note[j, i] = (34, 34, 68, 255)
            elif ch == 'W':
                note[j, i] = (255, 255, 255, 255)
    R.x4(Image.fromarray(note, 'RGBA')).save(OUT / 'note@4x.png')

    def centre(m):
        ys, xs = np.nonzero(m)
        k = int(np.argmin((ys - ys.mean()) ** 2 + (xs - xs.mean()) ** 2))
        return [int(xs[k]), int(ys[k])]

    # hotspots: owned masks front to back, outlines, anchors, lit rects
    objs = {
        'door_bedroom': ns['OBJ']['left_door'],
        'door_outside': ((ns['XX'] >= 397) & (ns['YY'] > ns['VAL_Y'](ns['XX'])) & (ns['YY'] < ns['TRACK_Y'](ns['XX']))),
        'lamp_sun': cv.masks['lamp_sun'], 'lamp_dining': cv.masks['lamp_dining'],
        'lamp_corner': cv.masks['lamp_corner'], 'lamp_window': cv.masks['lamp_window'],
        'speaker_l': cv.masks['speaker_l'], 'speaker_r': cv.masks['speaker_r'],
        'thermostat': cv.masks['thermostat'], 'tv': cv.masks['tv'], 'kotatsu': cv.masks['kotatsu'],
        'blind_living': cv.masks['blind_living'], 'blind_dining': cv.masks['blind_dining'],
    }
    taken = np.zeros(cv.idx.shape, bool)
    hot = {}
    for name in ORDER:
        m = objs[name] & ~taken
        taken |= m
        mc = crop(m)
        mask_png(mc, OUT / f'mask-obj-{name}.png')
        hit = R.grow(mc, PAD.get(name, 0)) if PAD.get(name) else mc
        comp = max(R.components(R.shrink(R.grow(hit, 2), 2) | hit), key=lambda c: c.sum())
        ys, xs = np.nonzero(R.grow(mc, 1))
        hot[name] = {'polygon': R.simplify(R.trace(comp), eps=0.6), 'anchor': centre(mc),
                     'lit': {'x': int(xs.min()), 'y': int(ys.min()), 'w': int(xs.max() - xs.min() + 1),
                             'h': int(ys.max() - ys.min() + 1)},
                     'mask': f'mask-obj-{name}.png'}

    # blinds: each over its panes, from under the valance down toward the track
    blinds = {}
    for name, (x0, x1) in BLINDS.items():
        blinds[name] = {'x0': x0, 'x1': x1,
                        'top': [float(ns['VAL_Y'](x0) - T + 7), float(ns['VAL_Y'](x1) - T + 7)],   # under the roll
                        'bottom': [float(ns['TRACK_Y'](x0) - T - 1), float(ns['TRACK_Y'](x1) - T - 1)]}

    ramp = {H['black']: H['dark'], H['dark']: H['slate'], H['slate']: H['wall_shade'], H['wall_shade']: H['wall'],
            H['wall']: H['curtain'], H['wood']: H['desk_shade'], H['desk_shade']: H['desk'], H['desk']: H['paper'],
            H['bedspread']: H['desk'], H['red']: H['bedspread'], H['floor']: H['glow'], H['glow']: H['curtain'],
            H['curtain']: H['paper']}
    spec = {
        'size': [cv.w, cv.h - T], 'scale': 4, 'idx': 'idx.png', 'registers': H,
        'phases': pals, 'albedo': day, 'ambient': AMBIENT,
        'outside': {'mask': 'outside.png', 'layers': layers},
        'lights': light_spec, 'light_names': LIGHTS,
        'tv': {'screen': scr, 'mask': 'mask-screen.png', 'glow': 'light-tv.png', 'backdrop': 'tv-backdrop@4x.png',
               'play': {'src': 'tv-play@4x.png', 'frames': 6, 'fps': 3}},
        'kotatsu': {'glow': 'light-kotatsu.png', 'plug': 'Kotatsu'},
        'thermostat': {'face': 'mask-thermostat_face.png'},
        'speakers': {'leds': ['mask-speaker_l_led.png', 'mask-speaker_r_led.png'],
                     'at': [hot['speaker_l']['anchor'], hot['speaker_r']['anchor']], 'note': 'note@4x.png'},
        'blinds': blinds,
        'hotspots': hot, 'z_order': ORDER, 'ramp': {str(k): v for k, v in ramp.items()},
        'masks': ['mask-screen.png', 'mask-thermostat_face.png', 'mask-speaker_l_led.png', 'mask-speaker_r_led.png']
                 + [h['mask'] for h in hot.values()],
    }
    (OUT / 'scene.json').write_text(json.dumps(spec, indent=1))
    # the room at noon with everything off: what the page shows before (or without) the live render
    prgb = np.array([hexrgb(h) for h in pals['noon']])
    noon = prgb[idx].astype(np.uint8)
    lay = np.asarray(Image.open(OUT / layers['noon']))
    gm = lay[..., 3] > 0
    noon[gm] = lay[gm][:, :3]
    R.x4(Image.fromarray(noon)).save(OUT / 'noon@4x.png')
    total = sum(f.stat().st_size for f in OUT.iterdir())
    print(f'exported {len(list(OUT.iterdir()))} files, {total // 1024} KB -> {OUT}')


if __name__ == '__main__':
    main()
