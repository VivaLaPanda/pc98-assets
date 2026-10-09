# 05 a small rasterizer for things built as surfaces in the room's camera (the kotatsu's quilt, the couch's cushions):
# a grid of quads in cm, each projected and filled with a depth test, keeping for every pixel the surface's own
# coordinates (u, v), its normal and its depth, so a print follows the drape and shading follows the form.


class Surf:
    def __init__(self):
        self.depth = np.full((cv.h, cv.w), np.inf)
        self.u = np.zeros((cv.h, cv.w))
        self.v = np.zeros((cv.h, cv.w))
        self.n = np.zeros((cv.h, cv.w, 3))
        self.part = np.zeros((cv.h, cv.w), np.int16)   # which piece of the object (0 = none)

    def mask(self, part=None):
        m = np.isfinite(self.depth)
        return m if part is None else m & (self.part == part)


def proj_arr(P):
    """(..., 3) cm -> (..., 2) canvas."""
    Z = np.maximum(P[..., 2], 1e-3)
    return np.stack([VP[0] + D * P[..., 0] / Z, VP[1] - D * P[..., 1] / Z], -1)


def raster_grid(S, P, U, V, part):
    """P (n, m, 3) points of a surface grid, U/V (n, m) its own coordinates: fill every cell (two triangles) into S."""
    Q = proj_arr(P)
    N = np.cross(P[1:, :-1] - P[:-1, :-1], P[:-1, 1:] - P[:-1, :-1])
    N /= np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-9)
    n, m = P.shape[:2]
    for i in range(n - 1):
        for j in range(m - 1):
            idx4 = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                a, b, c = (idx4[k] for k in tri)
                pa, pb, pc = Q[a], Q[b], Q[c]
                x0 = int(np.floor(min(pa[0], pb[0], pc[0]))); x1 = int(np.ceil(max(pa[0], pb[0], pc[0])))
                y0 = int(np.floor(min(pa[1], pb[1], pc[1]))); y1 = int(np.ceil(max(pa[1], pb[1], pc[1])))
                x0, y0 = max(x0, 0), max(y0, 0)
                x1, y1 = min(x1, cv.w - 1), min(y1, cv.h - 1)
                if x1 < x0 or y1 < y0:
                    continue
                ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1] + 0.5
                det = (pb[1] - pc[1]) * (pa[0] - pc[0]) + (pc[0] - pb[0]) * (pa[1] - pc[1])
                if abs(det) < 1e-9:
                    continue
                l1 = ((pb[1] - pc[1]) * (xs - pc[0]) + (pc[0] - pb[0]) * (ys - pc[1])) / det
                l2 = ((pc[1] - pa[1]) * (xs - pc[0]) + (pa[0] - pc[0]) * (ys - pc[1])) / det
                l3 = 1 - l1 - l2
                inside = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
                if not inside.any():
                    continue
                z = l1 * P[a][2] + l2 * P[b][2] + l3 * P[c][2]
                yy, xx = (ys - 0.5).astype(int), (xs - 0.5).astype(int)
                sel = inside & (z < S.depth[yy, xx])
                if not sel.any():
                    continue
                ty, tx = yy[sel], xx[sel]
                S.depth[ty, tx] = z[sel]
                S.u[ty, tx] = (l1 * U[a] + l2 * U[b] + l3 * U[c])[sel]
                S.v[ty, tx] = (l1 * V[a] + l2 * V[b] + l3 * V[c])[sel]
                S.n[ty, tx] = N[min(i, n - 2), min(j, m - 2)]
                S.part[ty, tx] = part


def lambert(S, L=(0.55, 0.65, -0.52)):
    """Light from the balcony glass (right), above and a little in front."""
    L = np.array(L, float); L /= np.linalg.norm(L)
    nn = S.n.copy()
    flip = nn[..., 2] > 0                               # normals toward the camera (-Z)
    nn[flip] *= -1
    return np.clip((nn * L).sum(-1), 0, 1)


# ---- the room's depth buffer: every pixel's nearest surface (cm along Z). New things are painted inside an
# `occluded(depth)` block: whatever they paint lands only where they are nearer than what's there, and the buffer
# takes their depth. So the order passages paint in never decides what's in front.
def room_depth():
    Zd = np.full((cv.h, cv.w), BACK_Z - 8.0)               # the back wall and what stands against it
    rx = (XX - VP[0]) / D
    with np.errstate(divide='ignore', invalid='ignore'):
        Zl = np.where(rx < -1e-3, -322 / rx, np.inf)
        Zr = np.where(rx > 1e-3, 178 / rx, np.inf)
    left = (XX < 57) & (Zl < Zd)
    Zd[left] = Zl[left]
    right = (XX > 382) & (Zr < Zd)
    Zd[right] = Zr[right]
    fl = FLOOR_M
    Zd[fl] = (D * EYE / np.maximum(YY - VP[1], 1e-3))[fl]
    return Zd


ZBUF = room_depth()
ZBUF[SOFA] = 125.0                                     # the sofa (03b): its base sits ~1.25m from us


class occluded:
    """with occluded(depth): ... paints only where `depth` (a number or a per-pixel array) is nearer than ZBUF."""

    def __init__(self, depth, eps=0.0):
        self.is_map = np.ndim(depth) > 0                 # a per-pixel map: its finite pixels are the object's footprint
        self.depth = np.broadcast_to(np.asarray(depth, float), ZBUF.shape)
        self.eps = eps

    def __enter__(self):
        self.before = cv.idx.copy()
        return self

    def __exit__(self, *exc):
        changed = cv.idx != self.before
        wins = self.depth < ZBUF - self.eps
        hidden = changed & ~wins
        cv.idx[hidden] = self.before[hidden]
        footprint = changed | (np.isfinite(self.depth) if self.is_map else False)
        keep = footprint & wins
        ZBUF[keep] = self.depth[keep]
        self.visible = keep
        return False


def plane_depth(P0, P1, P2):
    """Per-pixel Z where each pixel's ray meets the plane through three room points."""
    P0, P1, P2 = (np.asarray(p, float) for p in (P0, P1, P2))
    n = np.cross(P1 - P0, P2 - P0)
    rx, ry = (XX - VP[0]) / D, -(YY - VP[1]) / D
    den = n[0] * rx + n[1] * ry + n[2]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (n @ P0) / den
    return np.where(np.isfinite(t) & (t > 0), t, np.inf)
