"""home-icon: the kotatsu, modelled and lit, then brought to the set's 48x48 language. The drafts (draft.py) and the
image model's redraws (polish.py) of them read as clip art beside the real icons: flat fills, stripes painted on. A
render gives the quilt real folds and light, so the plaid follows the cloth and the shade falls where the light does.
Run:
    uv run python assets/home-icon/render.py [out_name]

The model (cm): a 76cm square board on a quilt that hangs from under it and flares to the floor, its corners bunched
into folds; three mikan on the board. Seen from above and the front left (the globe's and the computer's three-quarter),
lit from the top left. Rendered at 8x by dense surface points into a z-buffer, then each 8x8 cell takes its majority
material and mean light, and the light picks a tone in the set's ramp for that material (white highlight, body, a 50%
checker into shadow, the shadow), with the set's outline round the silhouette (plum top/left, black bottom/right).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from pc98 import palette as P

HERE = Path(__file__).parent
N, SS = 48, 8                                  # icon size, supersampling
LEG = P.get('site+')

# per material: tones from lit to dark (a pair is a 50% checker of its two letters)
RAMP = {
    'quilt': ['W', 'p', ('p', 'u'), 'u'],
    'plaid': ['k', 'k', ('k', 'h'), 'h'],
    'board': ['e', 'n', 'n', 'r'],
    'edge': ['W', 'e', 'n', 'r'],
    'mikan': ['y', 'y', 'e', 'n'],
    'leaf': ['t', 't', 't', 't'],
}
MATS = list(RAMP)
LIGHT = np.array([-0.6, 0.62, -0.5]); LIGHT /= np.linalg.norm(LIGHT)    # camera space: from the top left, toward us


def rot(az, el):
    a, e = np.radians(az), np.radians(el)
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return Rx @ Ry


def square(s, half, r):
    """A point on a rounded square's perimeter at s in [0,1) (corner radius r), and its outward normal."""
    side = 2 * (half - r)
    per = 4 * side + 2 * np.pi * r
    d = (s % 1) * per
    out = np.zeros(s.shape + (2,)); nrm = np.zeros(s.shape + (2,))
    seg = [side, np.pi * r / 2] * 4
    starts = np.cumsum([0] + seg[:-1])
    for k in range(8):
        m = (d >= starts[k]) & (d < starts[k] + seg[k])
        u = d[m] - starts[k]
        q = k // 2
        ang = q * np.pi / 2
        if k % 2 == 0:                                   # a straight side, then the corner after it
            p = np.stack([half * np.ones_like(u), -half + r + u], -1); n = np.array([1.0, 0])
            nn = np.repeat(n[None], len(u), 0)
        else:
            t = u / r
            c = np.array([half - r, half - r])
            p = c + r * np.stack([np.cos(t), np.sin(t)], -1); nn = np.stack([np.cos(t), np.sin(t)], -1)
        R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        out[m] = p @ R.T; nrm[m] = nn @ R.T
    return out, nrm


def quilt_points():
    s = np.linspace(0, 1, 1400, endpoint=False)
    t = np.linspace(0, 1, 160)
    S_, T_ = np.meshgrid(s, t)
    top, _ = square(S_, 40.0, 3.0)
    bot, bn = square(S_, 60.0, 24.0)
    corner = np.cos(4 * 2 * np.pi * (S_ - 0.125 / 1)) * 0 + 0
    # folds: soft vertical waves, deeper toward the floor and at the corners
    ang = np.arctan2(bot[..., 1], bot[..., 0])
    near_corner = np.abs(np.cos(2 * ang)) ** 6
    wave = np.sin(S_ * 2 * np.pi * 10) * (1.5 + 5.0 * near_corner)
    flare = T_ ** 1.8
    xy = top + (bot - top) * flare[..., None] + bn * (wave * flare)[..., None]
    y = 46.0 - 46.0 * T_
    P_ = np.stack([xy[..., 0], y, xy[..., 1]], -1)
    # normals by finite differences
    dS = np.gradient(P_, axis=1); dT = np.gradient(P_, axis=0)
    n = np.cross(dT, dS); n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    centre = np.stack([np.zeros_like(y), y, np.zeros_like(y)], -1)
    flip = ((P_ - centre) * n).sum(-1) < 0
    n[flip] *= -1
    # the plaid, in the cloth's own coordinates: lines along its length and across it
    u = S_ * 4 * 76 / 19                                      # ~19cm squares (an icon needs them big)
    v = T_ * 52 / 19
    plaid = (np.abs((u + 0.5) % 1 - 0.5) < 0.08) | (np.abs((v + 0.25) % 1 - 0.5) < 0.08)
    mat = np.where(plaid, MATS.index('plaid'), MATS.index('quilt'))
    return P_.reshape(-1, 3), n.reshape(-1, 3), mat.reshape(-1)


