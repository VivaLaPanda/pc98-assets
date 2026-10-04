# 05 moonlight. Still night, better lit: a moon low in the sky beside the tower in the right pane, and its light
# coming in through the balcony door the way a PC-98 night scene shows it: the door's shape laid on the floor in
# pale tile bands, barred by the mullion and the balusters, the bolster lit along its top with a long shadow.
# The moon's light is lavender (the curtain's ramp); the computer keeps the cyan (glow, screen) to itself.

# -- palette: the room lifted a step toward a cool night (registers only; same pixels). Floor and bed keep their
#    colours: they carry the moonlight and the warm accent. (A greener lift, wall #568 and wood #434, read as dusk.)
MOON_LIFT = dict(paper='#78b', curtain='#67b', wall='#558', wall_shade='#457', wood='#324', dark='#225')   # black stays #112
for _n, _c in MOON_LIFT.items():
    cv.pal_set(cv.names[_n], _c)

# -- the moon: low over the city, between the tower and the right curtain (sky there: x 273-283, y 66-81)
MOON_C, MOON_R = (278, 72), 5
MOON_SKY = cv.m_rect(273, 66, 283, 81) | (cv.m_rect(258, 66, 283, 70) & cv.m_where(SLATE, BLACK))
_halo = cv.rad(MOON_C, MOON_R, MOON_R + 5)
with cv.only_over(BLACK):                                   # the haze's dark dither lifts around it
    cv.fill(MOON_SKY & (_halo < 0.5), SLATE)
MOON_DISK = cv.m_ellipse(*MOON_C, MOON_R, MOON_R) & MOON_SKY
cv.fill(MOON_DISK, SCREEN)
cv.fill(MOON_DISK & (cv.rad((MOON_C[0] + 1, MOON_C[1] - 1), 0, MOON_R) < 0.55), WHITE)   # the lit face
cv.dots([(276, 73), (277, 74), (280, 75), (275, 70)], GLOW)                                # maria
cv.fill(cv.m_edge(MOON_DISK, 'left,bottom'), GLOW)

# -- the light, traced. Moon direction (screen point at infinity -> world direction per unit of depth):
_mx, _my = MOON_C
MOON_L = ((_mx - VP[0]) / D, (VP[1] - _my) / D)              # dX/dZ, dY/dZ of a ray toward the moon
FLOOR_Y, WALL_Z, RAIL_Z = -141, 226, 306
DOOR_X = ((191 - VP[0]) * WALL_Z / D, (284 - VP[0]) * WALL_Z / D)    # the opening between the curtains
MULLION_X = ((234 - VP[0]) * WALL_Z / D, (240 - VP[0]) * WALL_Z / D)
SILL_H, RAIL_H = 2.0, 70.0
POST_X = [((x - VP[0]) * RAIL_Z / D, (x + 5 - VP[0]) * RAIL_Z / D) for x in M['POSTS']]
# the bolster: a cylinder on the floor (from its end cap's size and where its ends meet the floor)
BOL_A, BOL_B, BOL_R = np.array([-75., FLOOR_Y + 10, 193.]), np.array([-29., FLOOR_Y + 10, 137.]), 10.0


def moon_lit(X, Y, Z):
    """True where a ray from the point toward the moon gets out through the door: between the curtains, over the
    sill, past the mullion and the balusters."""
    s = WALL_Z - Z
    xd, hd = X + MOON_L[0] * s, (Y - FLOOR_Y) + MOON_L[1] * s
    ok = (xd > DOOR_X[0]) & (xd < DOOR_X[1]) & (hd > SILL_H) & ~((xd > MULLION_X[0]) & (xd < MULLION_X[1]))
    s = RAIL_Z - Z
    xr, hr = X + MOON_L[0] * s, (Y - FLOOR_Y) + MOON_L[1] * s
    for a, b in POST_X:
        ok &= ~((xr > a) & (xr < b) & (hr < RAIL_H))
    return ok


def bolster_blocks(X, Y, Z):
    """True where the ray toward the moon passes through the bolster."""
    ax = BOL_B - BOL_A
    L2 = ax @ ax
    hit = np.zeros(np.shape(X), bool)
    for h in np.arange(0, 2 * BOL_R + 0.1, 0.5):
        s = (h - (Y - FLOOR_Y)) / MOON_L[1]
        Q = np.stack([X + MOON_L[0] * s, Y + MOON_L[1] * s, Z + s], -1)
        t = np.clip(((Q - BOL_A) @ ax) / L2, 0, 1)
        d = np.linalg.norm(Q - (BOL_A + t[..., None] * ax), axis=-1)
        hit |= (s >= 0) & (d < BOL_R)
    return hit


