"""vp-check: do the painted edges of every object meet the scene's vanishing points?

Passages declare the camera and each object's straight edges on `cv.persp` (see canvas.Persp). For every declared
edge the check scans the painted picture across a narrow band around it, collects the ink transitions there, and
fits the straight edge they really make (RANSAC over pixel transitions, then least squares on the inliers). That
fitted edge, not the declaration, is what gets measured:

  miss  how far the fitted edge, extended, passes from its vanishing point (px at 1x). For level and plumb edges,
        the drift from level/plumb over the edge's own length.
  off   how far the painted edge strays from the true line over its own length: the ray from the vanishing point
        through the edge's middle (or the level/plumb line through it). This is what the eye sees, and what passes
        or fails: a short edge can't aim at a far point better than its pixels allow, so `miss` grows with
        distance, `off` doesn't.

Coordinates are pixel indices (a pixel's centre is its index; a transition between rows y and y+1 is at y + 0.5).
"""

import numpy as np
from PIL import Image, ImageDraw

BAND = 2.5          # px either side of a declaration to look for the painted edge
INLIER = 0.75       # px from a candidate line to count as on it (a stair-stepped edge strays up to 0.5)
MIN_COVER = 0.5     # share of the scanned columns (rows) that must hold the edge


def _transitions(idx, p0, p1, band=BAND):
    """Ink changes across the edge near the segment p0-p1, as (x, y, scanline) at transition positions."""
    (x0, y0), (x1, y1) = p0, p1
    h, w = idx.shape
    dx, dy = x1 - x0, y1 - y0
    pts, lines = [], 0
    if abs(dx) >= abs(dy):                      # mostly level: scan columns, transitions between rows
        for x in range(int(np.ceil(min(x0, x1))), int(np.floor(max(x0, x1))) + 1):
            if not 0 <= x < w:
                continue
            lines += 1
            yd = y0 + (x - x0) * dy / dx if dx else y0
            for y in range(max(int(np.floor(yd - band)), 0), min(int(np.ceil(yd + band)), h - 1)):
                if idx[y, x] != idx[y + 1, x]:
                    pts.append((float(x), y + 0.5, x))
    else:                                       # mostly upright: scan rows, transitions between columns
        for y in range(int(np.ceil(min(y0, y1))), int(np.floor(max(y0, y1))) + 1):
            if not 0 <= y < h:
                continue
            lines += 1
            xd = x0 + (y - y0) * dx / dy
            for x in range(max(int(np.floor(xd - band)), 0), min(int(np.ceil(xd + band)), w - 1)):
                if idx[y, x] != idx[y, x + 1]:
                    pts.append((x + 0.5, float(y), y))
    return pts, lines


def _dist(pts, c, u):
    """Distances of points from the line through c along unit u."""
    d = pts - c
    return np.abs(d[:, 0] * u[1] - d[:, 1] * u[0])


def _fit(pts, p0, p1):
    """The straight edge the transitions make: (centre, unit direction, t0, t1, scanlines covered) or None."""
    if len(pts) < 3:
        return None
    P = np.array([(x, y) for x, y, _ in pts])
    keys = np.array([k for _, _, k in pts])
    d0 = np.array(p1) - np.array(p0)
    u0 = d0 / (np.hypot(*d0) or 1)
    best = None
    n = len(P)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if keys[i] != keys[j]]
    if len(pairs) > 3000:
        rng = np.random.default_rng(0)
        pairs = [pairs[k] for k in rng.choice(len(pairs), 3000, replace=False)]
    decl_d = _dist(P, np.array(p0), u0)
    for i, j in pairs:
        dd = P[j] - P[i]
        L = np.hypot(*dd)
        if L < 2:
            continue
        u = dd / L
        if abs(u @ u0) < 0.8:                   # within ~37 degrees of the declaration
            continue
        on = _dist(P, P[i], u) <= INLIER
        cover = len(set(keys[on]))
        score = (cover, -decl_d[on].mean())
        if best is None or score > best[0]:
            best = (score, P[i], u)
    if best is None:
        return None
    _, c, u = best
    for _ in range(2):                          # refine: one point per scanline, the nearest; total least squares
        dist = _dist(P, c, u)
        keep = {}
        for k, dk, p in zip(keys, dist, P):
            if dk <= INLIER and (k not in keep or dk < keep[k][0]):
                keep[k] = (dk, p)
        Q = np.array([p for _, p in keep.values()])
        if len(Q) < 3:
            return None
        c = Q.mean(0)
        _, _, vt = np.linalg.svd(Q - c)
        u = vt[0] if vt[0] @ u0 >= 0 else -vt[0]
    t = (Q - c) @ u
    return c, u, float(t.min()), float(t.max()), len(Q)