def board_points():
    g = np.linspace(-42, 42, 260)
    X, Z = np.meshgrid(g, g)
    top = np.stack([X, np.full_like(X, 49.5), Z], -1).reshape(-1, 3)
    pts = [top]; nrm = [np.repeat([[0, 1, 0]], len(top), 0)]; mat = [np.full(len(top), MATS.index('board'))]
    h = np.linspace(46.0, 49.5, 12)
    for axis, sgn in ((0, 1), (0, -1), (2, 1), (2, -1)):
        A, Hh = np.meshgrid(g, h)
        p = np.zeros(A.shape + (3,)); p[..., 1] = Hh
        p[..., axis] = 42 * sgn; p[..., 2 - axis] = A
        n = np.zeros(3); n[axis] = sgn
        pts.append(p.reshape(-1, 3)); nrm.append(np.repeat([n], p.size // 3, 0)); mat.append(np.full(p.size // 3, MATS.index('edge')))
    return np.concatenate(pts), np.concatenate(nrm), np.concatenate(mat)


def mikan_points():
    pts, nrm, mat = [], [], []
    for cx, cz in ((-14, 10), (13, 12), (-1, -11)):
        r = 12.0
        th, ph = np.meshgrid(np.linspace(0, np.pi, 90), np.linspace(0, 2 * np.pi, 180))
        n = np.stack([np.sin(th) * np.cos(ph), np.cos(th), np.sin(th) * np.sin(ph)], -1).reshape(-1, 3)
        n[:, 1] *= 0.82
        p = np.array([cx, 49.5 + r * 0.8, cz]) + n * r
        pts.append(p); nrm.append(n / np.linalg.norm(n, axis=1, keepdims=True)); mat.append(np.full(len(p), MATS.index('mikan')))
        lf = np.array([cx + 2.5, 49.5 + r * 1.65, cz - 1]) + np.random.default_rng(1).normal(0, 1.0, (200, 3)) * [1.6, 0.3, 0.9]
        pts.append(lf); nrm.append(np.repeat([[0, 1, 0]], 200, 0)); mat.append(np.full(200, MATS.index('leaf')))
    return np.concatenate(pts), np.concatenate(nrm), np.concatenate(mat)


def render(az=38, el=28):
    parts = [quilt_points(), board_points(), mikan_points()]
    P_ = np.concatenate([p[0] for p in parts]); Nn = np.concatenate([p[1] for p in parts])
    M = np.concatenate([p[2] for p in parts])
    R = rot(az, -el)                                          # looking down at it
    V = P_ @ R.T; Nv = Nn @ R.T
    lam = np.clip((Nv * LIGHT).sum(1), 0, 1) * 0.85 + 0.15
    # fit to the icon: x right, y up -> rows
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    W = N * SS
    lo, hi = np.array([x.min(), y.min()]), np.array([x.max(), y.max()])
    scale = (W - 2 * SS) / max(hi - lo)
    cx = (x - (lo[0] + hi[0]) / 2) * scale + W / 2
    cy = W / 2 - (y - (lo[1] + hi[1]) / 2) * scale + SS * 1.5
    ix, iy = np.round(cx).astype(int), np.round(cy).astype(int)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < W)
    order = np.argsort(-z[ok])                                # far first, near last wins
    zb = np.full((W, W), -1, int)
    idx = np.nonzero(ok)[0][order]
    zb[iy[idx], ix[idx]] = idx
    mat = np.where(zb >= 0, M[np.maximum(zb, 0)], -1)
    lit = np.where(zb >= 0, lam[np.maximum(zb, 0)], 0)
    return mat, lit


def to_icon(mat, lit, gamma=1.0):
    g = np.full((N, N), '.', dtype='<U1')
    for j in range(N):
        for i in range(N):
            m = mat[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS].ravel()
            l = lit[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS].ravel()
            if (m >= 0).sum() < SS * SS * 0.45:
                continue
            vals, cnt = np.unique(m[m >= 0], return_counts=True)
            k = vals[np.argmax(cnt)]
            qi, pi = MATS.index('quilt'), MATS.index('plaid')
            if k in (qi, pi):
                nq, npl = (m == qi).sum(), (m == pi).sum()
                k = pi if npl > 0.34 * (nq + npl) else qi
            li = MATS.index('leaf')
            if (m == li).sum() >= 24:
                k = li
            L = l[m == k].mean() ** gamma
            ramp = RAMP[MATS[k]]
            tone = ramp[0] if L > 0.86 else ramp[1] if L > 0.55 else ramp[2] if L > 0.32 else ramp[3]
            if isinstance(tone, tuple):
                tone = tone[(i + j) % 2]
            g[j, i] = tone
    mk = np.isin(g, ['y', 'e']) & ~np.isin(g, [])
    bd = (g == 'n')
    mpad = np.pad(mk, 1)
    near = mpad[:-2, 1:-1] | mpad[2:, 1:-1] | mpad[1:-1, :-2] | mpad[1:-1, 2:]
    g[bd & near & ~mk] = 'r'
    solid = g != '.'
    pad = np.pad(solid, 1)
    up, down = pad[:-2, 1:-1], pad[2:, 1:-1]
    left, right = pad[1:-1, :-2], pad[1:-1, 2:]
    edge = solid & ~(up & down & left & right)
    g[edge & (~down | ~right)] = 'K'
    g[edge & down & right & (~up | ~left)] = 'u'
    return g


def save(g, name):
    out = np.zeros((N, N, 4), np.uint8)
    for k, rgb in LEG.items():
        if k != '.':
            out[g == k] = (*rgb[:3], 255)
    dst = HERE / 'out' / f'{name}_recolor.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out, 'RGBA').save(dst)
    return dst


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'kotatsu3d'
    mat, lit = render()
    print(save(to_icon(mat, lit), name))
    cols = {'quilt': (136, 153, 255), 'plaid': (255, 170, 187), 'board': (204, 136, 68), 'edge': (153, 68, 34),
            'mikan': (255, 170, 60), 'leaf': (0, 119, 102)}
    img = np.zeros(mat.shape + (3,))
    for k, c in enumerate(MATS):
        img[mat == k] = np.array(cols[c]) * (0.35 + 0.65 * lit[mat == k, None])
    img[mat < 0] = (0, 238, 187)
    Image.fromarray(img.astype(np.uint8)).save(HERE / 'out' / f'{name}_render.png')
