# 02 floor: the 55 new rows below. The floor plane (Y -141) toward us, and what stands on it carried down to it: the
# bed's front-right leg to its foot (the bed's front is at Z 144, so the floor under it is at y ~310), the dark under
# the bed and the bed's shadow in front of it, the bolster's end cap (an ellipse cut in half by the old bottom edge),
# the bookshelf's plinth and the closet's foot above their floor line. The light is the same light: the CRT's cone is
# re-traced on the new rows by 07_light's own functions, and the window's light from behind throws the bed's and the
# bolster's shadows toward us and to the left (the line bounding the lit floor under the bed is that shadow's edge).
B0 = TOP + ROOM.h - 1                          # the last old row
NEW = YY > B0

# ---- the floor's own inks: the room's FLOOR, the darker SLATE floor by the desk and bookshelf (its edge leans out
# toward us as the old one does)
cv.fill(NEW, FLOOR)
SL_EDGE = 382 + (YY - B0) * 0.6
PEN = np.maximum(2 + (YY - B0) * 0.2, 1)                     # the desk's shadow: its penumbra widens with distance
cv.grad(NEW & (XX >= SL_EDGE - PEN), FLOOR, SLATE, (XX - SL_EDGE + PEN) / PEN)

# ---- the bookshelf and closet foot: their front plane meets the floor along a line to the VP through (452, B0-1)
FL = lambda x: (B0 - 1) + (x - 452) * (VP[1] - (B0 - 1)) / (VP[0] - 452)
FOOT = NEW & (YY < FL(XX)) & (XX >= 440)
clone_from(FOOT, OLD & (YY >= B0 - 12), 0, -8)                 # the upright, the closet door: vertical grain
cv.fill(FOOT & (XX < 462) & (YY >= FL(XX) - 3), DARK)           # the plinth under the bottom shelf
cv.fill(FOOT & (XX >= 470) & (YY >= FL(XX) - 3), WOOD)          # the closet's sill
cv.fill(cv.m_edge(FOOT, 'bottom', inside=True), BLACK)
cv.fill(cv.m_edge(FOOT, 'bottom', inside=False) & NEW, DARK)    # contact shadow on the floor

# ---- the bed: the under-bed dark, its edge the window's shadow line, carried on in front of the bed as its shadow
SH_EDGE = 71 - (YY - B0) / 0.58
UNDER = NEW & (XX < SH_EDGE)
cv.fill(UNDER & (YY <= 306), BLACK)
cv.tile(UNDER & (YY > 306) & (YY <= 311), '1/2', BLACK, DARK)
cv.fill(UNDER & (YY > 311), DARK)
cv.tile(NEW & (XX >= SH_EDGE) & (XX < SH_EDGE + 2) & (YY > 311), '1/2', DARK, SLATE)
cv.fill(NEW & (XX >= SH_EDGE) & (XX < SH_EDGE + 2) & (YY <= 311), SLATE)
# the floor under the bed toward the leg, as the old rows have it: a SLATE band at the shadow's edge
cv.fill(NEW & (YY <= 309) & (XX >= SH_EDGE + 2) & (XX < SH_EDGE + 8), SLATE)
# the leg: found in the last old row by its pattern, carried down to its foot at the floor
_row = ''.join('0123456789abcdef'[v] for v in cv.idx[B0])
LEG_X0 = _row.index('f889f961008f')
LEG_X1 = LEG_X0 + 11
LEG_FOOT = 310
for y in range(B0 + 1, LEG_FOOT + 1):
    cv.idx[y, LEG_X0:LEG_X1 + 1] = cv.idx[B0, LEG_X0:LEG_X1 + 1]
cv.fill(cv.m_rect(LEG_X0, LEG_FOOT, LEG_X1, LEG_FOOT), BLACK)  # its foot
cv.tile(cv.m_rect(LEG_X0 - 4, LEG_FOOT + 1, LEG_X1 - 2, LEG_FOOT + 1), '1/2', SLATE, DARK)   # and its shadow, left

