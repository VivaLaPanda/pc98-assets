# 06 the kotatsu (Panda's: "my kotatsu has a blanket on it"): a 105x75cm table, 40cm high, where the coffee table
# stood, its quilt (195x165cm) laid over the frame under the top board, rounding over the edges, falling with a little
# flare and spreading on the floor. The quilt is warm orange with a dark-red border band at its hem and a cream lattice
# of diamonds (the print follows the drape: it is painted in the quilt's own coordinates), shaded from the window side.
# A blue rug under it, in the bedroom carpet's ink.
KT_C = np.array([-5.0, 0.0, 188.0])                    # the table's centre on the floor (X, -, Z)
KT_HW, KT_HD, KT_H = 52.5, 37.5, 40.0
QW, QD = 97.5, 82.5                                  # the quilt's half sizes
TOP_Y = FLOOR_Y + KT_H - 3.0                           # the quilt's top surface, under the board


def quilt_point(cx, cz):
    """The quilt's 3D point for its own coordinates (cm from its centre): over the board's frame, round over the edge
    (a thick quilt), falling in soft folds that deepen toward the floor, its spare cloth flaring out at the corners."""
    ex = np.abs(cx) - KT_HW
    ez = np.abs(cz) - KT_HD
    e = np.maximum(np.maximum(ex, ez), 0.0)             # cloth beyond the table's edge
    corner = np.clip(np.minimum(ex, ez), 0, None)       # cloth beyond both edges: the corner's spare
    wx = np.clip(ex + 8, 0, None); wz = np.clip(ez + 8, 0, None)
    dx = np.sign(cx) * wx; dz = np.sign(cz) * wz
    nrm = np.maximum(np.hypot(dx, dz), 1e-6)
    dx, dz = dx / nrm, dz / nrm
    r = 8.0
    drop_h = TOP_Y - FLOOR_Y
    sh = np.minimum(e, r * np.pi / 2)
    ang = sh / r
    out = r * np.sin(ang)
    down = r * (1 - np.cos(ang))
    fall = np.clip(e - r * np.pi / 2, 0, drop_h - r)
    ff = fall / (drop_h - r)                            # 0 at the shoulder .. 1 at the floor
    out = out + 0.22 * fall + 3.0 * ff ** 2
    down = down + fall
    rest = np.clip(e - r * np.pi / 2 - (drop_h - r), 0, None)
    out = out + rest * 0.8 + corner * 0.3             # the corners flare into points on the floor
    # folds: along each side, every ~28cm, deeper toward the floor (and out on the floor)
    along = np.where(ex >= ez, cz, cx)
    fold = np.sin(along * 2 * np.pi / 28.0 + 0.7) * (2.2 * ff + 0.08 * np.clip(rest, 0, 15))
    out = out + fold
    X = np.where(e > 0, np.clip(cx, -KT_HW, KT_HW), cx) + dx * out
    Z = np.where(e > 0, np.clip(cz, -KT_HD, KT_HD), cz) + dz * out
    Y = TOP_Y - down
    Y = Y + 2.5 * np.exp(-((rest - 4) / 3.0) ** 2) * (rest > 0)    # a soft roll where it meets the floor
    Y = np.maximum(Y, FLOOR_Y + 0.4)
    return np.stack([KT_C[0] + X, Y, KT_C[2] + Z], -1)


_g = 2.0
_cx, _cz = np.meshgrid(np.arange(-QW, QW + 0.01, _g), np.arange(-QD, QD + 0.01, _g))
KQ = Surf()
raster_grid(KQ, quilt_point(_cx, _cz), _cx, _cz, 1)
QUILT = KQ.mask()

