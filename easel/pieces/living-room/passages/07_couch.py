# 07 the couch, comfy (the user: the old leather ones were "weird" and "cold"): a soft two-seater in moss corduroy,
# its back to the glass and facing the kotatsu, nearer us than the old one so the far sliding door stays clear to the
# floor. Constructed like the bedroom's furniture: boxes in the camera, each visible face a flat polygon in its
# plane's ink (top light, front mid, the arm's inside face a step darker), cushion faces bowed a little and their
# corners eased, dark seams between cushions, a black silhouette, piping lit along the edges that face the glass.
F0 = FLOOR_Y
COUCH = np.zeros((cv.h, cv.w), bool)
CPART = {}


def bowed(P0, P1, P2, P3, bulge, n=8):
    """A face (four 3D corners, in order) as a polygon whose edges bow out by `bulge` cm (along the face, away from its
    centre) at their middles: a plump cushion's outline."""
    pts = []
    C = (P0 + P1 + P2 + P3) / 4
    for A, B in ((P0, P1), (P1, P2), (P2, P3), (P3, P0)):
        for k in range(n):
            t = k / n
            M = A + (B - A) * t
            out = M - C
            out_dir = out / max(np.linalg.norm(out), 1e-6)
            M = M + out_dir * bulge * np.sin(np.pi * t)
            pts.append(pf(M))
    return pts


def cbox(name, x0, x1, y0, y1, z0, z1, inks, bulge=1.5, faces=('near', 'front', 'top')):
    """A box's visible faces from the camera: near (-Z), front (-X), top (+Y), each depth-tested on its own plane."""
    c = lambda x, y, z: np.array([x, y, z], float)
    F = {
        'near': (c(x0, y1, z0), c(x1, y1, z0), c(x1, y0, z0), c(x0, y0, z0)),
        'front': (c(x0, y1, z1), c(x0, y1, z0), c(x0, y0, z0), c(x0, y0, z1)),
        'top': (c(x0, y1, z1), c(x1, y1, z1), c(x1, y1, z0), c(x0, y1, z0)),
    }
    masks = {}
    k = len(CPART) + 1
    for fi, f in enumerate(faces):
        m = cv.m_poly(bowed(*F[f], bulge))
        dep = np.where(m, plane_depth(F[f][0], F[f][1], F[f][2]), np.inf)
        with occluded(dep - (0.4 if f == 'top' else 0.0)) as oc:
            cv.fill(m, inks[f])
        OWNER[oc.visible] = k * 4 + fi
        masks[f] = fi
    CPART[name] = (k, masks)
    return k, masks


def resolve_parts():
    """Each part's visible pixels, per face, from who won the depth test."""
    for name, (k, faces) in list(CPART.items()):
        fm = {f: OWNER == k * 4 + fi for f, fi in faces.items()}
        w = np.zeros((cv.h, cv.w), bool)
        for m in fm.values():
            w |= m
        CPART[name] = (w, fm)


OWNER = np.zeros((cv.h, cv.w), np.int32)
LIGHT, MID, SHADE, DEEP = DESK, DESK_SHADE, WOOD, BLACK
INK = {'top': LIGHT, 'front': MID, 'near': MID}
# far to near: the arm at the far end, the back cushions, the base, the seats
arm, arm_m = cbox('arm', 100, 178, F0 + 8, F0 + 50, 166, 181, {'top': LIGHT, 'front': MID, 'near': MID}, bulge=2.6)
for i, (z0, z1) in enumerate(((98, 166), (24, 98))):
    cbox(f'back{i}', 148, 176, F0 + 42, F0 + 86, z0 + 0.5, z1 - 0.5, INK, bulge=3.0)
base, base_m = cbox('base', 100, 176, F0 + 8, F0 + 26, 10, 166, {'top': MID, 'front': MID, 'near': MID},
                    bulge=0.4, faces=('front',))
for i, (z0, z1) in enumerate(((98, 166), (24, 98))):
    cbox(f'seat{i}', 99, 150, F0 + 26, F0 + 44, z0 + 0.5, z1 - 0.5, INK, bulge=2.6)

resolve_parts()
COUCH = np.zeros((cv.h, cv.w), bool)
for _w, _m in CPART.values():
    COUCH |= _w
# planes: tops mid rose with the light along their front edge (piping), fronts a deeper rose-brown, the back cushions'
# faces shading down into the seat, the plinth darkest at its foot
for k, (w, m) in CPART.items():
    if 'top' in m:
        piping = m['top'] & cv.m_edge(m['top'], 'bottom', inside=True)
        cv.fill(piping, MID)                                   # the cushion's welt where its top turns down
        cv.fill(m['top'] & (cv.dist_from(piping, 3) == 1), PAPER)   # and the light just above it
    if 'front' in m and k.startswith('back'):
        _ys = np.nonzero(m['front'])[0]
        if len(_ys):
            cv.fill(m['front'], MID)
            _lo = np.percentile(_ys, 55)
            cv.tile(m['front'] & (YY > _lo), '1/4', MID, SHADE)
    if 'front' in m and k.startswith('seat'):
        cv.fill(m['front'] & cv.m_edge(m['front'], 'top', inside=True), MID)   # the seat's rounded lip
for k in ('base',):
    w, m = CPART[k]
    if 'front' in m:
        _ys = np.nonzero(m['front'])[0]
        if len(_ys):
            cv.tile(m['front'] & (YY > np.percentile(_ys, 55)), '1/2', MID, SHADE)
