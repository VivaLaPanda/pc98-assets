# 13 the tapes (Kitsu): two anime VHS sleeves lying on top of the TV (round 4: the three on the floor were bigger
# than rank 12 should be; tapes on a set is the period's own still life). Square to the set (and so to the room),
# spines to us, shuffled a little, their backs over the tube's taper. The lower one is the bright, cute sleeve: pale
# with a red heart. The upper one is dark, its cover face up: a small picture (a red-haired girl's head, sideways
# as the sleeve lies) and a gold title band. Light: the PC behind and above rims the far edge of the cover, the
# window's side (left) a step lighter than the spines (the picture's rule).
KT_X0, KT_W, KT_D, KT_T = 119.5, 19.5, 10.5, 2.5          # a VHS sleeve: 19.5 x 10.5 x 2.5 cm
KT_Y0 = TV_P0[1] + TV_H                                   # the set's top
KT_Z0 = TV_P0[2] + 0.4                                    # just behind its front edge
KT_SHIFT = [(0.0, 0.0), (-1.3, 0.6)]                     # each sleeve's (dX, dZ)
# (spine, side, its title ink, the label's mark) per sleeve, bottom to top
KT_INKS = [(PAPER, CURTAIN, RED, DESK_SHADE), (DESK_SHADE, DESK, WALL, RED)]


def kt(i, x, y, z):
    """A point of sleeve i: x 0..1 across, y 0..1 up its thickness, z 0..1 back from its spine."""
    dx, dz = KT_SHIFT[i]
    return pf((KT_X0 + dx + x * KT_W, KT_Y0 + (i + y) * KT_T, KT_Z0 + dz + z * KT_D))


def kt_face(i, which):
    if which == 'front':
        return cv.m_poly([kt(i, 0, 1, 0), kt(i, 1, 1, 0), kt(i, 1, 0, 0), kt(i, 0, 0, 0)])
    if which == 'left':
        return cv.m_poly([kt(i, 0, 1, 0), kt(i, 0, 1, 1), kt(i, 0, 0, 1), kt(i, 0, 0, 0)])
    return cv.m_poly([kt(i, 0, 1, 0), kt(i, 1, 1, 0), kt(i, 1, 1, 1), kt(i, 0, 1, 1)])     # top


KITSU = np.zeros((cv.h, cv.w), bool)
for _i in range(2):
    _sp, _sd, _lab, _mk = KT_INKS[_i]
    _f, _l, _t = kt_face(_i, 'front'), kt_face(_i, 'left'), kt_face(_i, 'top')
    cv.fill(_t, WALL_SHADE)
    cv.fill(_l, _sd)
    cv.fill(_f, _sp)
    KITSU |= _f | _l | _t

# the upper sleeve's cover, face up: dark, a small picture, a gold title band
_art = cv.m_poly([kt(1, 0.30, 1, 0.22), kt(1, 0.86, 1, 0.22), kt(1, 0.86, 1, 0.84), kt(1, 0.30, 1, 0.84)])
cv.fill(kt_face(1, 'top'), DARK)
cv.fill(_art, WALL)
_hx, _hy = kt(1, 0.66, 1, 0.55)
cv.fill(cv.m_ellipse(_hx, _hy, 3.0, 2.0) & _art, RED)                    # her hair
cv.fill(cv.m_ellipse(_hx - 2.5, _hy + 0.3, 1.6, 1.3) & _art, DESK)       # her face
cv.dot(round(_hx - 3), round(_hy), BLACK)                                 # one big eye
cv.fill(cv.m_poly([kt(1, 0.08, 1, 0.30), kt(1, 0.20, 1, 0.30), kt(1, 0.20, 1, 0.76), kt(1, 0.08, 1, 0.76)]), BEDSPREAD)
cv.fill(cv.m_edge(_art, 'all'), BLACK)

# the spines: a title in 1px clusters and a logo; on the bright one a red heart
for _i in range(2):
    _sp, _sd, _lab, _mk = KT_INKS[_i]
    _yy = round(kt(_i, 0, 0.5, 0)[1])
    for _x in range(round(kt(_i, 0.10, 0.5, 0)[0]), round(kt(_i, 0.62, 0.5, 0)[0]) + 1):
        if (_x * 5 + _i) % 7 not in (0, 4):
            cv.dot(_x, _yy, _lab)
    _lx = round(kt(_i, 0.74, 0.5, 0)[0])
    cv.dots([(_lx, _yy), (_lx + 1, _yy)], _mk)
_hx, _hy = round(kt(0, 0.88, 0.5, 0)[0]), round(kt(0, 0, 0.5, 0)[1])
cv.dots([(_hx - 1, _hy - 1), (_hx + 1, _hy - 1), (_hx - 1, _hy), (_hx, _hy), (_hx + 1, _hy), (_hx, _hy + 1)], RED)

# line art, then the light: the far edge of the cover rimmed by the PC behind and above
cv.fill(cv.m_edge(KITSU, 'all'), BLACK)
cv.polyline([kt(1, 0, 0, 0), kt(1, 1, 0, 0)], BLACK)
cv.polyline([kt(1, 0, 0, 0), kt(1, 0, 0, 1)], BLACK)
cv.polyline([kt(1, 0.04, 1, 1), kt(1, 0.96, 1, 1)], GLOW)
# its shadow on the set's top, to the right (away from the window): a step darker
_sh = np.roll(KITSU, 1, 1) & ~KITSU & cv.m_where(SLATE, DARK) & TV_TOP
cv.replace(SLATE, DARK, _sh)
cv.masks['kitsu'] = KITSU
cv.masks['tv'] &= ~KITSU
print('kitsu area', int(KITSU.sum()))

# vp-check: square to the set, so to the room. Spines level, ends plumb, the side and the top to the VP.
cv.persp.edge('tapes', kt(0, 0, 0, 0), kt(0, 1, 0, 0), 'h')
cv.persp.edge('tapes', kt(1, 0, 1, 0), kt(1, 1, 1, 0), 'h')
cv.persp.edge('tapes', kt(1, 0, 1, 0), kt(1, 0, 1, 1))
cv.persp.edge('tapes', kt(1, 1, 1, 0), kt(1, 1, 1, 1))
