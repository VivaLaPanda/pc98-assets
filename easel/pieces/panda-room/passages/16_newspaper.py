# 16 the newspaper (Substack), moved to the bed (round 3: on the desk it lay at a grazing angle, a few pale sheets
# by the keyboard that nobody found). A broadsheet folded in half, front page up, thrown on the bedspread in front of
# the phone and to the right of the tome, its masthead at the far edge as if Panda had been reading it from the
# bed's foot. Built on the mattress plane (Y -113), turned -5 degrees (its long edges stay near the picture's
# horizontal: an askew rectangle reads as a diamond here). What names it at a glance, in this order: the pale sheet
# on the yellow, the dark masthead band across its top, the headline bar under it, the column rules, a photo.
# The phone's screen is just behind its right half: that corner of the paper takes the cyan.
NW_C, NW_DEG, NW_L, NW_D = np.array([-122.0, 157.5]), -5, 36.0, 22.0      # clear of the tome, the phone and
# the mattress's front edge by 3px each (at 32x20 on the phone's right it lay on the moonlit mauve: pale on pale)
_th = np.radians(NW_DEG)
NW_U = np.array([np.cos(_th), np.sin(_th)])           # across the page, left to right
NW_V = np.array([-np.sin(_th), np.cos(_th)])          # up the page: 0 the fold toward us, 1 the masthead's edge


def nw(u, v, h=0.6):
    X, Z = NW_C + (u - 0.5) * NW_L * NW_U + (v - 0.5) * NW_D * NW_V
    return pf((X, BED_Y + h, Z))


def nw_quad(u0, v0, u1, v1):
    return cv.m_poly([nw(u0, v0), nw(u1, v0), nw(u1, v1), nw(u0, v1)])


NW_TOP = nw_quad(0, 0, 1, 1)
NEWS = NW_TOP | np.roll(NW_TOP, 1, 0)                 # its folded thickness, toward us: one row
NW_TOP_IN = NW_TOP & ~cv.m_edge(NW_TOP)
# page-local (u, v) of every pixel, through the mattress plane
_Z = D * -BED_Y / np.maximum(_ys - VP[1], 1e-6)
_X = (_xs - VP[0]) * _Z / D
_d = np.stack([_X - NW_C[0], _Z - NW_C[1]], -1)
NW_PU, NW_PV = _d @ NW_U / NW_L + 0.5, _d @ NW_V / NW_D + 0.5

# its shadow on the bedspread, down and to the left (away from the phone and the window), like the tome's
_sh = (np.roll(np.roll(NEWS, 1, 0), -1, 1) | np.roll(NEWS, 1, 0)) & ~NEWS
cv.replace(BEDSPREAD, WOOD, _sh); cv.replace(DESK, BEDSPREAD, _sh); cv.replace(RED, WOOD, _sh)

# the sheet: paper, the fold's edge a step down, the phone's light on its far right
cv.fill(NEWS, PAPER)
cv.fill(NEWS & ~NW_TOP, CURTAIN)
_px, _py = M['ph'](0, 0, M['PH_T'])
_lit = NW_TOP_IN & (np.hypot(_xs - 0.5 - _px, _ys - 0.5 - (_py + TOP)) < 15)
cv.relight_halves(_lit, 1.0, {PAPER: GLOW})

# print (after the light): the masthead band, dark, with the title in pale clusters; a rule; the headline bar; the
# columns and their rules; a photo; text as rows of the ink one under the paper's
_in = lambda u0, u1, v0, v1: NW_TOP_IN & (NW_PU >= u0) & (NW_PU < u1) & (NW_PV >= v0) & (NW_PV < v1)
NW_MAST = _in(0.04, 0.96, 0.77, 0.97)
cv.fill(NW_MAST, DARK)
_title = NW_MAST & (np.abs(NW_PV - 0.87) < 0.022) & (NW_PU > 0.22) & (NW_PU < 0.78)
cv.fill(_title & ((_xs.astype(int) * 3) % 5 < 2), PAPER)                # the title: one sparse pale row, so the band
                                                                         # stays a dark bar (a fuller title read as dashes)
cv.fill(_in(0.04, 0.96, 0.725, 0.755), CURTAIN)                          # the rule under it
cv.fill(_in(0.06, 0.74, 0.60, 0.69), SLATE)                              # the headline
cv.fill(_in(0.06, 0.74, 0.60, 0.69) & ((_xs.astype(int) % 13) == 6), PAPER)  # a word gap or two
for _u in (0.27, 0.51, 0.75):                                            # column rules
    cv.fill(NW_TOP_IN & (np.abs(NW_PU - _u) < 0.011) & (NW_PV > 0.06) & (NW_PV < 0.55), WALL)
_photo = _in(0.53, 0.73, 0.20, 0.53)
cv.fill(_photo, SLATE)                                                   # a photo: dark, a pale figure in it
cv.tile(_photo & (NW_PV < 0.34), '1/2', SLATE, DARK)
cv.fill(_photo & (np.abs(NW_PU - 0.62) < 0.025) & (NW_PV > 0.30) & (NW_PV < 0.48), CURTAIN)
# text: three or four grey rows per column, broken into words, the paper showing between (a full grid read as a form)
_txt = NW_TOP_IN & (NW_PV > 0.07) & (NW_PV < 0.53) & ~_photo & ((_ys.astype(int) % 2) == 1)
_txt &= ((_xs.astype(int) * 7 + _ys.astype(int) * 3) % 5 > 1)
for _a, _c in {PAPER: CURTAIN, GLOW: PAPER}.items():
    cv.replace(_a, _c, _txt)

# line art last: the silhouette, and the fold's crease where the top turns down toward us
cv.fill(cv.m_edge(NEWS, 'all'), BLACK)
cv.masks['newspaper'] = NEWS

# vp-check: lying askew on the bed, its edges run to its own VPs (on the horizon)
cv.persp.edge('newspaper', nw(0, 1), nw(1, 1), own_vp(*NW_U))           # the masthead's edge
cv.persp.edge('newspaper', nw(0, 0), nw(1, 0), own_vp(*NW_U))           # the fold
cv.persp.edge('newspaper', nw(0, 0), nw(0, 1), own_vp(*NW_V))           # the left edge
cv.persp.edge('newspaper', nw(1, 0), nw(1, 1), own_vp(*NW_V))           # the right edge
