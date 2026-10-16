"""panel-icons, step 1 (the home-icon flow): the futon and the sunrise modelled and lit, then quantized to the set's tone
ramps, as assets/home-icon/render.py did for the kotatsu. Drafts drawn from primitives read as clip art (the futon as a
cake, the sunrise as a sun over a box); a lit model gives the quilt and the land real volume for polish.py to redraw.
Run:
    uv run python assets/panel-icons/render.py [futon hills fuji fuji2 saddle dome]

Writes out/render/<name>_render.png (the lit model at 8x, flat colours, mint background: the second reference for the
image model) and out/render/<name>.png (48x48 in SITE letters with the set's outline and plum overlap lines: the draft
beside the real icons).

Models (cm, y up, the camera looks down from the front; light from the top left, toward us):
- futon (chosen): a shikibuton on the floor, its head at the back left; a puffy kakebuton in the kotatsu's periwinkle
  and pink plaid over a sleeper's lump, overhanging and draping to the floor in soft folds, its top edge turned down
  white; a big white pillow; zzz.
- hills: two rounded hills, the sun behind the dip between them (redrawn, the dip pinched the sun into a bulb).
- fuji: a snow-capped cone over foothills, the sun rising beside the peak (redrawn: reads, but half the square empty).
- fuji2 (chosen): the sun half risen behind Fuji's flat summit, centred, so it fills the square.
- saddle: the sun over a broad shallow saddle of hills (not redrawn: too wide and flat at 48 px).
- dome (no Fuji): the sun half risen behind a rounded hill (not redrawn: a lumpy periwinkle hill under a sun reads as
  the "partly cloudy" weather icon).
"""
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from pc98 import palette as P

HERE = Path(__file__).parent
OUT = HERE / 'out' / 'render'
N, SS = 48, 8                                  # icon size, supersampling
LEG = P.get('site+')
MINT = (0x00, 0xEE, 0xBB)

# per material: tones from lit to dark (a pair is a 50% checker of its two letters)
RAMP = {
    'quilt': ['W', 'p', ('p', 'u'), 'u'],
    'plaid': ['k', 'k', ('p', 'u'), 'u'],     # the plaid fades into the shade, as on the kotatsu
    'collar': ['W', 'W', ('W', 'a'), 'a'],
    'sheet': ['W', 'a', ('a', 'u'), 'u'],     # mauve under the white pillow, so the pillow stands out
    'pillow': ['W', 'W', ('W', 'a'), 'a'],
    'sun': ['W', 'y', ('y', 'e'), 'e'],
    'ray': ['y', 'y', 'y', 'y'],
    'ray2': ['e', 'e', 'e', 'e'],
    'hill': ['W', 'p', ('p', 'u'), 'u'],
    'far': ['a', 'a', ('a', 'u'), 'u'],
    'snow': ['W', 'W', ('W', 'a'), 'a'],
}
MATS = list(RAMP)
WHITE = {'quilt': 0.97, 'plaid': 0.97, 'hill': 0.975, 'far': 0.975, 'sun': 0.96}   # white only this lit (else 0.86)
NO_OUTLINE = ('ray', 'ray2')
FLAT = {   # the lit model's preview colours
    'quilt': (136, 153, 255), 'plaid': (255, 170, 187), 'collar': (255, 255, 255), 'sheet': (238, 238, 238),
    'pillow': (255, 255, 255), 'sun': (255, 238, 85), 'ray': (255, 238, 85), 'ray2': (255, 170, 119),
    'hill': (136, 153, 255), 'far': (187, 170, 187), 'snow': (255, 255, 255),
}
LIGHT = np.array([-0.6, 0.62, -0.5]); LIGHT /= np.linalg.norm(LIGHT)    # camera space: from the top left, toward us


@dataclass
class Part:
    pts: np.ndarray          # (n, 3) world points
    nrm: np.ndarray          # (n, 3) unit normals
    mat: np.ndarray          # (n,) material index
    glow: float = 0.0        # light sources: a floor under the shading (1 = always fully lit)


def mid(name: str) -> int:
    return MATS.index(name)


