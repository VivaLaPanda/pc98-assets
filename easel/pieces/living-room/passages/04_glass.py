# 04 the balcony's sliding doors, in the bedroom's materials: their frames dark wood like the bedroom's balcony door,
# the curtain and the pleated valance in its pale-blue curtain stripes with the orange tabs. The glass becomes the
# outside: one layer per time of day (the same skyline the bedroom sees, past the same railing), so here it only gets
# a mask and a placeholder sky.
# Every line along the right wall runs to the VP: the ceiling (Fermion's cornice top), the valance's top and hem, the
# rolled blinds' foot, the floor track. Things on the wall that keep a size get it in perspective (scale `s`: 1 at the
# near edge, x 500), and repeats along it (pleats, the blinds' weave) are spaced by depth, not by pixels.
def vp_line(k):
    return lambda x: VP[1] + k * (np.asarray(x, float) - VP[0])


CEIL_R = vp_line(-0.645)                       # the ceiling along the right wall (the cornice's top edge, as drawn)
VAL_Y = vp_line(-0.534)                        # the valance's hem: 26px deep at the near edge, 15 at the corner
TUBE_Y = vp_line(-0.505)                       # the rolled-up blinds' foot (4px roll at the corner, 7 at the edge)
TRACK_Y = vp_line((240 - VP[1]) / (382 - VP[0]))   # the floor track, through the back wall's corner (382, 240)
WALL_S = lambda x: (np.asarray(x, float) - VP[0]) / (500 - VP[0])
PLEAT_K = 175.0 ** 2                           # depth units: one per px at x 440


def depth_cols(x0, x1, unit):
    """Columns x0..x1 cut into repeats of `unit` depth units (narrow far away): each column's index in its repeat,
    from 0 at its far edge, and whether it is the repeat's last (nearest) column."""
    xs = np.arange(x0, x1 + 1)
    u = -PLEAT_K / (xs - VP[0])
    k = np.floor(u / unit).astype(int)
    first = np.r_[True, k[1:] != k[:-1]]
    last = np.r_[k[1:] != k[:-1], True]
    pos = np.zeros(len(xs), int)
    for i in range(1, len(xs)):
        pos[i] = 0 if first[i] else pos[i - 1] + 1
    return dict(zip(xs.tolist(), zip(pos.tolist(), last.tolist())))


PANES = [(399, 424), (431, 471), (479, 499)]
GLASS = np.zeros((cv.h, cv.w), bool)
for x0, x1 in PANES:
    GLASS |= (XX >= x0) & (XX <= x1) & (YY > VAL_Y(XX) + 1) & (YY < TRACK_Y(XX) - 1)
MULLION = (XX >= 425) & (XX <= 430) | (XX >= 472) & (XX <= 478)
MULLION &= (YY > VAL_Y(XX)) & (YY < TRACK_Y(XX))
JAMB = (XX >= 397) & (XX <= 398) & (YY > VAL_Y(XX)) & (YY < TRACK_Y(XX))     # the frame beside the curtain
CURT = (XX >= 383) & (XX <= 396) & (YY > VAL_Y(XX)) & (YY < TRACK_Y(XX))
VALANCE = (XX >= 383) & (YY <= VAL_Y(XX)) & (YY >= CEIL_R(XX) - 0.5) & ~cv.m_poly(OBJ_POLY['ac'])

# frames: dark wood, a lit edge toward the room (the left side of each), a black line on the glass side
for m in (MULLION, JAMB):
    cv.fill(m, WOOD)
for x0, x1 in ((425, 430), (472, 478)):
    cv.fill(MULLION & (XX == x0), DESK_SHADE)
    cv.fill(MULLION & (XX == x1), BLACK)

