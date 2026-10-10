# 08 the house's devices, each where it stands in Panda's real living room (and each with a mask: what glows when it's
# on, what the hotspot is):
#  - The Sun: Panda's Brighter (getbrighter.com), a 190cm white pole lamp, beside the sideboard. Its head is above our
#    eye, so we see the disc from below: the finned heatsink, the LED ring along its rim (what lights up).
#  - Dining Room Light: the couch's arc lamp, a brass arc from behind the couch's far arm, its dome hanging out over
#    the kotatsu side of the couch.
#  - Corner Table Lamp: a drum-shade lamp on the sideboard's right end, in the TV corner.
#  - Windowside Table: a little lamp on a round side table in the window corner, with Nest Audio R beside it.
#  - Nest Audio L on the sideboard's left end (the pair flank the TV); the Nest thermostat by the hallway door.
#  - On the kotatsu: a basket of mikan, a mug, the remote.
#  - The TV's screen, off: dark glass with the room's reflection (the renderer puts on what's showing).
THINGS = {}


def outline(m, ink=BLACK):
    cv.fill(cv.m_edge(m, 'all', inside=True), ink)


def stamp_mask(x, y, art, key):
    rows = art.strip('\n').splitlines()
    pts = [(x + i, y + j) for j, r in enumerate(rows) for i, ch in enumerate(r) if ch not in '. ']
    cv.stamp(x, y, art, key)
    return cv._mask_pts(pts)


# ---- the sideboard's top: the dark box goes (the wall behind it continued from 12 rows up)
for yy in range(150, 167):
    for xx in range(244, 276):
        if cv.idx[yy, xx] in (DARK, BLACK, SLATE, WOOD) and yy < 166:
            cv.idx[yy, xx] = cv.idx[yy - 14, xx]

PRE08 = cv.idx.copy()                                  # the room before the devices (08b restores wall from it)

# ---- Nest Audio: a fabric pill, chalk white, four LED dots near its top (lit when music plays)
NEST_AUDIO = '''
..SSSS..
.SPPPCS.
SPPPPCCS
SPWPWCCS
SPPPPCCS
SPPPPCCS
SPPPPCCS
SPPPPCCS
SPPPPCCS
SPPPPCCS
SPPPPCCS
.SPPPCS.
..SSSS..
'''
_nkey = {'S': SLATE, 'P': PAPER, 'C': CURTAIN, 'W': PAPER}
with occluded(246):
    SPK_L = stamp_mask(146, 154, NEST_AUDIO, _nkey)
THINGS['speaker_l'] = SPK_L
SPK_L_LED = cv._mask_pts([(148, 157), (150, 157), (151, 157), (149, 157)]) & SPK_L

# ---- the Corner Table Lamp: a ceramic base and a cream drum shade, on the sideboard's right end
CORNER_LAMP = '''
...KKKKKKKKKKKKK...
..KHHSSSSSSSSssdK..
..KHSSSSSSSSSssdK..
.KHSSSSSSSSSSsssdK.
.KHSSSSSSSSSSsssdK.
.KHSSSSSSSSSSsssdK.
.KSSSSSSSSSSSsssdK.
KHSSSSSSSSSSSssddK.
KKKKKKKKKKKKKKKKKKK
........KbK........
........KbK........
.......KbbbK.......
......KbbcbbK......
.....KbbbcbbbK.....
.....KbbbbbcbK.....
......KbbbbbK......
.......KKKKK.......
'''
_lkey = {'K': WOOD, 'H': PAPER, 'S': DESK, 's': DESK_SHADE, 'd': WOOD, 'b': CURTAIN, 'c': GLOW}
with occluded(246):
    LAMP_CORNER = stamp_mask(249, 150, CORNER_LAMP, _lkey)
_rows = CORNER_LAMP.strip('\n').splitlines()
SHADE_CORNER = cv._mask_pts([(249 + i, 150 + j) for j, r in enumerate(_rows[:9]) for i, ch in enumerate(r)
                             if ch in 'HSsd'])
THINGS['lamp_corner'] = LAMP_CORNER