# the window behind: a rim of light along the back cushions' and the arm's tops
for k in ('back0', 'back1', 'arm'):
    w, m = CPART[k]
    if 'top' in m:
        cv.fill(m['top'] & cv.m_edge(m['top'], 'top', inside=True), PAPER)
# seams: a line wherever two parts meet (on the nearer one), and the silhouette
_own = np.zeros((cv.h, cv.w), np.int16)
for i, (k, (w, m)) in enumerate(CPART.items()):
    _own[w] = i + 1
_nb = [np.roll(_own, s_, a_) for s_ in (1, -1) for a_ in (0, 1)]
seam = (_own > 0) & np.any([(n_ != _own) & (n_ > 0) for n_ in _nb], axis=0)
cv.fill(seam, SHADE)
cv.fill(cv.m_edge(COUCH, 'all', inside=True), DEEP)

# ---- two plump pillows leaning in the far corner, against the back cushion and the arm: orange with a cream band,
# and cream with blue stripes; each a bowed square in its own tilted plane
def pillow(cx, cz, w, h, lean, turn, inks, stripes=None):
    c = np.array([cx, F0 + 44 + h / 2 * np.cos(lean), cz])
    up = np.array([np.sin(lean), np.cos(lean), 0.0])          # leaning back toward the glass (+X)
    side = np.array([0.0, 0.0, 1.0])
    side = side * np.cos(turn) + np.array([np.sin(turn), 0, 0])
    P = [c - side * w / 2 + up * h / 2, c + side * w / 2 + up * h / 2, c + side * w / 2 - up * h / 2,
         c - side * w / 2 - up * h / 2]
    m = cv.m_poly(bowed(*P, 2.2, n=10))
    dep = np.where(m, plane_depth(P[0], P[1], P[2]) - 1.5, np.inf)
    oc = occluded(dep)
    oc.__enter__()
    light, mid, dark, line = inks
    cv.fill(m, mid)
    ys = np.nonzero(m)[0]
    top = ys.min(); bot = ys.max()
    cv.tile(m & (YY < top + (bot - top) * 0.35), '1/2', mid, light)
    cv.tile(m & (YY > top + (bot - top) * 0.7), '1/2', mid, dark)
    if stripes is not None:
        cv.fill(m & ((XX - YY // 2) % 6 == 0), stripes)
    cv.fill(cv.m_edge(m, 'all', inside=True), line)
    # its corners pinch: a darker pixel at each
    for p in P:
        x, y = (int(round(v)) for v in pf(p))
        if 0 <= x < cv.w and 0 <= y < cv.h and m[y, x]:
            cv.dot(x, y, line)
    oc.__exit__(None, None, None)
    return oc.visible


PILLOW_A = pillow(143, 152, 30, 30, 0.35, 0.15, (CURTAIN, GLOW, FLOOR, SLATE))
PILLOW_B = pillow(139, 132, 30, 28, 0.30, 0.10, (PAPER, DESK, BEDSPREAD, WOOD), stripes=BEDSPREAD)
COUCH |= PILLOW_A | PILLOW_B

# ---- a knitted throw over the near back cushion, hanging down its front in a soft wave
_bw, _bm = CPART['back1']
_top = _bm['top']
_drape = []
for z in np.linspace(34, 90, 24):
    _drape.append(pf((150 - 0.5, F0 + 86, z)))
for z in np.linspace(90, 34, 24):
    hem = F0 + 58 + 5 * np.sin((z - 34) / 56 * np.pi * 2.5)
    _drape.append(pf((148.5, hem, z)))
THROW = cv.m_poly(_drape) & (CPART['back1'][0] | CPART['seat1'][0])
_th_ctx = occluded(np.where(THROW, plane_depth((148, 0, 0), (148, 1, 0), (148, 0, 1)) - 1.0, np.inf))
_th_ctx.__enter__()
cv.tile(THROW, '1/2', PAPER, DESK)                       # a cream knit
cv.fill(THROW & (((YY + XX // 3) % 6) == 0), DESK_SHADE)  # its rows of stitches
cv.fill(cv.m_edge(THROW, 'bottom', inside=True), DESK_SHADE)
cv.fill(cv.m_edge(THROW, 'all', inside=True) & ~cv.m_edge(THROW, 'bottom', inside=True), WOOD)
_th_ctx.__exit__(None, None, None)
COUCH |= THROW

# feet: little honey-wood blocks under the base's front corners
for fz in (162, 92, 22):
    q = [pf((98, F0 + 8, fz - 3)), pf((104, F0 + 8, fz - 3)), pf((104, F0, fz - 3)), pf((98, F0, fz - 3))]
    m = cv.m_poly(q) & ~COUCH
    with occluded(np.where(m, fz - 3, np.inf)):
        cv.fill(m, WOOD)
        cv.fill(cv.m_edge(m, 'left'), DESK_SHADE)
        cv.fill(cv.m_edge(m, 'bottom'), BLACK)
# a contact shadow where its plinth meets the floor: the board ink a step down, two pixels deep
_under = cv.m_edge(COUCH, 'bottom', inside=False) & ~COUCH
_under |= np.roll(_under, 1, 0) & ~COUCH
for a_, b_ in {DESK: DESK_SHADE, DESK_SHADE: WOOD, WOOD: DARK, PAPER: DESK, CURTAIN: FLOOR, GLOW: CURTAIN,
               FLOOR: SLATE}.items():
    cv.idx[_under & (cv.idx == a_)] = b_
cv.masks['couch'] = COUCH
