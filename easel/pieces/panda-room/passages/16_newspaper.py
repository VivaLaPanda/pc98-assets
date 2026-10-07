# 16 the newspaper (Substack): round 4 puts it on the floor in the moonlight, right of the bolster, big (rank 4: just
# under the PC in size). On the desk it lay at a grazing angle and nobody found it; on the bed (round 3) it read, but
# small. A broadsheet folded in half, front page up, thrown down a little askew, its masthead at the far edge (the
# top of the page, upright to us). The moon's barred light lies across it like across the floor around it: the
# paper in a bar is the top of the moon's lavender ramp (PAPER), between bars a step down (CURTAIN), so it is the
# brightest thing on the floor without taking the PC's cyan. What names it at a glance: the pale sheet, the dark
# masthead band across its top, the headline bar, the column rules, a photo; the print is laid after the light.
NW_C, NW_DEG, NW_L, NW_D = np.array([12.0, 140.0]), -6, 42.0, 29.0      # centre (X, Z) on the floor, size (cm)
NW_Y = FLOOR_Y + 0.3
_th = np.radians(NW_DEG)
NW_U = np.array([np.cos(_th), np.sin(_th)])           # across the page, left to right
NW_V = np.array([-np.sin(_th), np.cos(_th)])          # up the page: 0 the fold toward us, 1 the masthead's edge


def nw(u, v):
    X, Z = NW_C + (u - 0.5) * NW_L * NW_U + (v - 0.5) * NW_D * NW_V
    return pf((X, NW_Y, Z))


NW_TOP = cv.m_poly([nw(0, 0), nw(1, 0), nw(1, 1), nw(0, 1)])
NEWS = NW_TOP | np.roll(NW_TOP, 1, 0)                 # the fold's thickness, toward us: one row
NW_IN = NW_TOP & ~cv.m_edge(NW_TOP)
# page-local (u, v) of every pixel, through the floor plane
_d = np.stack([_fx - NW_C[0], _fz - NW_C[1]], -1)
NW_PU, NW_PV = _d @ NW_U / NW_L + 0.5, _d @ NW_V / NW_D + 0.5

# the sheet in the moon's bars (the same trace as the floor's), the fold's edge a step down
NW_MOON = moon_lit(_fx, NW_Y, _fz) & ~bolster_blocks(_fx, np.full_like(_fx, NW_Y), _fz)
cv.fill(NEWS, CURTAIN)
cv.fill(NW_TOP & NW_MOON, PAPER)
cv.fill(NEWS & ~NW_TOP, WALL)

# print: one step under the paper's local ink, so it stays a pale sheet with grey print, not a dark form
_under = {PAPER: CURTAIN, CURTAIN: WALL}
_box = lambda u0, u1, v0, v1: NW_IN & (NW_PU >= u0) & (NW_PU < u1) & (NW_PV >= v0) & (NW_PV < v1)
NW_MAST = _box(0.04, 0.96, 0.78, 0.96)
cv.fill(NW_MAST, DARK)                                                       # the masthead band
_title = NW_MAST & (np.abs(NW_PV - 0.87) < 0.025) & (NW_PU > 0.20) & (NW_PU < 0.80)
cv.fill(_title & ((_xs.astype(int) * 3) % 5 < 2), PAPER)                    # its title: one sparse pale row
cv.fill(_box(0.04, 0.96, 0.735, 0.76), WALL)                                 # the rule under it
cv.fill(_box(0.05, 0.70, 0.60, 0.69), SLATE)                                 # the headline
cv.fill(_box(0.05, 0.70, 0.60, 0.69) & ((_xs.astype(int) % 13) == 6), CURTAIN)
for _u in (0.27, 0.51, 0.75):                                                # column rules
    cv.fill(NW_IN & (np.abs(NW_PU - _u) < 0.009) & (NW_PV > 0.06) & (NW_PV < 0.56), WALL)
NW_PHOTO = _box(0.53, 0.73, 0.20, 0.54)
cv.fill(NW_PHOTO, SLATE)                                                     # a photo: dark, a pale figure in it
cv.tile(NW_PHOTO & (NW_PV < 0.34), '1/2', SLATE, DARK)
cv.fill(NW_PHOTO & (np.abs(NW_PU - 0.62) < 0.02) & (NW_PV > 0.30) & (NW_PV < 0.48), CURTAIN)
_txt = NW_IN & (NW_PV > 0.07) & (NW_PV < 0.55) & ~NW_PHOTO & ((_ys.astype(int) % 2) == 1)
_txt &= ((_xs.astype(int) * 7 + _ys.astype(int) * 3) % 5 > 1)
_txt &= ~(np.abs(((NW_PU - 0.27) % 0.24) - 0.0) < 0.012)
for _a, _c in _under.items():
    cv.replace(_a, _c, _txt)

# line art: the silhouette (dark against the floor, as the tome's and the pad's)
cv.fill(cv.m_edge(NEWS, 'all'), BLACK)
cv.masks['newspaper'] = NEWS
print('newspaper area', int(NEWS.sum()))

# vp-check: lying askew on the floor, its edges run to its own VPs (on the horizon)
cv.persp.edge('newspaper', nw(0.02, 1), nw(0.98, 1), own_vp(*NW_U))         # the masthead's edge
cv.persp.edge('newspaper', nw(0.02, 0), nw(0.98, 0), own_vp(*NW_U))         # the fold
cv.persp.edge('newspaper', nw(0, 0.03), nw(0, 0.97), own_vp(*NW_V))         # the left edge
cv.persp.edge('newspaper', nw(1, 0.03), nw(1, 0.97), own_vp(*NW_V))         # the right edge
