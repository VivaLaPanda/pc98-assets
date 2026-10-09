# 04 the balcony's sliding doors, in the bedroom's materials: their frames dark wood like the bedroom's balcony door,
# the curtain and the pleated valance in its pale-blue curtain stripes with the orange tabs. The glass becomes the
# outside: one layer per time of day (the same skyline the bedroom sees, past the same railing), so here it only gets
# a mask and a placeholder sky.
VAL_Y = lambda x: VP[1] - 0.481 * (np.asarray(x, float) - VP[0])            # the valance's lower edge (to the VP)
TRACK_Y = lambda x: 240 + (np.asarray(x, float) - 382) * (240 - VP[1]) / (382 - VP[0])
PANES = [(399, 424), (431, 471), (479, 499)]
GLASS = np.zeros((cv.h, cv.w), bool)
for x0, x1 in PANES:
    GLASS |= (XX >= x0) & (XX <= x1) & (YY > VAL_Y(XX) + 1) & (YY < TRACK_Y(XX) - 1)
MULLION = (XX >= 425) & (XX <= 430) | (XX >= 472) & (XX <= 478)
MULLION &= (YY > VAL_Y(XX)) & (YY < TRACK_Y(XX))
JAMB = (XX >= 397) & (XX <= 398) & (YY > VAL_Y(XX)) & (YY < TRACK_Y(XX))     # the frame beside the curtain
CURT = (XX >= 383) & (XX <= 396) & (YY > VAL_Y(XX)) & (YY < TRACK_Y(XX))
VALANCE = (XX >= 383) & (YY <= VAL_Y(XX)) & (YY > VAL_Y(XX) - 26) & ~cv.m_poly(OBJ_POLY['ac'])

# frames: dark wood, a lit edge toward the room (the left side of each), a black line on the glass side
for m in (MULLION, JAMB):
    cv.fill(m, WOOD)
for x0, x1 in ((425, 430), (472, 478)):
    cv.fill(MULLION & (XX == x0), DESK_SHADE)
    cv.fill(MULLION & (XX == x1), BLACK)

# the curtain: stripes of the bedroom's pale blue, lit on its folds, a darker fold every 4px, the hem band in blue
_cy = YY - VAL_Y(XX)
_fold = (XX - 383) % 4
cv.fill(CURT, CURTAIN)
cv.fill(CURT & (_fold == 0), PAPER)
cv.fill(CURT & (_fold == 2), GLOW)
cv.fill(CURT & (XX == 396), FLOOR)
cv.fill(CURT & (YY > TRACK_Y(XX) - 12) & (YY < TRACK_Y(XX) - 8) & (_fold != 0), FLOOR)   # the hem band, as on the bedroom's
# the valance: pleats (light, mid, shade) with the orange tabs along its top, like the bedroom curtains' heading
_p = np.floor((XX - 383) / 1.0).astype(int) % 6
cv.fill(VALANCE, CURTAIN)
cv.fill(VALANCE & (_p < 2), PAPER)
cv.fill(VALANCE & (_p == 4), GLOW)
cv.fill(VALANCE & (_p == 5), FLOOR)
cv.fill(VALANCE & (YY <= VAL_Y(XX) - 21), BEDSPREAD)
cv.fill(VALANCE & (YY <= VAL_Y(XX) - 21) & (_p == 0), DESK)
cv.fill(VALANCE & (YY > VAL_Y(XX) - 1), FLOOR)                 # its hem line
cv.fill(VALANCE & (YY <= VAL_Y(XX) - 25), WOOD)                 # the rod's box above it

# the glass: the outside's own layer at export; a pale placeholder sky here
cv.fill(GLASS, SCREEN)
cv.masks['outside'] = GLASS
