# 15 the map (Bump): a folded city map pinned flat to the back wall above the picture rail, over the desk: where
# Panda's friends are. Frontal (level and plumb, like the calendar under it). The folds make it paper: three
# panels across, the middle one turned away from the window a step darker, a crease across the middle. On it a
# street grid, a river running down into a bay, a highway in the map's yellow, and two bright pushpins marking
# friends; two dull pins hold its top corners. The CRT is below and to the right, so the sheet throws a 1px shadow
# up and to the left on the wall, and the pins' shadows fall the same way.
MP_X0, MP_Y0, MP_W, MP_H = 346, 23, 36, 24
MP_X1, MP_Y1 = MP_X0 + MP_W - 1, MP_Y0 + MP_H - 1
MAP = cv.m_rect(MP_X0, MP_Y0, MP_X1, MP_Y1)
_u, _v = _xs - 0.5 - MP_X0, _ys - 0.5 - MP_Y0                      # map-local pixel coordinates

_shadow = (np.roll(MAP, -1, 0) | np.roll(MAP, -1, 1) | np.roll(np.roll(MAP, -1, 0), -1, 1)) & ~MAP
for _a, _c in {WALL: WALL_SHADE, WALL_SHADE: DARK}.items():
    cv.replace(_a, _c, _shadow)

_in = MAP & ~cv.m_edge(MAP)
_dim = _in & (_u >= 12) & (_u < 24)                                  # the middle panel, turned from the window
_lit = _in & ~_dim
cv.fill(_lit, CURTAIN)
cv.fill(_dim, WALL)
# streets: a loose grid (not every block the same), lighter than the blocks
_st = _in & (np.isin(_v, (3, 8, 17, 21)) | np.isin(_u, (4, 9, 15, 20, 27, 31)))
cv.replace(CURTAIN, PAPER, _st)
cv.replace(WALL, CURTAIN, _st)
# the river, down from the top right into a bay at the bottom left
_rv = 4.0 + 12.0 * (1 - _u / 35.0) + 1.6 * np.sin(_u / 4.0)
_river = _in & (np.abs(_v - _rv) < 1.0)
_bay = _in & (((_u + 1) / 9.0) ** 2 + ((MP_H - 1 - _v) / 6.5) ** 2 < 1)
cv.fill(_river | _bay, FLOOR)
cv.fill(_bay & ~_river & (np.roll(_bay, -1, 0) & ~np.roll(_bay, 1, 0)), SLATE)   # the shore line, darker
# the highway, crossing the river on a bridge
cv.line(MP_X0 + 1, MP_Y0 + 6, MP_X1 - 1, MP_Y0 + 14, BEDSPREAD)
# the crease across the middle and the folds' edges
cv.fill(_in & (_v == 12) & _lit, WALL)
cv.fill(_in & (_v == 12) & _dim, WALL_SHADE)
cv.fill(cv.m_edge(MAP), BLACK)
MP_SHEET = MAP.copy()

# pins: two dull ones at the top corners, two bright ones on friends (a 2x2 head, a catchlight toward the CRT
# below right, a 1px shadow up-left on the paper)
MP_PINS = []
for _px, _py in ((MP_X0 + 1, MP_Y0 + 1), (MP_X1 - 1, MP_Y0 + 1)):
    cv.dot(_px, _py, SLATE)
    MP_PINS.append((_px, _py))
for (_lx, _ly), _ink in (((7, 10), RED), ((17, 18), GLOW)):      # red on the lit panel, cyan on the dim one
    _px, _py = MP_X0 + _lx, MP_Y0 + _ly
    cv.dots([(_px - 1, _py - 1), (_px, _py - 1), (_px - 1, _py)], DARK)
    cv.dots([(_px, _py), (_px + 1, _py), (_px, _py + 1)], _ink)
    cv.dot(_px + 1, _py + 1, SCREEN)
    MP_PINS += [(_px, _py), (_px + 1, _py), (_px, _py + 1), (_px + 1, _py + 1)]
cv.masks['bump'] = MAP

# vp-check: pinned flat to the back wall, it is frontal: level top and bottom, plumb sides
cv.persp.edge('map', (MP_X0 + 1, MP_Y0), (MP_X1 - 1, MP_Y0), 'h')
cv.persp.edge('map', (MP_X0 + 1, MP_Y1), (MP_X1 - 1, MP_Y1), 'h')
cv.persp.edge('map', (MP_X0, MP_Y0 + 1), (MP_X0, MP_Y1 - 1), 'v')
cv.persp.edge('map', (MP_X1, MP_Y0 + 1), (MP_X1, MP_Y1 - 1), 'v')
