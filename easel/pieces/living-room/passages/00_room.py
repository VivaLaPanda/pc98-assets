# 00 the room. The ground is a real PC-98 living room (Fermion's TV room; a 16-ink recovery of the rescaled rip, never
# committed), resampled 640 -> 500 like the bedroom's own base so the two rooms share a pixel density, then each pixel
# snapped back to the room's 16 inks. It sits in the bedroom's 740:528 window (500x357): TOP rows of ceiling above,
# BOTTOM rows of floor below, painted in 01/02.
from pc98.config import ROOT
SCRATCH = ROOT / '.scratch'                            # third-party sources and model redraws (gitignored)
SRC = str(SCRATCH / 'fermion_living.png')
idx640, pal16 = quantize(SRC)
_rgb = np.array([[int(c, 16) * 17 for c in h[1:]] for h in pal16], float)
_big = Image.fromarray(_rgb[idx640].astype(np.uint8))
_small = np.asarray(_big.resize((500, 294), Image.BILINEAR)).astype(float)
_snap = ((_small[..., None, :] - _rgb[None, None]) ** 2).sum(-1).argmin(-1).astype(np.uint8)
TOP, BOTTOM = 30, 63           # the export crops the TOP rows: the site shows rows 30..386 (500x357)
assert TOP + 294 + BOTTOM == cv.h
_idx = np.zeros((cv.h, cv.w), np.uint8)
_idx[TOP:TOP + 294] = _snap
cv.start_from(_idx, pal16)
OLD = np.zeros((cv.h, cv.w), bool)
OLD[TOP:TOP + 294] = True