_ys, _xs = np.mgrid[0:cv.h, 0:cv.w] + 0.5
_fz = D * -FLOOR_Y / np.maximum(_ys - VP[1], 1e-6)
_fx = (_xs - VP[0]) * _fz / D
MOON_FLOOR_AREA = cv.m_rect(90, 236, 320, cv.h - 1) & (_ys > VP[1] + 1)
_floor = cv.m_region(250, 300, inks=(FLOOR, SLATE, DARK), within=MOON_FLOOR_AREA)
MOON_ON_FLOOR = _floor & moon_lit(_fx, FLOOR_Y, _fz) & ~bolster_blocks(_fx, np.full_like(_fx, FLOOR_Y), _fz)
# strength (chosen): 3/4 of the lavender just inside the door, 1/2 across the room, 1/4 nearest us (full strength
# to the frame's edge pulled the eye off the window); the patch's edge a band lower
_lv = np.where(_fz > 185, 0.75, np.where(_fz > 138, 0.5, 0.25))
_edge = MOON_ON_FLOOR & ~(np.roll(MOON_ON_FLOOR, 1, 1) & np.roll(MOON_ON_FLOOR, -1, 1))
_lv = np.where(_edge, _lv - 0.25, _lv)
cv.relight(MOON_ON_FLOOR, _lv, {DARK: SLATE, SLATE: FLOOR, FLOOR: CURTAIN}, tile_on={FLOOR, SLATE, DARK})

# -- the bolster in it: its upper-right flank faces the moon (normals from the cylinder; only where the trace
#    reaches it: the far end is in the curtain's shadow, the near end in the mullion's)
MOON_RAMP = {DARK: SLATE, SLATE: FLOOR, FLOOR: CURTAIN, CURTAIN: PAPER, RED: DESK_SHADE, DESK_SHADE: DESK,
             BEDSPREAD: DESK, WOOD: DESK_SHADE, WALL_SHADE: WALL, WALL: PAPER}
_dirs = np.stack([(_xs - VP[0]) / D, -(_ys - VP[1]) / D, np.ones_like(_xs)], -1)
_ax = BOL_B - BOL_A; _len = np.linalg.norm(_ax); _a = _ax / _len
_dp = _dirs - (_dirs @ _a)[..., None] * _a
_wp = -BOL_A - (-BOL_A @ _a) * _a
_qa, _qb, _qc = (_dp * _dp).sum(-1), 2 * (_dp * _wp).sum(-1), _wp @ _wp - BOL_R ** 2
_disc = _qb * _qb - 4 * _qa * _qc
_t = (-_qb - np.sqrt(np.maximum(_disc, 0))) / (2 * _qa)
_P = _t[..., None] * _dirs
_u = (_P - BOL_A) @ _a
BOL_SIDE = (_disc > 0) & (_u >= 0) & (_u <= _len)
_n = (_P - BOL_A) - _u[..., None] * _a
_n /= np.maximum(np.linalg.norm(_n, axis=-1, keepdims=True), 1e-6)
_l = np.array([MOON_L[0], MOON_L[1], 1.0]); _l /= np.linalg.norm(_l)
_ndl = (_n @ _l) * BOL_SIDE
BOL_LIT = BOL_SIDE & moon_lit(_P[..., 0], _P[..., 1], _P[..., 2]) & (_ndl > 0.2)
_bol = BOL_LIT & ~cv.m_where(FLOOR, BLACK) & ~cv.m_edge(BOL_SIDE)       # its own inks, not the floor at its rim
cv.relight(_bol, np.clip((_ndl - 0.2) * 2.2, 0, 1.25), MOON_RAMP)
# the moon's rim along the lit flank's silhouette, where it meets the lit floor
_rim = cv.m_edge(BOL_SIDE, 'top,right') & BOL_LIT & ~cv.m_where(BLACK, FLOOR, CURTAIN, SLATE, DARK)
cv.fill(_rim, PAPER)

# -- the curtains, backlit: sheer cloth glows where it hangs against the glass, a half step up the curtain ramp,
#    the edge itself a step
_glass_l, _glass_r = cv.m_rect(186, 64, 190, 237), cv.m_rect(284, 64, 289, 233)
_cur = cv.m_where(CURTAIN, WALL, WALL_SHADE, PAPER)
for _g, _x0 in ((_glass_l, 190), (_glass_r, 284)):
    _d = np.abs(_xs - 0.5 - _x0)
    cv.relight_halves(_g & _cur, np.where(_d < 1.5, 1.0, 0.5), {WALL_SHADE: WALL, WALL: CURTAIN, CURTAIN: PAPER})

# -- the balcony deck outside takes the same light (a half step, between the balusters' shadows), so the floor's
#    bars visibly come in from out there
_dk = cv.m_rect(188, 207, 283, 231) & (_fz > WALL_Z) & (_fz < RAIL_Z)
_xr = _fx + MOON_L[0] * (RAIL_Z - _fz)
for _a, _b in POST_X:
    _dk &= ~((_xr > _a) & (_xr < _b))
cv.relight(_dk, 0.5, MOON_RAMP, tile_on={DARK, WOOD, SLATE})
