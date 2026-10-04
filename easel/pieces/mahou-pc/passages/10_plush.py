# 10 plush: Panda's plush replaces the santa-hat seal at the head of the bed, tucked in the same way with its
# paws over the hem. Its light is the room's: the window and the CRT are both to its right, so the right side
# of every round form takes the glow and the left falls into the corner's shade.

cv.masks = getattr(cv, 'masks', {})

# the seal, hat and all (its outline included), down to the hem
SEAL = cv.m_poly([(39, 125), (47, 125), (50, 132), (57, 136), (63, 140), (66, 146), (66, 158), (64, 162), (63, 178),
                  (34, 178), (33, 160), (34, 147), (36, 138), (37, 129)])

# ---- the panda's forms (ellipsoids) and the light on them
def lambert(cx, cy, rx, ry, L=(0.75, -0.45, 0.5)):
    ys, xs = np.mgrid[0:cv.h, 0:cv.w]
    nx, ny = (xs - cx) / rx, (ys - cy) / ry
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    l = np.array(L, float) / np.linalg.norm(L)
    return nx * l[0] + ny * l[1] + nz * l[2]


def tilted(cx, cy, rx, ry, deg, n=28):
    a = np.radians(deg)
    return [(cx + rx * np.cos(t) * np.cos(a) - ry * np.sin(t) * np.sin(a),
             cy + rx * np.cos(t) * np.sin(a) + ry * np.sin(t) * np.cos(a))
            for t in np.linspace(0, 2 * np.pi, n, endpoint=False)]


FUR = [(0.95, GLOW), (0.86, Tile('1/2', PAPER, GLOW)), (0.22, PAPER), (0.10, Tile('1/2', CURTAIN, PAPER)),
       (-0.35, CURTAIN), (-9, Tile('1/2', WALL, CURTAIN))]
INK = [(0.78, Tile('1/2', DARK, SLATE)), (0.48, DARK), (0.32, Tile('1/2', BLACK, DARK)), (-9, BLACK)]


def form(mask, s, bands):
    done = np.zeros_like(mask)
    for th, c in bands:
        m = mask & (s >= th) & ~done
        cv.fill(m, c)
        done |= m


YY, XX = np.mgrid[0:cv.h, 0:cv.w]
HX, HY, HRX, HRY = 49, 148, 14, 11.5                 # head
HEAD = cv.m_ellipse(HX, HY, HRX, HRY)
EARS = [(39, 137.5), (59, 137.5)]
EAR = [cv.m_ellipse(x, y, 4.5, 4.5) for x, y in EARS]
SHOULDERS = cv.m_ellipse(49, 166, 15, 9) & (YY <= 178)
CHEST = cv.m_ellipse(49, 170, 8, 9) & (YY <= 178)
PAWS = [(41, 175.5), (57, 175.5)]
PAW = [cv.m_ellipse(x, y, 3.5, 2.5) for x, y in PAWS]
PANDA_SIL = HEAD | EAR[0] | EAR[1] | SHOULDERS | CHEST | PAW[0] | PAW[1]

# ---- the seal's leftovers (its pompom and hat tip, a sliver at its right): rebuilt from what's around them. The
# corner post and the slate headboard post are vertical grain, so they come back from 8 rows up (same tile phase);
# the headboard behind is horizontal, so it comes back from 8 px to its right.
rest = SEAL & ~PANDA_SIL
clean = ~SEAL


def rebuild(sel, dx, dy):
    """Each pixel takes the nearest clean one 8 px along (dx, dy), in an order that keeps every source clean."""
    ys, xs = np.nonzero(sel)
    for i in np.argsort(ys if dy else -xs, kind='stable'):
        y, x = ys[i], xs[i]
        k = 1
        while not clean[y + k * dy, x + k * dx]:
            k += 1
        cv.idx[y, x] = cv.idx[y + k * dy, x + k * dx]
        clean[y, x] = True


BOARD = (YY >= 134) & (XX >= 51)
rebuild(rest & ~BOARD, 0, -8)
rebuild(rest & BOARD, 8, 0)

# ---- paint, back to front: shoulders and arms, chest, head, ears, paws
form(SHOULDERS, lambert(49, 166, 15, 9), INK)
form(CHEST, lambert(49, 168, 8, 9) - 0.15, FUR)                       # under the chin: a step darker
form(HEAD, lambert(HX, HY, HRX, HRY), FUR)
for (x, y), m in zip(EARS, EAR):
    form(m & ~HEAD | m & (YY < y - 1), lambert(x, y, 4.5, 4.5), INK)
for (x, y), m in zip(PAWS, PAW):
    form(m, lambert(x, y, 3.5, 2.5), INK)

# chin shadow on the chest: the head's underside, one row, broken
CHIN = cv.m_edge(HEAD, 'bottom', inside=False) & CHEST
cv.tile(CHIN, '1/2', CURTAIN, WALL)

# the eye patches lean out at the bottom, the way every panda toy's do
PATCH = [cv.m_poly(tilted(43.5, 150.5, 2.6, 4.0, 28)), cv.m_poly(tilted(54.5, 150.5, 2.6, 4.0, -28))]
for m in PATCH:
    cv.fill(m & HEAD, BLACK)
# eyes: a bead in each patch, the catchlight on the window's side
cv.stamp(44, 148, '''
DE
DD
''', {'D': DARK, 'E': WHITE})
cv.stamp(54, 148, '''
DE
DD
''', {'D': DARK, 'E': WHITE})
# nose and mouth (the little "w")
cv.stamp(48, 154, '''
KKK
.K.
K.K
''', {'K': BLACK})
# blush, under the patches
cv.dots([(41, 156), (42, 156)], DESK_SHADE)
cv.dots([(56, 156), (57, 156)], DESK_SHADE)

# ---- line: a dark contour all round, lifted a step where the glow rims it
OUT = cv.m_edge(PANDA_SIL, inside=True)
s_out = lambert(HX, HY + 6, 16, 22)
cv.fill(OUT & (s_out < 0.62), BLACK)
cv.fill(OUT & (s_out >= 0.62) & cv.m_where(PAPER, GLOW, CURTAIN), DARK)
# head over shoulders, ears behind head: the inner seams
cv.fill(cv.m_edge(HEAD, 'bottom', inside=True) & SHOULDERS & ~CHEST, BLACK)

# ---- the hem: the seal's dark under-body on the blanket goes; the panda sits on it with a contact shadow
HEM = cv.m_rect(44, 179, 63, 181) & cv.m_where(BLACK, DARK, WOOD, WALL_SHADE, WALL, DESK_SHADE)
cv.fill(HEM, BEDSPREAD)
UNDER = cv.m_edge(PANDA_SIL, 'bottom', inside=False) & cv.m_rect(34, 176, 64, 182)
cv.fill(UNDER, WOOD)
cv.tile(cv.m_edge(PANDA_SIL | UNDER, 'bottom', inside=False) & cv.m_rect(34, 177, 64, 183), '1/2', BEDSPREAD, WOOD)

PLUSH = PANDA_SIL.copy()
cv.masks['plush'] = PLUSH
