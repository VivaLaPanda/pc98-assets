# 07 the TV, bigger: a 13" CRT on a low wooden board on the floor in front of the desk's knee space, between the
# trash can and the bookshelf (the only floor that's free at the PC's depth: nearer, this 103-degree camera blows a
# set up past the PC's size). Turned 15 degrees toward the bed. It's on, dim: a letterboxed film (Letterboxd) with a
# line of subtitles, its glow a small cool pool on the floor in front. Dark plastic in the room's shade: the top
# takes the PC's light from behind, the side facing the window a step lighter than the front (the picture's rule).
TV_A = np.radians(15)
TV_F = np.array([-np.sin(TV_A), 0., -np.cos(TV_A)])        # out of the screen
TV_R = np.array([np.cos(TV_A), 0., -np.sin(TV_A)])         # across the face, our left to right
TV_P0 = np.array([130., FLOOR_Y + 4, 155.])                # bottom centre of the face, on the board
TV_W, TV_H, TV_D1, TV_D2 = 32., 28., 12., 28.              # the bezel box is 12 deep, the tube's back bulges to 28


def pf(p):
    return (VP[0] + D * p[0] / p[2], VP[1] - D * p[1] / p[2])


def tv_p3(u, v, w=0.):
    """u 0..1 left to right across the face, v 0..1 top to bottom, w depth back from the face."""
    return TV_P0 + TV_R * (u - 0.5) * TV_W + np.array([0., (1 - v) * TV_H, 0.]) - TV_F * w


def tv_pt(u, v, w=0.):
    return pf(tv_p3(u, v, w))


def tv_quad(u0, v0, u1, v1, w=0.):
    return [tv_pt(u0, v0, w), tv_pt(u1, v0, w), tv_pt(u1, v1, w), tv_pt(u0, v1, w)]


TRASH = cv.m_poly([(365, 239), (369, 236), (382, 236), (387, 239), (387, 289), (382, 291), (369, 291), (365, 289)])
_keep = ~TRASH                                              # the can stands in front of the set's back corner

# -- the board: plain wood, room-aligned, its right edge on the bookshelf's front plane (X 150)
_y0, _y1 = FLOOR_Y, FLOOR_Y + 4
TV_BOARD_TOP = cv.m_poly([pf((112, _y1, 147)), pf((150, _y1, 147)), pf((150, _y1, 180)), pf((112, _y1, 180))])
TV_BOARD_FRONT = cv.m_poly([pf((112, _y1, 147)), pf((150, _y1, 147)), pf((150, _y0, 147)), pf((112, _y0, 147))])
TV_BOARD_LEFT = cv.m_poly([pf((112, _y1, 147)), pf((112, _y1, 180)), pf((112, _y0, 180)), pf((112, _y0, 147))])
TV_BOARD = (TV_BOARD_TOP | TV_BOARD_FRONT | TV_BOARD_LEFT) & _keep
cv.fill(TV_BOARD_TOP & _keep, DESK_SHADE)
cv.fill(TV_BOARD_LEFT & _keep, WOOD)
cv.fill(TV_BOARD_FRONT & _keep, WOOD)
cv.fill(cv.m_edge(TV_BOARD_TOP, 'top,left') & _keep, WOOD)
cv.fill(cv.m_edge(TV_BOARD, 'all') & _keep, BLACK)

# -- the tube's back, bulging out behind the bezel box (its top and the side toward the window show)
_b_top = cv.m_poly([tv_pt(0.10, 0.06, TV_D1), tv_pt(0.90, 0.06, TV_D1), tv_pt(0.78, 0.20, TV_D2), tv_pt(0.22, 0.20, TV_D2)])
_b_left = cv.m_poly([tv_pt(0.10, 0.06, TV_D1), tv_pt(0.22, 0.20, TV_D2), tv_pt(0.22, 0.86, TV_D2), tv_pt(0.10, 0.96, TV_D1)])
TV_BULGE = (_b_top | _b_left) & _keep
cv.fill(TV_BULGE, DARK)
cv.fill(cv.m_edge(_b_top, 'top') & _keep, SLATE)                     # the PC's light along its back
cv.fill(cv.m_edge(TV_BULGE, 'all') & _keep & ~cv.m_edge(_b_top, 'top'), BLACK)

# -- the bezel box: front, top, the side toward the window
TV_FRONT = cv.m_poly(tv_quad(0, 0, 1, 1))
TV_TOP = cv.m_poly([tv_pt(0, 0), tv_pt(1, 0), tv_pt(1, 0, TV_D1), tv_pt(0, 0, TV_D1)])
TV_LEFT = cv.m_poly([tv_pt(0, 0), tv_pt(0, 0, TV_D1), tv_pt(0, 1, TV_D1), tv_pt(0, 1)])
TV_BOX = (TV_FRONT | TV_TOP | TV_LEFT) & _keep
cv.fill(TV_TOP & _keep, SLATE)                                        # three values: top, the side toward the
cv.fill(TV_LEFT & _keep, SLATE)                                       # window, the front toward us, darkest
cv.tile(TV_LEFT & _keep, '1/4', SLATE, DARK)
cv.fill(TV_FRONT, DARK)
cv.fill(cv.m_edge(TV_BOX, 'all') & _keep, BLACK)
cv.polyline([tv_pt(0, 0), tv_pt(1, 0)], BLACK)                       # the bezel's top and side edges, drawn
cv.polyline([tv_pt(0, 0), tv_pt(0, 1)], BLACK)
cv.polyline([tv_pt(0.02, 0.01, 0.5), tv_pt(0.98, 0.01, 0.5)], SLATE)   # its bevel, catching light along the top
cv.polyline([tv_pt(0, 0, 1), tv_pt(0, 0, TV_D1 - 1)], CURTAIN)          # the top-left edge, toward the window

