# 18 the stand lamp (Panda's real bedroom lamp, Bedroom Lamp A and B: two bulbs under one shade): a floor lamp in the
# back-left corner, behind the bed's head and the plush, a cream pleated drum shade in front of the corner post, its
# pole going down behind the headboard. Drawn the house's way: blocked out in the camera, then an image model's
# cleanup of this picture (fal, 2026-10-09: "redraw the floor lamp in place, off"; it kept the butterfly and the
# posters), snapped to this room's 16 registers. Only the pixels that differ from the room as it was are taken (never
# committed: it derives from the third-party room). The site lights it live: the shade glows, its light falls on the
# wall, the posters, the pillows and the plush.
from pc98.config import ROOT
SCRATCH = ROOT / '.scratch'                            # the model's redraw (gitignored)
_fal = np.load(str(SCRATCH / 'fal_bedroom_lamp_v2_idx.npy'))
_pal = cv.pal.astype(float) * 17
_box = np.zeros((cv.h, cv.w), bool)
_box[84:175, 30:72] = True
_diff = (np.abs(_pal[_fal] - _pal[cv.idx]).sum(-1) > 60) & _box
STAND_LAMP = _diff
cv.idx[STAND_LAMP] = _fal[STAND_LAMP]
_ys = np.nonzero(STAND_LAMP)[0]
_shade_bot = _ys.min() + 0.42 * (_ys.max() - _ys.min())
cv.masks['stand_lamp'] = STAND_LAMP
cv.masks['shade_stand'] = STAND_LAMP & (YY <= _shade_bot) & cv.m_where(PAPER, CURTAIN, GLOW, DESK, SCREEN, WHITE)
