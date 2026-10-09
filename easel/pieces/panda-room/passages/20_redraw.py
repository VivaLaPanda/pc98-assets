# 20 the redrawn blazer: an image model's polish of 11's drawing (nano-banana-pro edit on fal, prompted with this
# picture; 2026-10-09), box-downscaled to the 500px grid and snapped to the room's inks (never committed: it derives
# from the third-party room). Only what it redrew comes back: where its picture strays from the headboard and pillow
# as they were before 11 (blurred, so a dither's shift doesn't count), cleaned to the jacket's own shape; where 11's
# drawing reaches past it, the headboard comes back. (The butterfly was polished too, but at 15x11 the snap to the
# inks lost its line art: 06's own pixels stay.)
from pc98.config import ROOT
_FAL = np.load(str(ROOT / '.scratch' / 'fal_bed_blazer_v1_1_idx.npy'))
_PAL = np.array([[int(c, 16) * 17 for c in cv.hex(i).lstrip('#')] for i in range(16)], float)


def _blur(rgb, r=1):
    out = np.zeros_like(rgb)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out += np.roll(np.roll(rgb, dy, 0), dx, 1)
    return out / (2 * r + 1) ** 2


def _fill_holes(m):
    """m with every hole the outside can't reach filled."""
    outside = np.zeros_like(m)
    outside[0, :] = ~m[0, :]; outside[-1, :] = ~m[-1, :]; outside[:, 0] = ~m[:, 0]; outside[:, -1] = ~m[:, -1]
    while True:
        g = outside.copy()
        g[1:] |= outside[:-1]; g[:-1] |= outside[1:]; g[:, 1:] |= outside[:, :-1]; g[:, :-1] |= outside[:, 1:]
        g &= ~m
        if (g == outside).all():
            return ~outside
        outside = g


def _redrawn(pre, box, thr):
    """Where the redraw strays from `pre` inside box, as one solid shape (its biggest piece, holes filled)."""
    x0, y0, x1, y1 = box
    a = _blur(_PAL[_FAL[y0:y1, x0:x1]]); b = _blur(_PAL[pre[y0:y1, x0:x1]])
    d = np.sqrt(((a - b) ** 2).sum(-1)) > thr
    lab = np.zeros(d.shape, int); n = 0; best, size = 0, 0
    for y, x in zip(*np.nonzero(d)):
        if lab[y, x]:
            continue
        n += 1; stack = [(y, x)]; lab[y, x] = n; k = 0
        while stack:
            cy, cx = stack.pop(); k += 1
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < d.shape[0] and 0 <= nx < d.shape[1] and d[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; stack.append((ny, nx))
        if k > size:
            best, size = n, k
    m = np.zeros((cv.h, cv.w), bool)
    m[y0:y1, x0:x1] = _fill_holes(lab == best)
    return m


BLAZER_FAL = _redrawn(PRE_BZ, (70, 150, 180, 226), 22)
cv.idx[BLAZER & ~BLAZER_FAL] = PRE_BZ[BLAZER & ~BLAZER_FAL]
cv.idx[BLAZER_FAL] = _FAL[BLAZER_FAL]
cv.masks['linkedin'] = BLAZER_FAL
print('blazer', int(BLAZER_FAL.sum()))