# -- the screen: a rounded tube in a black ring, the film letterboxed in it
_S0, _S1 = (0.08, 0.08), (0.92, 0.74)                                 # tube corners on the face (u, v)


def tube(s, t):
    return tv_pt(_S0[0] + (_S1[0] - _S0[0]) * s, _S0[1] + (_S1[1] - _S0[1]) * t)


TV_TUBE = cv.m_poly([tube(0.03, 0), tube(0.97, 0), tube(1, 0.05), tube(1, 0.95), tube(0.97, 1), tube(0.03, 1),
                     tube(0, 0.95), tube(0, 0.05)])
cv.fill(TV_TUBE, BLACK)
_pic = cv.m_poly([tube(0.04, 0.2), tube(0.96, 0.2), tube(0.96, 0.8), tube(0.04, 0.8)])       # between the bars
_lt = cv.lin(tube(0.5, 0.2), tube(0.5, 0.8))                                                    # 0 top .. 1 bottom
cv.fill(_pic, FLOOR)                                                                             # a night sky
cv.tile(_pic & (_lt > 0.38), '1/2', FLOOR, GLOW)                                                 # dusk at the horizon
cv.tile(_pic & (_lt > 0.52), '1/4', GLOW, SCREEN)
_hz = [tube(0.04, 0.66), tube(0.18, 0.6), tube(0.3, 0.64), tube(0.46, 0.57), tube(0.6, 0.62), tube(0.75, 0.55),
       tube(0.96, 0.6), tube(0.96, 0.8), tube(0.04, 0.8)]                                        # hills against it
cv.fill(cv.m_poly(_hz) & _pic, BLACK)
for _s in (0.62, 0.67):                                                                            # two figures on them
    _x, _y = tube(_s, 0.6)
    cv.line(round(_x), round(_y) - 3, round(_x), round(_y), BLACK)
    cv.dot(round(_x), round(_y) - 4, BLACK)
_mx, _my = tube(0.2, 0.32)
cv.dot(round(_mx), round(_my), SCREEN)                                                           # a moon in the film
_sx0, _sy = tube(0.3, 0.9); _sx1, _ = tube(0.7, 0.9)                                              # a subtitle line
for _x in range(round(_sx0), round(_sx1) + 1):
    if (_x * 7) % 5 != 0:
        cv.dot(_x, round(_sy), PAPER)
_gx, _gy = tube(0.08, 0.08)                                                                       # the window, in the glass
cv.dots([(round(_gx) + 1, round(_gy) + 1), (round(_gx) + 2, round(_gy) + 1), (round(_gx) + 1, round(_gy) + 2)], CURTAIN)

# -- the control strip: speaker slots, three buttons, a lit power lamp; a badge on the top bezel
for _v in (0.80, 0.84, 0.88):
    cv.polyline([tv_pt(0.10, _v), tv_pt(0.42, _v)], BLACK)
for _u in (0.56, 0.63, 0.70):
    _x, _y = tv_pt(_u, 0.84)
    cv.dot(round(_x), round(_y), WALL_SHADE)
_x, _y = tv_pt(0.86, 0.84)
cv.dot(round(_x), round(_y), SCREEN); cv.dot(round(_x) + 1, round(_y), GLOW)
_x, _y = tv_pt(0.5, 0.035)
cv.dots([(round(_x) - 1, round(_y)), (round(_x), round(_y)), (round(_x) + 1, round(_y))], WALL_SHADE)

# -- its glow: a small cool pool on the floor in front of the face, strongest straight ahead
_c = TV_P0 + np.array([0., 0., 0.]) - TV_F * 0
_qx, _qz = _fx - _c[0], _fz - _c[2]
_dist = np.hypot(_qx, _qz)
_cos = (_qx * TV_F[0] + _qz * TV_F[2]) / np.maximum(_dist, 1e-6)
TV_POOL = cv.m_region(400, 330, inks=(FLOOR, SLATE, DARK), within=cv.m_rect(300, 296, 499, 356)) & (_cos > 0.35)
_lv = np.clip(_cos, 0, 1) * np.clip(1.2 - _dist / 45, 0, 1) * 1.1
cv.relight(TV_POOL & _keep & ~TV_BOARD, _lv, {DARK: SLATE, SLATE: FLOOR, FLOOR: GLOW}, tile_on={FLOOR, SLATE, DARK})

_x0, _y0 = tv_pt(0.15, 1.0); _x1, _ = tv_pt(0.85, 1.0)                # the screen's light on the board in front
cv.line(round(_x0), round(_y0) + 2, round(_x1), round(_y0) + 1, DESK)

cv.masks['tv'] = TV_BOARD | TV_BULGE | TV_BOX
