# 03 clear the old furniture: the two leather armchairs, the coffee table with its plant and the leather couch go (the
# user: "the couches are weird and the vibe is cold"). Everything they hid is rebuilt from the room's own pixels: the
# bedroom door and the glass door carried down to the floor (each door's top mirrored for its bottom), the sideboard's
# left end mirrored from its right, the walls continued in their own texture to a skirting board, and a new floor of
# honey boards built in the camera (planks across the room, seams on depth lines, butt joints receding to the VP).
CLEAR_Y = 199                                          # the old furniture's top, roughly; everything below is redrawn
# the sofa stays (its forms are the artist's; its leather is repainted as fabric below): its silhouette, traced
SOFA_POLY = [(318, 243), (330, 235), (355, 221), (378, 212), (405, 219), (430, 229), (460, 242), (500, 257),
             (500, 323), (333, 323), (327, 290), (321, 262)]
SOFA = cv.m_poly(SOFA_POLY) & (YY <= 323) & False      # (the sofa is redrawn in 07; its pixels are cleared)
CLR = (YY > CLEAR_Y) & ~SOFA
KEEP = cv.m_rect(190, 199, 287, 241) | cv.m_rect(288, 199, 339, 242)   # the sideboard's right part, the TV stand's left
CLR &= ~KEEP

# ---- the floor lines: the left wall's (0,246)-(57,240), the back wall's y 240, the right wall's from (382,240) to the VP
def floor_line_y(x):
    x = np.asarray(x, float)
    left = 246 - (x / 57) * 6
    right = 240 + (x - 382) * (240 - VP[1]) / (382 - VP[0])
    return np.where(x < 57, left, np.where(x > 382, right, 240))


FLOOR_M = YY > floor_line_y(XX)
cv.masks = {}

# ---- the floor, in Fermion's own manner (its boards studied where they showed): planks across the room, ~9cm deep,
# each one flat in one of three tones (mostly the mid, some light, a few half-and-half), a 1px dark seam between, and
# now and then a butt joint near us. The whole floor is redrawn so real and rebuilt boards can't disagree.
FX, FZ = on_floor(XX, np.maximum(YY, VP[1] + 1))
_pk = np.floor(FZ / 9.0).astype(int)
_rng = np.random.default_rng(12)
_tone = _rng.choice([0, 0, 0, 1, 1, 2], 6000)               # 0 mid, 1 half, 2 light
_kk = np.clip(_pk, 0, 5999)
_board = FLOOR_M
cv.fill(_board & (_tone[_kk] == 0), DESK_SHADE)
cv.tile(_board & (_tone[_kk] == 1), '1/2', DESK_SHADE, DESK)
cv.fill(_board & (_tone[_kk] == 2), DESK)
cv.fill(_board & (_pk != np.roll(_pk, 1, axis=0)), WOOD)    # seams
_phase = _rng.uniform(0, 140, 6000)
_jx = (FX + _phase[_kk]) % 140
_joint = _board & (np.abs(_jx - 70) < 140 / np.maximum(FZ, 1) * 0.7) & (YY > VP[1] + 95)
cv.fill(_joint, WOOD)
# ---- the strip below the old frame (BOTTOM rows): every receding surface continued along its own rays from the VP
# (the band just above, scaled 1.4x out from the VP: that continues a floor's boards, the rug, and the sofa's skirt and
# seat exactly, as each is a plane through the eye's direction); the sofa's pillows don't continue (seat fabric there)
_last = TOP + 293
_mag = (cv.h - 1 - VP[1]) / (_last - VP[1])
for y in range(_last + 1, cv.h):
    y0 = VP[1] + (y - VP[1]) / _mag * ((cv.h - 1 - VP[1]) / (cv.h - 1 - VP[1]))
    y0 = VP[1] + (y - VP[1]) / _mag
    xs = np.arange(cv.w)
    x0 = np.clip(np.round(VP[0] + (xs - VP[0]) / _mag).astype(int), 0, cv.w - 1)
    yy0 = int(np.clip(round(y0), 0, _last))
    cv.idx[y, xs] = cv.idx[yy0, x0]
    src[y, xs] = src[yy0, x0]
    SOFA[y, xs] = SOFA[yy0, x0]
    FLOOR_M[y, xs] = True