def smoothstep(t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def heightfield(xs: np.ndarray, zs: np.ndarray, H: np.ndarray, mat: np.ndarray, keep: np.ndarray) -> Part:
    """y = H(x, z) on a grid; normals from its gradient; only `keep` points."""
    X, Z = np.meshgrid(xs, zs)
    dHz, dHx = np.gradient(H, zs, xs)
    n = np.stack([-dHx, np.ones_like(H), -dHz], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Pg = np.stack([X, H, Z], -1)
    return Part(Pg[keep], n[keep], mat[keep])


def spow(v: np.ndarray, e: float) -> np.ndarray:
    return np.sign(v) * np.abs(v) ** e


def superellipsoid(c: tuple, r: tuple, e1: float, e2: float, mat: str, n: int = 400) -> Part:
    """A rounded box: centre c, half sizes r (x, y, z), squareness e1 (vertical) and e2 (round the sides). Normals
    from the implicit form's gradient (finite differences crease at the poles)."""
    eta, om = np.meshgrid(np.linspace(-np.pi / 2, np.pi / 2, n), np.linspace(-np.pi, np.pi, 2 * n))
    x = r[0] * spow(np.cos(eta), e1) * spow(np.cos(om), e2)
    y = r[1] * spow(np.sin(eta), e1)
    z = r[2] * spow(np.cos(eta), e1) * spow(np.sin(om), e2)
    u, v, w = np.abs(x / r[0]) + 1e-9, np.abs(y / r[1]) + 1e-9, np.abs(z / r[2]) + 1e-9
    h = u ** (2 / e2) + w ** (2 / e2)
    k = (e2 / e1) * h ** (e2 / e1 - 1)
    nx = k * (2 / e2) * u ** (2 / e2 - 1) * np.sign(x) / r[0]
    ny = (2 / e1) * v ** (2 / e1 - 1) * np.sign(y) / r[1]
    nz = k * (2 / e2) * w ** (2 / e2 - 1) * np.sign(z) / r[2]
    nrm = np.stack([nx, ny, nz], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-12
    Pg = np.stack([x, y, z], -1) + np.array(c)
    return Part(Pg.reshape(-1, 3), nrm.reshape(-1, 3), np.full(Pg.shape[0] * Pg.shape[1], mid(mat)))


# ---- the futon ----------------------------------------------------------------------------------------------------

MAT_W, MAT_L, MAT_H = 50.0, 66.0, 9.0          # shikibuton half width, half length, height
Q_SIDE, Q_FOOT, Q_HEAD = 63.0, -80.0, 26.0    # kakebuton: half width, foot edge, head edge (z)


def body(X: np.ndarray, Z: np.ndarray) -> np.ndarray:
    """The sleeper's lump under the quilt: shoulders and hips high, legs lower, feet a small rise."""
    across = np.exp(-((X - 3) / 21) ** 2)
    along = 1.0 * np.exp(-((Z - 10) / 26) ** 2) + 0.75 * np.exp(-((Z + 30) / 20) ** 2) + 0.55 * np.exp(-((Z + 60) / 9) ** 2)
    return 16 * across * np.clip(along, 0, 1.1)


def quilt() -> Part:
    xs = np.linspace(-Q_SIDE - 4, Q_SIDE + 4, 900)
    zs = np.linspace(Q_FOOT - 4, Q_HEAD, 900)
    X, Z = np.meshgrid(xs, zs)
    top = MAT_H + 7 + body(X, Z)
    # the overhang: 0 over the mattress, 1 at the quilt's wavy edge, which lies on the floor in soft folds
    side = Q_SIDE + 2.8 * np.sin(Z / 6.5) + 1.5 * np.sin(Z / 2.9)
    foot = Q_FOOT + 2.8 * np.sin(X / 6.0) + 1.2 * np.sin(X / 2.6)
    dx = np.clip((np.abs(X) - MAT_W) / (side - MAT_W), 0, None)
    dz = np.clip((-MAT_L - Z) / (-MAT_L - foot), 0, None)
    d = np.sqrt(dx ** 2 + dz ** 2)
    H = 2.0 + (top - 2.0) * (1 - smoothstep(d))
    # the head edge: the quilt's thickness rolls down onto the mattress
    H = MAT_H + (H - MAT_H) * smoothstep((Q_HEAD - Z) / 5)
    keep = (d < 1.0) & (Z <= Q_HEAD) & (H > MAT_H * 0.2)
    # the plaid in the cloth's own coordinates (arc length over the drape, roughly), ~25 cm squares
    u = X + np.sign(X) * dx * 10
    v = Z - dz * 10
    plaid = (np.abs((u / 25 + 0.5) % 1 - 0.5) < 0.06) | (np.abs(((v - 6) / 25) % 1 - 0.5) < 0.06)
    collar = Z > Q_HEAD - 10
    mat = np.where(collar, mid('collar'), np.where(plaid, mid('plaid'), mid('quilt')))
    return heightfield(xs, zs, H, mat, keep)


def pillow() -> Part:
    return superellipsoid((0, MAT_H + 9, 45), (31, 9, 15), 0.7, 0.45, 'pillow', n=1000)


def mattress() -> Part:
    return superellipsoid((0, MAT_H / 2, 0), (MAT_W, MAT_H / 2, MAT_L), 0.2, 0.1, 'sheet', n=1100)


def futon_parts() -> list:
    return [mattress(), quilt(), pillow()]


# ---- the sunrise --------------------------------------------------------------------------------------------------

def sun(c: tuple, r: float) -> Part:
    th, ph = np.meshgrid(np.linspace(0, np.pi, 300), np.linspace(0, 2 * np.pi, 600))
    n = np.stack([np.sin(th) * np.cos(ph), np.cos(th), np.sin(th) * np.sin(ph)], -1)
    Pg = np.array(c) + n * r
    return Part(Pg.reshape(-1, 3), n.reshape(-1, 3), np.full(Pg.shape[0] * Pg.shape[1], mid('sun')), glow=0.3)


def rays(c: tuple, r0: float, r1: float, k: int = 9, width: float = 0.13) -> Part:
    """Flat wedges in a plane behind the sun, fanned over its upper half, yellow and peach in turn."""
    pts, mats = [], []
    for i in range(k):
        a = np.pi * (i + 0.5) / k
        rr, ww = np.meshgrid(np.linspace(r0, r1, 120), np.linspace(-width / 2, width / 2, 40))
        ww = ww * (1 - 0.5 * (rr - r0) / (r1 - r0))
        ang = a + ww
        x = c[0] - np.cos(ang) * rr
        y = c[1] + np.sin(ang) * rr
        pts.append(np.stack([x, y, np.full_like(x, c[2] + 3)], -1).reshape(-1, 3))
        mats.append(np.full(x.size, mid('ray' if i % 2 == 0 else 'ray2')))
    p = np.concatenate(pts)
    return Part(p, np.repeat([[0, 0, -1.0]], len(p), 0), np.concatenate(mats), glow=1.0)


def hills_parts() -> list:
    xs = np.linspace(-80, 80, 900); zs = np.linspace(-45, 90, 700)
    X, Z = np.meshgrid(xs, zs)
    bump = lambda cx, cz, rx, rz, h: h * np.exp(-((X - cx) / rx) ** 2 - ((Z - cz) / rz) ** 2)
    near = bump(-24, 0, 23, 22, 38)
    right = bump(25, 16, 22, 20, 29)
    H = np.maximum(np.maximum(near, right), 7 * np.exp(-(X / 50) ** 2 - ((Z - 8) / 28) ** 2))
    land = H > 3.0                                                # the land ends at a contour: no plate under it
    mat = np.full(H.shape, mid('hill'))
    c = (4, 16, 110)
    return [heightfield(xs, zs, H, mat, land), sun(c, 30), rays(c, 37, 62)]


def fuji_parts() -> list:
    xs = np.linspace(-90, 90, 900); zs = np.linspace(-40, 80, 700)
    X, Z = np.meshgrid(xs, zs)
    R = np.sqrt((X + 8) ** 2 + (Z - 30) ** 2)
    cone = 54 * np.clip(1 - R / 58, 0, None) ** 1.45
    cone = np.minimum(cone, 47)                                   # the crater's flat top
    bump = lambda cx, cz, rx, rz, h: h * np.clip(1 - ((X - cx) / rx) ** 2 - ((Z - cz) / rz) ** 2, 0, None) ** 0.6
    foot = np.maximum(bump(34, -4, 26, 22, 12), bump(-40, -6, 24, 20, 9))
    H = np.maximum(cone, foot)
    land = H > 0.4
    th = np.arctan2(Z - 30, X + 8)
    snow = cone > 36 + 2.5 * np.sin(7 * th) + 1.5 * np.sin(13 * th + 1)
    mat = np.where(snow & (cone >= foot), mid('snow'), mid('hill'))
    c = (30, 22, 110)
    return [heightfield(xs, zs, H, mat, land), sun(c, 20), rays(c, 26, 46, k=7)]


def fuji2_parts() -> list:
    """Round 2: the sun half risen behind Fuji's flat summit ("Diamond Fuji"), centred, so it fills the square."""
    xs = np.linspace(-80, 80, 900); zs = np.linspace(-40, 90, 700)
    X, Z = np.meshgrid(xs, zs)
    R = np.sqrt(X ** 2 + (Z - 30) ** 2)
    cone = 56 * np.clip(1 - R / 66, 0, None) ** 1.5
    cone = np.minimum(cone, 44)                                   # the crater's flat top
    H = cone
    land = H > 2.5
    th = np.arctan2(Z - 30, X)
    snow = cone > 30 + 3.0 * np.sin(9 * th) + 1.5 * np.sin(17 * th + 1)
    mat = np.where(snow, mid('snow'), mid('hill'))
    c = (0, 34, 130)
    return [heightfield(xs, zs, H, mat, land), sun(c, 24), rays(c, 31, 52)]


def saddle_parts() -> list:
    """Round 2: the sun a clean half disc over a broad, shallow saddle of two rounded hills (no V to pinch it)."""
    xs = np.linspace(-90, 90, 900); zs = np.linspace(-45, 90, 700)
    X, Z = np.meshgrid(xs, zs)
    bump = lambda cx, cz, rx, rz, h: h * np.exp(-((X - cx) / rx) ** 2 - ((Z - cz) / rz) ** 2)
    near = bump(-30, 0, 36, 26, 30)
    right = bump(34, 14, 34, 24, 24)
    ridge = bump(0, 40, 70, 22, 20)
    H = np.maximum(np.maximum(near, right), ridge)
    land = H > 3.0
    mat = np.full(H.shape, mid('hill'))
    c = (2, 16, 120)
    return [heightfield(xs, zs, H, mat, land), sun(c, 28), rays(c, 35, 58)]


def dome_parts() -> list:
    """Round 2 alternate without Fuji: the sun half risen behind the broad, convex top of a rounded hill (no dip to pinch
    it), a nearer hill at the right."""
    xs = np.linspace(-80, 80, 900); zs = np.linspace(-45, 90, 700)
    X, Z = np.meshgrid(xs, zs)
    bump = lambda cx, cz, rx, rz, h: h * np.exp(-((X - cx) / rx) ** 2 - ((Z - cz) / rz) ** 2)
    back = bump(-4, 30, 44, 30, 40)
    near = bump(40, -6, 26, 20, 22)
    H = np.maximum(back, near)
    land = H > 3.0
    mat = np.full(H.shape, mid('hill'))
    c = (0, 30, 130)
    return [heightfield(xs, zs, H, mat, land), sun(c, 26), rays(c, 33, 54)]


# ---- rendering ----------------------------------------------------------------------------------------------------

def rot(az: float, el: float) -> np.ndarray:
    a, e = np.radians(az), np.radians(el)
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return Rx @ Ry


def render(parts: list, az: float, el: float, margin: float = 1.0) -> tuple:
    """Splat every point into an 8x z-buffer (2x2 so nothing shows through). Returns material, light, depth (in icon
    pixels) and part index per pixel."""
    P_ = np.concatenate([p.pts for p in parts]); Nn = np.concatenate([p.nrm for p in parts])
    M = np.concatenate([p.mat for p in parts]); G = np.concatenate([np.full(len(p.mat), p.glow) for p in parts])
    O = np.concatenate([np.full(len(p.mat), k) for k, p in enumerate(parts)])
    R = rot(az, -el)
    V = P_ @ R.T; Nv = Nn @ R.T
    lam = np.clip((Nv * LIGHT).sum(1), 0, 1) * 0.85 + 0.15
    lam = G + (1 - G) * lam
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    W = N * SS
    lo, hi = np.array([x.min(), y.min()]), np.array([x.max(), y.max()])
    scale = (W - 2 * SS * margin) / max(hi - lo)
    cx = (x - (lo[0] + hi[0]) / 2) * scale + W / 2
    cy = W / 2 - (y - (lo[1] + hi[1]) / 2) * scale
    order = np.argsort(-z)                                    # far first, near last wins
    zb = np.full((W, W), -1, int)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        ix, iy = np.floor(cx).astype(int) + dx, np.floor(cy).astype(int) + dy
        ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < W)
        idx = order[ok[order]]
        # within a layer the nearest write wins (depth order); across layers keep the nearer
        layer = np.full((W, W), -1, int)
        layer[iy[idx], ix[idx]] = idx
        both = (zb >= 0) & (layer >= 0)
        nearer = both & (z[np.maximum(layer, 0)] < z[np.maximum(zb, 0)])
        zb = np.where((zb < 0) | nearer, layer, zb)
    mat = np.where(zb >= 0, M[np.maximum(zb, 0)], -1)
    lit = np.where(zb >= 0, lam[np.maximum(zb, 0)], 0)
    dep = np.where(zb >= 0, z[np.maximum(zb, 0)] * scale / SS, np.inf)   # in icon pixels
    obj = np.where(zb >= 0, O[np.maximum(zb, 0)], -1)
    return mat, lit, dep, obj


def to_icon(mat: np.ndarray, lit: np.ndarray, dep: np.ndarray, obj: np.ndarray) -> np.ndarray:
    g = np.full((N, N), '.', dtype='<U1')
    qi, pi = mid('quilt'), mid('plaid')
    for j in range(N):
        for i in range(N):
            m = mat[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS].ravel()
            l = lit[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS].ravel()
            if (m >= 0).sum() < SS * SS * 0.45:
                continue
            vals, cnt = np.unique(m[m >= 0], return_counts=True)
            k = vals[np.argmax(cnt)]
            if k in (qi, pi):
                nq, npl = (m == qi).sum(), (m == pi).sum()
                k = pi if npl > 0.34 * (nq + npl) else qi
            L = l[m == k].mean()
            ramp = RAMP[MATS[k]]
            tone = ramp[0] if L > WHITE.get(MATS[k], 0.86) else ramp[1] if L > 0.55 else ramp[2] if L > 0.32 else ramp[3]
            if isinstance(tone, tuple):
                tone = tone[(i + j) % 2]
            g[j, i] = tone
    cm = cellmat(mat)
    cd, co = celldepth(dep, obj, cm, mat)
    g = overlaps(g, cm, cd, co)
    return outline(g, cm)


def cellmat(mat: np.ndarray) -> np.ndarray:
    """Each cell's majority material (-1 for empty), to keep rays out of the outline."""
    out = np.full((N, N), -1)
    for j in range(N):
        for i in range(N):
            m = mat[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS].ravel()
            if (m >= 0).sum() >= SS * SS * 0.45:
                vals, cnt = np.unique(m[m >= 0], return_counts=True)
                out[j, i] = vals[np.argmax(cnt)]
    return out


def celldepth(dep: np.ndarray, obj: np.ndarray, cm: np.ndarray, mat: np.ndarray) -> tuple:
    """Each cell's median depth and its part, over its majority material."""
    d_out = np.full((N, N), np.inf); o_out = np.full((N, N), -1)
    for j in range(N):
        for i in range(N):
            if cm[j, i] >= 0:
                sl = (slice(j * SS, (j + 1) * SS), slice(i * SS, (i + 1) * SS))
                m = mat[sl] == cm[j, i]
                d_out[j, i] = np.median(dep[sl][m])
                o_out[j, i] = np.bincount(obj[sl][m]).argmax()
    return d_out, o_out


def overlaps(g: np.ndarray, cm: np.ndarray, cd: np.ndarray, co: np.ndarray) -> np.ndarray:
    """Plum interior lines (the set's): a cell of a nearer part next to another part behind it, or next to its own
    part well behind it (a fold or a hill over a hill). Rays excluded."""
    skip = np.isin(cm, [mid(k) for k in NO_OUTLINE]) | (cm < 0)
    line = np.zeros_like(skip)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.full((N, N), np.inf); nskip = np.ones((N, N), bool); no = np.full((N, N), -1)
        ys, xs = slice(max(dy, 0), N + min(dy, 0)), slice(max(dx, 0), N + min(dx, 0))
        yd, xd = slice(max(-dy, 0), N + min(-dy, 0)), slice(max(-dx, 0), N + min(-dx, 0))
        nb[yd, xd] = cd[ys, xs]; nskip[yd, xd] = skip[ys, xs]; no[yd, xd] = co[ys, xs]
        gap = np.where(skip | nskip, 0, nb - np.where(skip, 0, cd))
        line |= ~skip & ~nskip & (((no != co) & (gap > 0.5)) | (gap > 4))
    g[line] = 'u'
    return g


def outline(g: np.ndarray, cm: np.ndarray) -> np.ndarray:
    """The set's outline round the silhouette (rays excluded): plum on the lit top/left, black on the bottom/right."""
    solid = (g != '.') & ~np.isin(cm, [mid(k) for k in NO_OUTLINE])
    pad = np.pad(solid, 1)
    up, down = pad[:-2, 1:-1], pad[2:, 1:-1]
    left, right = pad[1:-1, :-2], pad[1:-1, 2:]
    edge = solid & ~(up & down & left & right)
    g[edge & (~down | ~right)] = 'K'
    g[edge & down & right & (~up | ~left)] = 'u'
    return g


ZZZ = ['ppppp\n...p.\n..p..\n.p...\nppppp', 'pppp\n..p.\n.p..\npppp', 'ppp\n.p.\nppp']


def add_zzz(g: np.ndarray, at: list) -> np.ndarray:
    """The draft's zzz in periwinkle, so the model leaves room for them."""
    for z, (x, y) in zip(ZZZ, at):
        for dy, row in enumerate(z.split('\n')):
            for dx, ch in enumerate(row):
                if ch == 'p':
                    g[y + dy, x + dx] = 'p'
    return g


def save_icon(g: np.ndarray, name: str) -> Path:
    out = np.zeros((N, N, 4), np.uint8)
    for k, rgb in LEG.items():
        if k != '.':
            out[g == k] = (*rgb[:3], 255)
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f'{name}.png'
    Image.fromarray(out, 'RGBA').save(dst)
    return dst


def save_render(mat: np.ndarray, lit: np.ndarray, name: str) -> Path:
    img = np.zeros(mat.shape + (3,))
    for k, c in enumerate(MATS):
        img[mat == k] = np.array(FLAT[c]) * (0.35 + 0.65 * lit[mat == k, None])
    img[mat < 0] = MINT
    dst = OUT / f'{name}_render.png'
    Image.fromarray(img.astype(np.uint8)).save(dst)
    return dst


SCENES = {
    # name: (parts, azimuth, elevation, margin, zzz positions)
    'futon': (futon_parts, -22, 42, 1.0, [(31, 1), (37, 7), (42, 12)]),
    'hills': (hills_parts, 0, 16, 1.0, []),
    'fuji': (fuji_parts, 0, 14, 1.0, []),
    'fuji2': (fuji2_parts, 0, 10, 1.0, []),
    'saddle': (saddle_parts, 0, 14, 1.0, []),
    'dome': (dome_parts, 0, 12, 1.0, []),
}

if __name__ == '__main__':
    for name in sys.argv[1:] or list(SCENES):
        parts, az, el, margin, zzz = SCENES[name]
        mat, lit, dep, obj = render(parts(), az, el, margin)
        g = to_icon(mat, lit, dep, obj)
        if zzz:
            g = add_zzz(g, zzz)
        print(save_icon(g, name), save_render(mat, lit, name))