# ---- the bolster's end cap: the ellipse's top half is in the old rows; the bottom half mirrors it (the seam and
# piping included), a step darker as it turns down and away from the window's light
CAP_C, CAP_R = (206, B0), (16.5, 20.5)
CAP = cv.m_ellipse(CAP_C[0], CAP_C[1], *CAP_R) & NEW
for y, x in zip(*np.nonzero(CAP)):
    cv.idx[y, x] = cv.idx[2 * B0 - y, x]
DARKER = {GLOW: PAPER, PAPER: CURTAIN, CURTAIN: WALL, WALL: WALL_SHADE, DESK: DESK_SHADE, DESK_SHADE: RED,
          RED: WOOD, BEDSPREAD: WOOD}                          # one step down each ink's own ramp
cv.relight(CAP & (YY > B0 + 10), np.full((cv.h, cv.w), 1.0), DARKER)
cv.fill(cv.m_edge(CAP, 'bottom,left,right', inside=True) & ~cv.m_edge(CAP, 'top', inside=True), BLACK)
# the body's lower outline, down to where it meets the cap, and the red cloth inside it
BODY_OUT = lambda y: 189 + (y - B0) / 1.84
BOD = NEW & (XX > BODY_OUT(YY)) & (XX < CAP_C[0]) & ~CAP & (YY <= B0 + 6)
for y, x in zip(*np.nonzero(BOD)):
    cv.idx[y, x] = cv.idx[B0, min(x - int((y - B0) * 0.54), cv.w - 1)]
cv.fill(NEW & (np.abs(XX - BODY_OUT(YY)) < 0.6) & (YY <= B0 + 6), BLACK)
# its shadow on the floor, left and toward us, as the old rows' SLATE band along it
BOLSTER = CAP | BOD
SHAD = NEW & (cv.dist_from(BOLSTER, 8) <= 6) & ~BOLSTER & (XX < CAP_C[0] + 4) & (YY > CAP_C[1] + 2) \
       | NEW & (XX <= BODY_OUT(YY)) & (XX > BODY_OUT(YY) - 7) & (YY <= B0 + 8)
cv.replace(FLOOR, SLATE, SHAD)

# ---- the CRT's cone, re-traced by 07_light on a grid that covers the new rows (mahou-pc's coordinates), at the old
# cone's own reference: the same light, continued toward us
_xs, _ys = M['xs'], M['ys']
M['xs'], M['ys'] = XX.astype(float), (YY - TOP).astype(float)
LIT_FLOOR = NEW & cv.m_where(FLOOR, SLATE, DARK) & ~FOOT
E_NEW = M['irradiance'](M['on_plane_y'](-141), (0, 1, 0), LIT_FLOOR, desk=False)
M['xs'], M['ys'] = _xs, _ys
_Ef = M['E']['floor']
CONE_REF = float(np.percentile(_Ef[_Ef > 0], 97))
# Strength is chosen: traced as is, the floor toward us faces the glass and past the stool's shadow a second lobe
# opens up, a bright puddle across the bottom that outshone the phone. So the new rows keep to the old cone's own fan
# (from the CRT's foot on the floor, through the old cone's extent in the last old row) and fade toward us, a halving
# every 14 rows, which leaves the seam's bands as they are and lets the cone die out before the frame's edge.
_lit_last = np.nonzero((cv.idx[B0 - 3:B0 + 1] == GLOW).any(0) & (XX[0] > 280) & (XX[0] < 440))[0]
APEX = proj(M['MC'][0], -141, M['MC'][1])
_l, _r = _lit_last.min() - 2, _lit_last.max() + 2
_ang = np.arctan2(YY - APEX[1], XX - APEX[0])
FAN = (_ang >= np.arctan2(B0 - APEX[1], _r - APEX[0])) & (_ang <= np.arctan2(B0 - APEX[1], _l - APEX[0]))
E_FADE = E_NEW * FAN * 2.0 ** (-(YY - B0) / 14.0)
cv.relight(LIT_FLOOR, M['steps'](E_FADE, 0.75, 0.4, at=CONE_REF), {DARK: SLATE, SLATE: FLOOR, FLOOR: GLOW},
           tile_on={FLOOR, SLATE, DARK})
