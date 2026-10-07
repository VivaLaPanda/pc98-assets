# 17 the phone (Signal / Discord, rank 2): round 4 makes it the second thing the eye finds. A phone can't grow much
# (a big 16.5 x 7.8cm one, moved forward on the bed from Z 178 to 156, right of the tome and clear of the mattress's
# front edge), so its light does the work: face up with a chat open, its screen the hottest ink on the bed, its glow
# laid on the sheets two steps up at its edge and gone by ~12cm. The hotspot is the phone and the pool lit a full
# step or more around it: that pool is what the eye sees as the phone from across the room.
P2_C, P2_DEG, P2_W, P2_L, P2_T = np.array([-104.0, 156.0]), 80, 7.8, 16.5, 0.9
_th = np.radians(P2_DEG)
P2_A = np.array([np.sin(_th), -np.cos(_th)])          # along the phone, toward its bottom (to our right)
P2_B = np.array([np.cos(_th), np.sin(_th)])           # across it


def p2(u, v, y=0.0):
    X, Z = P2_C + u * P2_B + v * P2_A
    return pf((X, BED_Y + y, Z))


def p2_rect(u0, v0, u1, v1, y=0.0):
    return [p2(u0, v0, y), p2(u1, v0, y), p2(u1, v1, y), p2(u0, v1, y)]


P2_TOP = cv.m_poly(p2_rect(-P2_W / 2, -P2_L / 2, P2_W / 2, P2_L / 2, P2_T))
P2_BODY = P2_TOP | np.roll(P2_TOP, 1, axis=0)         # its near side, one row
_Z = D * -BED_Y / np.maximum(_ys - VP[1], 1e-6)
_X = (_xs - VP[0]) * _Z / D
_d = np.stack([_X - P2_C[0], _Z - P2_C[1]], -1)
P2_U, P2_V = _d @ P2_B, _d @ P2_A
P2_GLASS = P2_TOP & (np.abs(P2_V) <= P2_L / 2 - 1.0) & ~cv.m_edge(P2_TOP)

# the pool first (the phone is painted over it): distance on the mattress from the phone's edge (cm), strength chosen
_du = np.maximum(np.abs(P2_U) - P2_W / 2, 0)
_dv = np.maximum(np.abs(P2_V) - P2_L / 2, 0)
P2_DIST = np.hypot(_du, _dv)
_bed = cv.m_rect(40, 225, 175, 272) & cv.m_where(BEDSPREAD, DESK, PAPER, RED, DESK_SHADE, CURTAIN, WOOD)
P2_CLOTH = _bed & ~P2_BODY & ~cv.masks['lesswrong'] & ~cv.masks['plush'] & (_ys - 0.5 < 271)
P2_LEVEL = np.clip(2.2 - P2_DIST / 5.5, 0, None)
_ramp = {k: v for k, v in LIT.items() if k not in (GLOW, SCREEN)}
_ramp[PAPER] = GLOW                                   # the cloth nearest the glass takes its cyan
cv.relight(P2_CLOTH, P2_LEVEL, _ramp, tile_on=(BEDSPREAD, DESK, RED, DESK_SHADE, WOOD))

# the phone: black body, its near side catching the spill, the glass with a chat (Signal's light theme): header,
# received bubbles at the left, sent ones (blue) at the right, the input bar
cv.fill(P2_BODY, BLACK)
cv.fill(P2_BODY & ~P2_TOP, SLATE)
cv.fill(P2_GLASS, SCREEN)
_v0 = -P2_L / 2 + 1.0
for (va, vb), (ua, ub), c in (((_v0, _v0 + 2.0), (-9, 9), GLOW),
                              ((_v0 + 3.6, _v0 + 4.8), (-9, 0.6), GLOW),
                              ((_v0 + 6.2, _v0 + 7.6), (-0.8, 9), FLOOR),
                              ((_v0 + 9.0, _v0 + 10.2), (-9, 1.2), GLOW),
                              ((_v0 + 11.2, _v0 + 12.6), (0.2, 9), FLOOR)):
    cv.fill(P2_GLASS & (P2_V >= va) & (P2_V < vb) & (P2_U >= ua) & (P2_U < ub), c)
cv.fill(P2_GLASS & (P2_V > P2_L / 2 - 2.6), GLOW)                   # the input bar
P2_LIT = P2_CLOTH & (P2_LEVEL >= 1.0)
cv.masks['phone'] = P2_BODY | P2_LIT
print('phone body', int(P2_BODY.sum()), 'with its pool', int(cv.masks['phone'].sum()))

# vp-check: lying askew on the bed, its edges run to its own VPs (on the horizon)
_w, _l = P2_W / 2, P2_L / 2
cv.persp.edge('phone', p2(-_w, -_l, P2_T), p2(-_w, _l, P2_T), own_vp(*P2_A))     # its long sides
cv.persp.edge('phone', p2(_w, -_l, P2_T), p2(_w, _l, P2_T), own_vp(*P2_A))
cv.persp.edge('phone', p2(-_w, -_l, P2_T), p2(_w, -_l, P2_T), own_vp(*P2_B))     # its ends
cv.persp.edge('phone', p2(-_w, _l, P2_T), p2(_w, _l, P2_T), own_vp(*P2_B))