def measure(cv, tol=1.0):
    """Measure every declared edge on the finished picture. Returns a list of result dicts."""
    ps = cv.persp
    out = []
    for e in ps.edges:
        pts, lines = _transitions(cv.idx, e['p0'], e['p1'])
        fit = _fit(pts, e['p0'], e['p1'])
        r = dict(e)
        r['lines'] = lines
        if fit is None:
            r.update(status='unseen', cover=0.0)
            out.append(r)
            continue
        c, u, t0, t1, cov = fit
        e0, e1 = c + u * t0, c + u * t1
        m = (e0 + e1) / 2
        r.update(c=c, u=u, e0=e0, e1=e1, length=float(t1 - t0), cover=cov / max(lines, 1))
        to = e['to']
        if to == 'h':
            r['kind'] = 'level'
            r['miss'] = float(abs(e1[1] - e0[1]))
            r['off'] = float(max(abs(e0[1] - m[1]), abs(e1[1] - m[1])))
            r['ideal'] = (m, np.array([1.0, 0.0]))
        elif to == 'v':
            r['kind'] = 'plumb'
            r['miss'] = float(abs(e1[0] - e0[0]))
            r['off'] = float(max(abs(e0[0] - m[0]), abs(e1[0] - m[0])))
            r['ideal'] = (m, np.array([0.0, 1.0]))
        else:
            vp = np.array(ps.vps[to] if isinstance(to, str) else to, float)
            r['kind'] = to if isinstance(to, str) else 'own VP'
            r['vp'] = vp
            if not isinstance(to, str) and ps.horizon is not None:
                r['vp_off_horizon'] = float(abs(vp[1] - ps.horizon))
            r['miss'] = float(_dist(vp[None], c, u)[0])
            g = m - vp
            gu = g / (np.hypot(*g) or 1)
            r['off'] = float(max(_dist(e0[None], vp, gu)[0], _dist(e1[None], vp, gu)[0]))
            r['ideal'] = (vp, gu)
        if r['cover'] < MIN_COVER:
            r['status'] = 'unseen'
        elif r['off'] <= tol and r.get('vp_off_horizon', 0) <= tol:
            r['status'] = 'ok'
        else:
            r['status'] = 'FAIL'
        out.append(r)
    return out


def report(results, tol):
    lines = [f'vp-check: tolerance {tol:.1f}px (the painted edge may stray at most this far from its true line, '
             f'measured over its own length at 1x)', '']
    lines.append(f'{"object":<13}{"edge":<26}{"to":<8}{"len":>5}{"cover":>7}{"miss":>8}{"off":>7}  status')
    groups = {}
    for r in results:
        groups.setdefault((not r['control'], r['obj']), []).append(r)
    for (_, obj), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        for r in rs:
            seg = f'({r["p0"][0]:.0f},{r["p0"][1]:.0f})-({r["p1"][0]:.0f},{r["p1"][1]:.0f})'
            to = r['to'] if isinstance(r['to'], str) else 'own'
            if r['status'] == 'unseen' and 'off' not in r:
                lines.append(f'{obj + ("*" if r["control"] else ""):<13}{seg:<26}{to:<8}{"":>5}{r["cover"]:>7.2f}'
                             f'{"":>8}{"":>7}  unseen')
                continue
            extra = f'  (its VP is {r["vp_off_horizon"]:.1f}px off the horizon)' if 'vp_off_horizon' in r else ''
            lines.append(f'{obj + ("*" if r["control"] else ""):<13}{seg:<26}{to:<8}{r["length"]:>5.0f}'
                         f'{r["cover"]:>7.2f}{r["miss"]:>8.1f}{r["off"]:>7.2f}  {r["status"]}{extra}')
    n = {s: sum(r['status'] == s for r in results) for s in ('ok', 'FAIL', 'unseen')}
    ctl = [r for r in results if r['control'] and 'off' in r and r['status'] != 'unseen']
    lines += ['', f'* = control (the base picture\'s own edges). {n["ok"]} ok, {n["FAIL"]} FAIL, {n["unseen"]} unseen.']
    if ctl:
        lines.append(f'controls: worst off {max(r["off"] for r in ctl):.2f}px, '
                     f'median {float(np.median([r["off"] for r in ctl])):.2f}px')
    return lines


