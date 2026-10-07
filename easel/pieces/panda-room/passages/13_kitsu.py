# 13 the tapes (Kitsu): three anime VHS sleeves stacked on the floor right of the console, in front of the TV's
# board, as if just taken off it. Square to the room (lying things you tidy square up; askew ones read as diamonds
# on this camera), spines to us, a little shuffled. The TV behind lights the top cover and rims the back edges; the
# spines face away from it, so they are dark, and the middle one is bright by its own colour: a pale, cute sleeve
# with a red heart. The side facing the window is a step lighter than the front (the picture's rule).
KT_X0, KT_W, KT_Z0, KT_D, KT_T = 127.5, 19.5, 130.5, 10.5, 2.5      # a VHS sleeve: 19.5 x 10.5 x 2.5 cm
# (at Z 128 its back top edge sat on the board's bottom edge, at 131.5 two px under its top: both tangencies; at
# 130.5 it splits the board's front face)
KT_SHIFT = [(0.0, 0.0), (2.2, -0.7), (-1.4, 0.9)]                    # each sleeve's (dX, dZ): a stack, not a box
# (spine, side, its label ink, the label's mark) per sleeve, bottom to top
KT_INKS = [(SLATE, WALL_SHADE, DESK, DESK_SHADE), (PAPER, CURTAIN, RED, DESK_SHADE), (DESK_SHADE, DESK, WALL, RED)]


def kt(i, x, y, z):
    """A point of sleeve i: x 0..1 across, y 0..1 up its thickness, z 0..1 back from its spine."""
    dx, dz = KT_SHIFT[i]
    return pf((KT_X0 + dx + x * KT_W, FLOOR_Y + (i + y) * KT_T, KT_Z0 + dz + z * KT_D))


def kt_face(i, which):
    if which == 'front':
        return cv.m_poly([kt(i, 0, 1, 0), kt(i, 1, 1, 0), kt(i, 1, 0, 0), kt(i, 0, 0, 0)])
    if which == 'left':
        return cv.m_poly([kt(i, 0, 1, 0), kt(i, 0, 1, 1), kt(i, 0, 0, 1), kt(i, 0, 0, 0)])
    return cv.m_poly([kt(i, 0, 1, 0), kt(i, 1, 1, 0), kt(i, 1, 1, 1), kt(i, 0, 1, 1)])     # top


KITSU = np.zeros((cv.h, cv.w), bool)
KT_FRONT = []
for _i in range(3):
    _sp, _sd, _lab, _mk = KT_INKS[_i]
    _f, _l, _t = kt_face(_i, 'front'), kt_face(_i, 'left'), kt_face(_i, 'top')
    cv.fill(_t, WALL_SHADE)                                  # a lower sleeve's top shows only as a sliver
    cv.fill(_l, _sd)
    cv.fill(_f, _sp)
    KITSU |= _f | _l | _t
    KT_FRONT.append(_f)

# the top sleeve's cover, lying face up: a dark sleeve, an inset picture (a red-haired girl, her head turned
# sideways as the sleeve lies: hair to the right, her face and one big eye to its left) over a gold title band. It
# stays below the bright spine in value: the TV behind only rims its far edge.
_top = kt_face(2, 'top')
_art = cv.m_poly([kt(2, 0.28, 1, 0.22), kt(2, 0.86, 1, 0.22), kt(2, 0.86, 1, 0.84), kt(2, 0.28, 1, 0.84)])
cv.fill(_top, DARK)
cv.fill(_art, WALL)
_hx, _hy = kt(2, 0.66, 1, 0.55)
cv.fill(cv.m_ellipse(_hx, _hy, 3.6, 2.6) & _art, RED)                   # her hair
cv.fill(cv.m_ellipse(_hx - 3.0, _hy + 0.4, 2.0, 1.6) & _art, DESK)      # her face
cv.dots([(round(_hx - 3.5), round(_hy)), (round(_hx - 3.5), round(_hy) + 1)], BLACK)    # one big eye
cv.fill(cv.m_poly([kt(2, 0.08, 1, 0.30), kt(2, 0.20, 1, 0.30), kt(2, 0.20, 1, 0.76), kt(2, 0.08, 1, 0.76)]), BEDSPREAD)
cv.fill(cv.m_edge(_art, 'all'), BLACK)

# the spines: a title in 1px clusters, a logo block, and on the bright one a red heart
for _i in range(3):
    _sp, _sd, _lab, _mk = KT_INKS[_i]
    _yy = kt(_i, 0, 0.5, 0)[1]
    _x0, _x1 = kt(_i, 0.10, 0.5, 0)[0], kt(_i, 0.66, 0.5, 0)[0]
    for _x in range(round(_x0), round(_x1) + 1):
        if (_x * 5 + _i) % 7 not in (0, 4):
            cv.dot(_x, round(_yy), _lab)
    _lx = round(kt(_i, 0.80, 0.5, 0)[0])
    cv.dots([(_lx, round(_yy)), (_lx + 1, round(_yy))], _mk)
_hx, _hy = round(kt(1, 0.86, 0.5, 0)[0]), round(kt(1, 0, 0.5, 0)[1])
cv.dots([(_hx - 1, _hy - 1), (_hx + 1, _hy - 1), (_hx - 1, _hy), (_hx, _hy), (_hx + 1, _hy), (_hx, _hy + 1)], RED)

# line art: the stack's silhouette, the seams between sleeves, the vertical corner of each sleeve
cv.fill(cv.m_edge(KITSU, 'all'), BLACK)
for _i in (1, 2):
    cv.polyline([kt(_i, 0, 0, 0), kt(_i, 1, 0, 0)], BLACK)
    cv.polyline([kt(_i, 0, 0, 0), kt(_i, 0, 0, 1)], BLACK)
# light: the TV behind rims the top cover's back edge and the right ends of the sleeves' tops; the window's side
# catches the moon along its top edge
cv.polyline([kt(2, 0.03, 1, 1), kt(2, 0.97, 1, 1)], GLOW)

# seated on the floor: a contact shadow under the front and the right, a step darker than the floor
_flo = {FLOOR: DARK, SLATE: DARK, GLOW: FLOOR, CURTAIN: FLOOR}
_foot = (np.roll(KITSU, 1, 0) | np.roll(KITSU, 1, 1) | np.roll(np.roll(KITSU, 1, 1), 1, 0)) & ~KITSU
_foot &= (_ys - 0.5 > kt(0, 0, 0, 1)[1])
for _a, _c in _flo.items():
    cv.replace(_a, _c, _foot)
cv.masks['kitsu'] = KITSU

# vp-check: square to the room. Spines level, ends plumb, the side and the top to the VP.
cv.persp.edge('tapes', kt(0, 0, 0, 0), kt(0, 1, 0, 0), 'h')
cv.persp.edge('tapes', kt(2, 0, 1, 0), kt(2, 1, 1, 0), 'h')
cv.persp.edge('tapes', kt(1, 1, 0, 0), kt(1, 1, 1, 0), 'v')
cv.persp.edge('tapes', kt(2, 0, 1, 0), kt(2, 0, 1, 1))
cv.persp.edge('tapes', kt(2, 1, 1, 0), kt(2, 1, 1, 1))
cv.persp.edge('tapes', kt(0, 0, 0, 0), kt(0, 0, 0, 1))