# the curtain: stripes of the bedroom's pale blue, lit on its folds, a darker fold every 4px, the hem band in blue
_fold = (XX - 383) % 4
cv.fill(CURT, CURTAIN)
cv.fill(CURT & (_fold == 0), PAPER)
cv.fill(CURT & (_fold == 2), GLOW)
cv.fill(CURT & (XX == 396), FLOOR)
cv.fill(CURT & (YY > TRACK_Y(XX) - 12) & (YY < TRACK_Y(XX) - 8) & (_fold != 0), FLOOR)   # the hem band, as on the bedroom's
# the valance: pleats (light, mid, a lit crease, a shade line), wider as they come nearer, with the orange tabs along
# its top under the rod's box, like the bedroom curtains' heading
_vy = YY - CEIL_R(XX)                          # px below the ceiling
_vs = WALL_S(XX)
_pleat = np.full(XX.shape, -1)
_last = np.zeros(XX.shape, bool)
for _x, (_pos, _isl) in depth_cols(383, 499, 6.0).items():
    _pleat[:, _x] = _pos
    _last[:, _x] = _isl
cv.fill(VALANCE, CURTAIN)
cv.fill(VALANCE & (_pleat <= 1) & ~_last, PAPER)
cv.fill(VALANCE & _last, FLOOR)
cv.fill(VALANCE & np.roll(_last, -1, axis=1) & (_pleat >= 3), GLOW)
_tabs = VALANCE & (_vy < 5 * _vs)
cv.fill(_tabs, BEDSPREAD)
cv.fill(_tabs & (_pleat == 0), DESK)
cv.fill(VALANCE & (YY > VAL_Y(XX) - 1), FLOOR)                 # its hem line
cv.fill(VALANCE & (_vy < np.maximum(1, 1.5 * _vs)), WOOD)      # the rod's box above it, against the ceiling

# the roller blinds (Panda's Living Room Blinds over the two near panes, Dining Room Blinds over the far one), rolled
# up under the valance: a cream roll from the hem to TUBE_Y, lit on top, its underside a step darker, end caps, a
# pull cord. The site lowers each one's cloth from the roll to the real position.
BLIND_SPANS = {'blind_living': (399, 471), 'blind_dining': (479, 499)}
BLIND_TUBE = {}
for _k, (_x0, _x1) in BLIND_SPANS.items():
    _tube = (XX >= _x0 - 1) & (XX <= _x1 + 1) & (YY > VAL_Y(XX)) & (YY <= TUBE_Y(XX))
    _tf = (YY - VAL_Y(XX)) / np.maximum(TUBE_Y(XX) - VAL_Y(XX), 1e-6)   # 0 at the hem, 1 at the roll's foot
    cv.fill(_tube, DESK)
    cv.fill(_tube & (_tf <= 0.3), PAPER)                                  # the roll's lit top
    cv.tile(_tube & (_tf > 0.6) & (_tf <= 0.85), '1/2', DESK, DESK_SHADE)
    cv.fill(_tube & (_tf > 0.85), WOOD)                                    # the bar along its foot
    cv.fill(_tube & ((XX == _x0 - 1) | (XX == _x1 + 1)), WOOD)          # end caps
    _cx = _x1 - 3
    _cl = 12 * float(WALL_S(_cx))
    _cord = (XX == _cx) & (YY > TUBE_Y(_cx)) & (YY <= TUBE_Y(_cx) + _cl)
    cv.fill(_cord, SLATE)
    cv.fill((np.abs(XX - _cx) <= 1) & (np.abs(YY - (TUBE_Y(_cx) + _cl + 1)) < 1), WOOD)   # the cord's pull
    BLIND_TUBE[_k] = _tube | _cord | ((np.abs(XX - _cx) <= 1) & (np.abs(YY - (TUBE_Y(_cx) + _cl + 1)) < 1))
GLASS &= ~(BLIND_TUBE['blind_living'] | BLIND_TUBE['blind_dining'])
for _k, _m in BLIND_TUBE.items():
    cv.masks[_k] = _m
# the blinds' cloth, where it can come down: under its roll to the track, across its span (the export takes away what
# stands in front)
BLIND_CLOTH = {_k: (XX >= _x0) & (XX <= _x1) & (YY > TUBE_Y(XX)) & (YY < TRACK_Y(XX))
               for _k, (_x0, _x1) in BLIND_SPANS.items()}
BLIND_WEAVE = {_k: [int(_isl) for _x, (_pos, _isl) in sorted(depth_cols(_x0, _x1, 5.0).items())]
               for _k, (_x0, _x1) in BLIND_SPANS.items()}

# the glass: the outside's own layer at export; a pale placeholder sky here
cv.fill(GLASS, SCREEN)
cv.masks['outside'] = GLASS