# ---- walls below CLEAR_Y down to the floor line: continue each wall's texture from 16 rows up (the tile phase)
for x0, x1 in ((0, 10), (47, 62), (129, 143), (377, 383)):
    for y in range(CLEAR_Y + 1, 247):
        sel = (XX[y] >= x0) & (XX[y] < x1) & ~FLOOR_M[y] & CLR[y]
        cv.idx[y, sel] = cv.idx[y - 16, sel]

# ---- skirting: a wood board along the walls' feet, 3px, its top edge lit
SKIRT = CLR & ~FLOOR_M & (YY >= floor_line_y(XX) - 3) & (XX < 383)
cv.fill(SKIRT, WOOD)
cv.fill(SKIRT & (YY < floor_line_y(XX) - 2), DESK_SHADE)

# ---- the bedroom door down to the floor: its top (rows 88-112) mirrored for the bottom (ends at the floor line)
LD = cv.m_poly(OBJ_POLY['left_door'])
for y in range(CLEAR_Y + 1, 241):
    src_y = 88 + (240 - y) + 6
    sel = (XX[y] >= 10) & (XX[y] <= 46) & CLR[y]
    if 98 <= src_y <= 140:
        cv.idx[y, sel] = cv.idx[src_y, sel]
    else:
        cv.idx[y, sel] = cv.idx[190, sel]               # the door's plain field and its panel, as at mid height

# ---- the glass door: its lower pane continues, then the bottom rail and a kick plate, mirrored from its top rail
for y in range(CLEAR_Y + 1, 239):
    sel = (XX[y] >= 62) & (XX[y] <= 128) & CLR[y]
    if y <= 222:
        cv.idx[y, sel] = cv.idx[y - 30, sel]           # the pane above's rows (the panes are 30 rows apart)
    else:
        cv.idx[y, sel] = cv.idx[100 + (238 - y), sel]  # the door's top rail and frame, upside down

# ---- the sideboard's left end: its right end mirrored
for y in range(CLEAR_Y + 1, 242):
    for x in range(143, 190):
        if CLR[y, x]:
            cv.idx[y, x] = cv.idx[y, 285 - (x - 143)]

# ---- the sideboard, rebuilt symmetric (about x 214): the right cabinet door's foot is its top mirrored (the coffee
# table's plant stood in front of it), the plinth is the middle's, and the left end is the right end mirrored
SB_AX = 428                                            # x' = SB_AX - x
for y in range(218, 233):                              # the right door's bottom rows from its top rows
    for x in range(246, 284):
        cv.idx[y, x] = cv.idx[172 + (232 - y), x]
for y in range(232, 242):                              # the plinth across the right end, from the middle's
    for x in range(236, 286):
        cv.idx[y, x] = cv.idx[y, 196 + (x - 236) % 36]
for y in range(169, 242):                              # below its top board: what stands on it stays
    for x in range(143, 214 - 30):
        cv.idx[y, x] = cv.idx[y, SB_AX - x]

# ---- the TV stand's right half: its left half mirrored (the couch's arm hid it)
TS_AX = 663
for y in range(210, 246):
    for x in range(332, 378):
        src_x = TS_AX - x
        if 288 <= src_x < 332:
            cv.idx[y, x] = cv.idx[y, src_x]

# ---- the right wall: the curtain's folds and the glass doors' frames run straight down to a floor track
RIGHT_LOW = (XX >= 383) & (YY > CLEAR_Y) & ~FLOOR_M & ~SOFA
for y in range(CLEAR_Y + 1, cv.h):
    sel = RIGHT_LOW[y]
    if sel.any():
        cv.idx[y, sel] = cv.idx[y - 48, sel]
TRACK = (XX >= 383) & (np.abs(YY - floor_line_y(XX)) <= 1.5)
cv.fill(TRACK, SLATE)
cv.fill(TRACK & (YY < floor_line_y(XX) - 0.5), CURTAIN)