VP_COL = (110, 255, 110)        # the vanishing points' own lines: the true rays, the horizon
OBJ_COL = (255, 110, 230)       # objects' painted edges, extended
CTL_COL = (90, 210, 255)        # the base picture's edges (controls), extended
BAD_COL = (255, 70, 60)
HZ_COL = (255, 230, 80)


def overlay(cv, results, z=3, box=None, title='', font=None):
    """The picture, dimmed, with the horizon, the VPs, every true ray and every painted edge extended."""
    x0, y0, x1, y1 = box or (0, 0, cv.w, cv.h)
    pic = Image.fromarray(cv.rgb()).crop((x0, y0, x1, y1))
    pic = pic.resize((pic.width * z, pic.height * z), Image.NEAREST)
    pic = Image.blend(pic, Image.new('RGB', pic.size, (10, 8, 20)), 0.45)
    d = ImageDraw.Draw(pic)

    def S(p):
        return ((p[0] - x0 + 0.5) * z, (p[1] - y0 + 0.5) * z)

    ps = cv.persp
    if ps.horizon is not None:
        d.line([S((x0 - 10, ps.horizon)), S((x1 + 10, ps.horizon))], fill=HZ_COL, width=1)
        d.text(S((x0 + 2, ps.horizon - 5)), 'horizon', fill=HZ_COL, font=font)
    for name, (vx, vy) in ps.vps.items():
        sx, sy = S((vx, vy))
        d.line([(sx - 8, sy), (sx + 8, sy)], fill=HZ_COL, width=2)
        d.line([(sx, sy - 8), (sx, sy + 8)], fill=HZ_COL, width=2)
        d.text((sx + 6, sy + 4), f'VP {name} ({vx:.0f},{vy:.0f})', fill=HZ_COL, font=font)
    labelled = set()
    for r in results:
        if 'off' not in r:
            continue
        col = BAD_COL if r['status'] == 'FAIL' else (CTL_COL if r['control'] else OBJ_COL)
        e0, e1 = r['e0'], r['e1']
        a, g = r['ideal']
        if r['kind'] in ('level', 'plumb'):
            ext = 18
            d.line([S(e0 - r['u'] * ext), S(e1 + r['u'] * ext)], fill=col, width=1)
            d.line([S(a - g * (r['length'] / 2 + ext)), S(a + g * (r['length'] / 2 + ext))], fill=VP_COL, width=1)
        else:
            vp = r['vp']
            far = e0 if np.hypot(*(e0 - vp)) > np.hypot(*(e1 - vp)) else e1
            d.line([S(vp), S(far + g * 6)], fill=VP_COL, width=1)                  # the true ray
            tv = float((vp - r['c']) @ r['u'])                                     # the painted edge, extended
            near = r['c'] + r['u'] * tv
            d.line([S(far), S(near)], fill=col, width=1)
        d.line([S(e0), S(e1)], fill=col, width=3)
        m = (e0 + e1) / 2
        txt = f'{r["off"]:.1f}' if r['status'] != 'FAIL' else f'{r["off"]:.1f}!'
        if r['obj'] not in labelled:
            txt = f'{r["obj"]} {txt}'
            labelled.add(r['obj'])
        tx, ty = S(m)
        d.text((tx + 4, ty + 2), txt, fill=col, font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    if title:
        d.text((8, 8), title, fill=(240, 240, 240), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    return pic
