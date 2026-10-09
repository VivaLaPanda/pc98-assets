# 07b the redrawn foreground. The kotatsu, the couch, the rug and the floor here are an image model's redraw of this
# room (nano-banana-pro edit on fal, prompted with this picture and the bedroom as the style; 2026-10-09), brought back
# to this canvas: box-downscaled to its 500px grid and snapped to the house's 16 inks (never committed: it derives from
# the third-party room). It replaces 06/07's paint where it stands (below the floor line, and the kotatsu's and the
# couch's own outlines); 06/07 still give their geometry (depth, normals) to the depth buffer and the lamplight.
_fal = np.load(str(SCRATCH / 'fal_living_v1_1_idx.npy'))     # final coords (500x357)
_FAL = np.zeros((cv.h, cv.w), np.uint8)
_FAL[TOP:TOP + _fal.shape[0]] = _fal
_o = np.array([0, TOP])
KOT_POLY = [(197, 192), (285, 190), (362, 192), (372, 226), (390, 262), (398, 300), (388, 312), (300, 318),
            (200, 317), (122, 313), (122, 300), (150, 265), (170, 240), (185, 228)]
COUCH_POLY = [(356, 197), (408, 196), (412, 168), (440, 167), (470, 170), (500, 173), (500, 357), (402, 357), (398, 320), (393, 300),
              (380, 272), (366, 242), (357, 215)]
KOT_M = cv.m_poly([tuple(np.array(p) + _o) for p in KOT_POLY])
COUCH_M = cv.m_poly([tuple(np.array(p) + _o) for p in COUCH_POLY])
# the redraw's couch back ran flatter than the room (its top from y 168 to 173, final coords, where a line to the VP
# drops ~15px over the same run; 07's box couch agrees with the VP): each column of the back, from its top down to
# where it meets the seat, is stretched or squashed so its top lies on the VP line through its middle (the far end
# rises 7px, the near end comes down 3; the glass shows where it came down)
_bx = np.arange(410, 500)
_t_old = np.interp(_bx, [408, 412, 440, 470, 500], [196, 168, 167, 170, 173]) + TOP
_t_new = VP[1] + 0.176 * (_bx - VP[0])
_anch = VP[1] + 0.571 * (_bx - VP[0])
for _i, _x in enumerate(_bx):
    _t0, _t1, _a = _t_old[_i], _t_new[_i], _anch[_i]
    _ys = np.arange(int(np.ceil(_t1)), int(_a) + 1)
    _src = np.clip(np.round(_a - (_a - _ys) * (_a - _t0) / (_a - _t1)).astype(int), 0, cv.h - 1)
    _col = _FAL[:, _x].copy()
    _FAL[_ys, _x] = _col[_src]
    COUCH_M[:int(np.ceil(_t1)), _x] = False
    COUCH_M[int(np.ceil(_t1)):int(_a) + 1, _x] = True
REDRAW = ((YY > TOP + 210) | KOT_M | COUCH_M) & (YY >= TOP)
REDRAW &= ~(cv.m_rect(288, 199, 377, 244) & ~KOT_M)        # the TV stand's foot stays ours
cv.idx[REDRAW] = _FAL[REDRAW]
cv.masks['kotatsu'] = KOT_M
cv.masks['couch'] = COUCH_M
KT_BOARD = KT_BOARD | (KOT_M & (YY < TOP + 229))