# ---- the Brighter (The Sun): white pole, round base, the disc head seen from below
BR_X, BR_Z = -190.0, 250.0
_bx, _base_y = pf((BR_X, FLOOR_Y, BR_Z))
_, _head_y = pf((BR_X, FLOOR_Y + 190, BR_Z))
_bx = int(round(_bx)); _head_y = int(round(_head_y)); _base_y = int(round(_base_y))
_r = int(round(D * 25 / BR_Z))                          # the disc's radius (50cm across)
_ry = max(3, int(round(_r * (190 - EYE) / np.hypot(BR_Z, 190 - EYE))))   # seen from below at this angle
HEAD = cv.m_ellipse(_bx, _head_y, _r, _ry)
HEAD_UNDER = HEAD & (YY >= _head_y - _ry // 3)
POLE = cv.m_rect(_bx - 1, _head_y + _ry, _bx, _base_y - 1) & ~HEAD
BASE = cv.m_ellipse(_bx, _base_y, 8, 2)
BR = HEAD | POLE | BASE
_br_ctx = occluded(BR_Z)
_br_ctx.__enter__()
cv.fill(POLE, PAPER)
cv.fill(POLE & (XX == _bx), CURTAIN)                    # the pole's side away from the glass
cv.fill(cv.m_edge(POLE, 'left,right', inside=False) & ~HEAD & ~BASE & ~cv.m_where(PAPER), SLATE)
cv.fill(BASE, PAPER)
cv.fill(BASE & (YY > _base_y), CURTAIN)
outline(BASE, SLATE)
# the head: the rim (LED ring, lit when on) is its top edge; under it the fins radiate from the hub
cv.fill(HEAD, CURTAIN)
_ang = np.arctan2((YY - _head_y) * _r / max(_ry, 1), XX - _bx)
_fins = (np.floor((_ang + np.pi) / (2 * np.pi) * 28).astype(int) % 2 == 0)
cv.fill(HEAD_UNDER & _fins, GLOW)
cv.fill(HEAD & (cv.rad((_bx, _head_y + 1), 0, 4, sy=_ry / _r) < 1), PAPER)   # the hub
RIM = HEAD & ~cv.m_ellipse(_bx, _head_y + 1, _r - 1, _ry - 1) & (YY <= _head_y)
cv.fill(RIM, PAPER)
outline(HEAD, SLATE)
_br_ctx.__exit__(None, None, None)
SHADE_SUN = RIM | (HEAD & (YY < _head_y - _ry // 2))
THINGS['lamp_sun'] = BR & _br_ctx.visible

# ---- the arc lamp (Dining Room Light): brass arc from behind the couch's far arm, the dome over the couch's seat
AR_BASE = np.array(pf((165, FLOOR_Y, 200)))
AR_TOP = np.array(pf((165, FLOOR_Y + 182, 200)))
SH_C = np.array(pf((75, FLOOR_Y + 136, 158)))           # the dome's top
_ctrl = np.array([AR_TOP[0] - 6, AR_TOP[1] - 34])
_pts = []
for t in np.linspace(0, 1, 60):                         # the pole, then the arc (a quadratic curve) to the dome
    p = (1 - t) ** 2 * AR_TOP + 2 * (1 - t) * t * _ctrl + t ** 2 * (SH_C + np.array([0, -4]))
    _pts.append(p)
ARC = np.zeros((cv.h, cv.w), bool)
for a, b in zip(_pts, _pts[1:]):
    ARC |= cv.m_line(*np.round(a).astype(int), *np.round(b).astype(int))
ARC |= cv.m_line(int(AR_BASE[0]), int(AR_BASE[1]), int(AR_TOP[0]), int(AR_TOP[1]))
ARC2 = ARC | np.roll(ARC, 1, 1)                         # 2px brass
_arc_d = np.where(ARC2 | cv.m_edge(ARC2, 'all', inside=False), np.where(YY > AR_TOP[1], 200.0, 175.0), np.inf)   # pole behind the couch; the arc nears us
_arc_ctx = occluded(_arc_d)
_arc_ctx.__enter__()
cv.fill(ARC2, DESK_SHADE)
cv.fill(ARC & ~np.roll(ARC, -1, 1), DESK)                 # its lit side
cv.fill(cv.m_edge(ARC2, 'all', inside=False) & ~ARC2 & (YY < SH_C[1]), WOOD)
_arc_ctx.__exit__(None, None, None)
ARC2 = _arc_ctx.visible & ARC2
# the dome: 36cm across, brass outside, its underside open (the bulb's glow when on)
_dr = int(round(D * 18 / 158)); _dh = int(round(D * 17 / 158))
_dx, _dy = int(round(SH_C[0])), int(round(SH_C[1]))
DOME = cv.m_ellipse(_dx, _dy + _dh, _dr, _dh) & (YY <= _dy + _dh)
LIP = cv.m_ellipse(_dx, _dy + _dh, _dr, 3)
DOME_ALL = DOME | LIP
_dome_ctx = occluded(158.0)
_dome_ctx.__enter__()
cv.fill(DOME, DESK_SHADE)
cv.grad(DOME, DESK, DESK_SHADE, cv.lin((_dx + _dr, _dy), (_dx - _dr, _dy + _dh)))
cv.fill(LIP & (YY > _dy + _dh), DESK)                   # the inside of the lip, lit by its bulb
cv.fill(LIP & (YY > _dy + _dh) & (cv.rad((_dx, _dy + _dh + 1), 0, 4) < 1), PAPER)
outline(DOME_ALL, WOOD)
_dome_ctx.__exit__(None, None, None)
SHADE_DINING = LIP & (YY > _dy + _dh - 1)
LAMP_DINING = (ARC2 | (DOME_ALL & _dome_ctx.visible))
THINGS['lamp_dining'] = LAMP_DINING

# ---- the window corner: a tall wooden side table (26cm square, 72cm high) between the TV and the curtain; the couch's
# far arm hides its legs. On it the Windowside lamp and Nest Audio R.
ST_X0, ST_X1, ST_Z0, ST_Z1, ST_H = 150.0, 176.0, 236.0, 258.0, 72.0
_c = lambda x, y, z: np.array([x, y, z], float)
_y1 = FLOOR_Y + ST_H
_faces = {
    'top': (_c(ST_X0, _y1, ST_Z1), _c(ST_X1, _y1, ST_Z1), _c(ST_X1, _y1, ST_Z0), _c(ST_X0, _y1, ST_Z0)),
    'front': (_c(ST_X0, _y1, ST_Z1), _c(ST_X0, _y1, ST_Z0), _c(ST_X0, FLOOR_Y, ST_Z0), _c(ST_X0, FLOOR_Y, ST_Z1)),
    'near': (_c(ST_X0, _y1, ST_Z0), _c(ST_X1, _y1, ST_Z0), _c(ST_X1, FLOOR_Y, ST_Z0), _c(ST_X0, FLOOR_Y, ST_Z0)),
}
TABLE = np.zeros((cv.h, cv.w), bool)
_st_ink = {'top': DESK_SHADE, 'front': WOOD, 'near': WOOD}
for _f, _q in _faces.items():
    _m = cv.m_poly([pf(p) for p in _q])
    with occluded(np.where(_m, plane_depth(*_q[:3]) - (0.3 if _f == 'top' else 0), np.inf)) as _oc:
        cv.fill(_m, _st_ink[_f])
        if _f != 'top':
            # an open frame: the sides are legs and an apron, a shelf low down; the room shows between
            _top_y = min(pf(p)[1] for p in _q)
            cv.fill(_m & (YY > _top_y + 4), DARK)
    TABLE |= _oc.visible
cv.fill(cv.m_edge(TABLE, 'all', inside=True), BLACK)
_tx, _ty = (int(round(v)) for v in pf(((ST_X0 + ST_X1) / 2, _y1, (ST_Z0 + ST_Z1) / 2)))
_tr = 6
WINDOW_LAMP = '''
..KKKKKKKKK..
.KHSSSSSssdK.
.KHSSSSSssdK.
KHSSSSSSsssdK
KHSSSSSSsssdK
KKKKKKKKKKKKK
.....KbK.....
....KbbbK....
...KbcbbbK...
...KbbbcbK...
....KKKKK....
'''
_wl_x, _wl_y = _tx - 4, _ty - 11
with occluded((ST_Z0 + ST_Z1) / 2 - 2) as _wl_oc:
    LAMP_WINDOW_M = stamp_mask(_wl_x, _wl_y, WINDOW_LAMP, _lkey)
_rows = WINDOW_LAMP.strip('\n').splitlines()
SHADE_WINDOW = cv._mask_pts([(_wl_x + i, _wl_y + j) for j, r in enumerate(_rows[:6]) for i, ch in enumerate(r)
                             if ch in 'HSsd'])
with occluded((ST_Z0 + ST_Z1) / 2 - 2) as _sr_oc:
    SPK_R = stamp_mask(_tx - _tr - 6, _ty - 12, NEST_AUDIO, _nkey)
SPK_R_LED = cv._mask_pts([(_tx - _tr - 4 + i, _ty - 9) for i in range(4)]) & SPK_R
THINGS['lamp_window'] = (LAMP_WINDOW_M & _wl_oc.visible) | TABLE
SPK_R = SPK_R & _sr_oc.visible
THINGS['speaker_r'] = SPK_R

# ---- the Nest thermostat, on the back wall by the hallway door
TH_C, TH_R = (186, 124), 4
TH = cv.m_ellipse(*TH_C, TH_R, TH_R)
TH_FACE = cv.m_ellipse(*TH_C, TH_R - 1.5, TH_R - 1.5)      # the dark glass (it shows the heat as orange: house-room.js)
_th2 = occluded(BACK_Z - 9)               # just proud of the wall (the depth buffer holds the wall at BACK_Z - 8)
_th2.__enter__()
# in the wall's own inks, so it sits in the room's light: a ring lit at the top left, in the wall's tone below,
# a slate glass (not black), the reading a soft glow, the wall's shade for its edge
cv.fill(TH, PAPER)
cv.fill(TH & (XX + YY > TH_C[0] + TH_C[1]), WALL)
cv.fill(TH_FACE, SLATE)
cv.fill(TH_FACE & (XX + YY > TH_C[0] + TH_C[1] + 1), DARK)
cv.dots([(TH_C[0] - 1, TH_C[1]), (TH_C[0], TH_C[1])], GLOW)
outline(TH, WALL_SHADE)
_th2.__exit__(None, None, None)
THINGS['thermostat'] = TH

# ---- the TV's screen, off: dark glass, a soft band of the room's reflection. The glass as the set draws it (traced
# from its inks): x 298-354 from row 166, its foot falling from y 198 to 202 across it. The set is turned ~22deg to
# the left: its face's level lines run to (-160, 165), on the room's horizon (its top, at eye level, stays flat).
TV_QUAD = [(298, 166), (355, 166), (355, 202), (298, 198)]       # the glass's corners (pixel edges): TL TR BR BL
_tv_foot = lambda x: 198 + (np.asarray(x, float) - 298) * (202 - 198) / (355 - 298)
SCREEN_M = (XX >= 298) & (XX <= 354) & (YY >= 166) & (YY + 0.5 < _tv_foot(XX + 0.5))
cv.fill(SCREEN_M, DARK)
_refl = SCREEN_M & (np.abs((XX - 297) - (YY - 165) * 1.4 - 18) < 6)
cv.tile(_refl, '1/4', DARK, SLATE)
cv.fill(SCREEN_M & (YY == 166) & (XX < 330), SLATE)
THINGS['tv'] = cv.m_rect(289, 156, 377, 245)

# (on the kotatsu: the redraw's bowl of mikan, 07b)

for k, m in (('shade_sun', SHADE_SUN), ('shade_dining', SHADE_DINING), ('shade_corner', SHADE_CORNER),
             ('shade_window', SHADE_WINDOW), ('screen', SCREEN_M), ('thermostat_face', TH_FACE),
             ('speaker_l_led', SPK_L_LED), ('speaker_r_led', SPK_R_LED)):
    cv.masks[k] = m
for k, m in THINGS.items():
    cv.masks[k] = m