# ---- the rug first (under everything): big enough to cover where the armchairs and the coffee table stood (Fermion's
# own boards show all round it). A cream field in a soft woven check, a border in the bedroom carpet's blue between two
# rows of the quilt's red, and a short fringe at its near end. Painted in its own coordinates, so it lies flat.
_fx, _fz = on_floor(XX, np.maximum(YY, VP[1] + 1))
_rx0, _rx1, _rz0, _rz1 = -160, 112, 96, 248
RUG = (YY > VP[1] + 2) & (_fx > _rx0) & (_fx < _rx1) & (_fz > _rz0) & (_fz < _rz1)
_ru, _rv = _fx - _rx0, _fz - _rz0
_bd = np.minimum.reduce([_fx - _rx0, _rx1 - _fx, _fz - _rz0, _rz1 - _fz])
_rug_ctx = occluded(np.where(RUG, _fz - 0.5, np.inf))
_rug_ctx.__enter__()
cv.fill(RUG, DESK)
_check = ((np.floor(_ru / 9) + np.floor(_rv / 9)) % 2 == 0)
cv.tile(RUG & _check, '1/4', DESK, PAPER)                # the weave's soft check
cv.fill(RUG & (_bd < 22), FLOOR)                        # the border
cv.tile(RUG & (_bd < 22) & (_bd >= 19), '1/2', FLOOR, GLOW)
_band = (_bd < 18) & (_bd >= 6)
_diam = (np.abs(((np.maximum(_ru, _rv) + 6) % 12) - 6) + np.abs((np.minimum(_bd, 18) - 12))) < 3.2
cv.fill(RUG & _band & _diam, DESK)                      # a row of cream diamonds along it
cv.fill(RUG & (((_bd < 24) & (_bd >= 22)) | ((_bd < 6) & (_bd >= 4))), RED)
cv.fill(RUG & (_bd < 1.4), WOOD)                        # its edge on the boards
_fr = (YY > VP[1] + 2) & (_fx > _rx0 + 4) & (_fx < _rx1 - 4) & (_fz > _rz0 - 7) & (_fz <= _rz0)
cv.fill(_fr & ((XX % 2) == 0), PAPER)                   # the fringe
_rug_ctx.__exit__(None, None, None)
cv.masks['rug'] = RUG
_q_ctx = occluded(KQ.depth)
_q_ctx.__enter__()

# ---- the quilt: print in its own coordinates, three values by facing
_u, _v = KQ.u, KQ.v
_edge = np.minimum(QW - np.abs(_u), QD - np.abs(_v))   # cm from the quilt's hem
BORDER = QUILT & (_edge < 9)
# a plaid: red bands every 26cm each way (3.5cm wide), a cream line beside each, where they cross a deeper red
_bu = np.abs(((_u + 13) % 26) - 13) < 1.8
_bv = np.abs(((_v + 13) % 26) - 13) < 1.8
_lu = np.abs(((_u + 13) % 26) - 13 - 3.4) < 0.6
_lv_ = np.abs(((_v + 13) % 26) - 13 - 3.4) < 0.6
MOTIF = QUILT & ~BORDER & (_lu | _lv_)
PLAID = QUILT & ~BORDER & (_bu | _bv) & ~MOTIF
LINE = QUILT & ~BORDER & ((np.abs(_edge - 10.5) < 0.8))  # a cream piping inside the border
lit = lambert(KQ, L=(0.75, 0.62, -0.22))
# smooth the facets: a masked 5x5 box blur of the light (the grid's flat quads band otherwise)
_k = np.ones(5) / 5
_num = np.apply_along_axis(lambda r: np.convolve(r, _k, 'same'), 1, lit * QUILT)
_num = np.apply_along_axis(lambda c: np.convolve(c, _k, 'same'), 0, _num)
_den = np.apply_along_axis(lambda r: np.convolve(r, _k, 'same'), 1, QUILT.astype(float))
_den = np.apply_along_axis(lambda c: np.convolve(c, _k, 'same'), 0, _den)
lit = np.where(QUILT, _num / np.maximum(_den, 1e-6), 0)
# base inks per colour: (light, mid, shade, deep)
KT_ORANGE = (DESK, BEDSPREAD, DESK_SHADE, WOOD)
KT_RED = (DESK_SHADE, RED, WOOD, BLACK)
KT_CREAM = (PAPER, DESK, DESK, DESK_SHADE)


def shade(mask, ramp, level):
    """level 0 (deep) .. 3 (light) in tile bands between neighbours."""
    l = np.clip(level, 0, 3)
    a = np.floor(l).astype(int); f = l - a
    for k in range(3):
        sel = mask & (a == k)
        cv.grad(sel, ramp[3 - k], ramp[2 - k], f)
    cv.fill(mask & (a >= 3), ramp[0])


_lv = 0.6 + 2.5 * lit                                  # light: 0.6 (away) .. 3.1 (toward the glass)
shade(QUILT & ~BORDER & ~MOTIF & ~LINE & ~PLAID, KT_ORANGE, _lv)
shade(PLAID, KT_RED, _lv + 0.4)
shade(BORDER, KT_RED, _lv)
shade(MOTIF, KT_CREAM, _lv)
shade(LINE, KT_CREAM, _lv)
# outline: the quilt's silhouette in its deep ink, black where it meets the floor
_ring = cv.m_edge(QUILT, 'all', inside=True)
cv.fill(_ring, WOOD)
cv.fill(_ring & (KQ.n[..., 1] < 0.3) & (YY > VP[1] + 60), BLACK)
_q_ctx.__exit__(None, None, None)
QUILT = _q_ctx.visible | (QUILT & (cv.idx != _q_ctx.before))
cv.masks['kotatsu_quilt'] = QUILT

# ---- the top board: 110x80cm honey wood, 3cm thick, lying on the quilt; its front and right edges show
_bx0, _bx1 = KT_C[0] - 55, KT_C[0] + 55
_bz0, _bz1 = KT_C[2] - 40, KT_C[2] + 40
_by1 = TOP_Y + 3.2
_top = [pf((_bx0, _by1, _bz0)), pf((_bx1, _by1, _bz0)), pf((_bx1, _by1, _bz1)), pf((_bx0, _by1, _bz1))]
_front = [pf((_bx0, _by1, _bz0)), pf((_bx1, _by1, _bz0)), pf((_bx1, TOP_Y, _bz0)), pf((_bx0, TOP_Y, _bz0))]
_right = [pf((_bx1, _by1, _bz0)), pf((_bx1, _by1, _bz1)), pf((_bx1, TOP_Y, _bz1)), pf((_bx1, TOP_Y, _bz0))]
KT_TOP = cv.m_poly(_top)
KT_FRONT = cv.m_poly(_front) & ~KT_TOP
KT_RIGHT = cv.m_poly(_right) & ~KT_TOP & ~KT_FRONT
KT_BOARD = KT_TOP | KT_FRONT | KT_RIGHT
_bd_depth = np.where(KT_TOP, plane_depth(*[np.array(p) for p in [(_bx0, _by1, _bz0), (_bx1, _by1, _bz0), (_bx1, _by1, _bz1)]]),
                     np.where(KT_FRONT | KT_RIGHT, _bz0, np.inf))
_b_ctx = occluded(_bd_depth - 3.0)
_b_ctx.__enter__()
# the top: honey grain along X, lighter toward the glass, a soft reflection of the window near its right end
_tx, _tz = on_floor(XX, np.maximum(YY, VP[1] + 1))
_t = np.clip(0.55 - (XX - pf((_bx0, _by1, _bz0))[0]) / 260.0, 0, 1)
cv.grad(KT_TOP, DESK, DESK_SHADE, _t)
_grain = ((YY % 4) == 1) & (((XX // 9) * 7 + YY * 3) % 5 < 3)                    # long broken grain lines
cv.fill(KT_TOP & _grain & (_t > 0.15), DESK_SHADE)
cv.fill(KT_FRONT, WOOD)
cv.fill(KT_FRONT & (YY == YY[KT_FRONT].min()), DESK_SHADE)                        # the lit arris
cv.fill(KT_RIGHT, DESK_SHADE)
cv.fill(cv.m_edge(KT_BOARD, 'all', inside=True), WOOD)
cv.fill(cv.m_edge(KT_BOARD, 'bottom', inside=False) & QUILT, WOOD)                # its shadow on the quilt
_b_ctx.__exit__(None, None, None)
cv.masks['kotatsu_board'] = KT_BOARD
cv.masks['kotatsu'] = QUILT | KT_BOARD
