# 06 the city through the glass. It continues the scene above the seam column for column (the towers, the alley,
# the pink signs, the cyan sign), seen below eye level: lit windows as 1px dashes, signs as hard flats with a frame,
# a faint street glow at the bottom. Only the glass that the tower and CRT don't cover.
G = cv.m_rect(0, 0, 175, GLASS_B - 1) & ~SIL['crt'] & ~SIL['tower'] & ~cv.m_rect(MULL[0], 0, MULL[1], GLASS_B)

def g(mask, c):
    cv.fill(mask & G, c)

def windows(x0, x1, y0, y1, dx, dy, h, lit, cols, phase=0):
    """A grid of 1px-wide window slits, h tall, every dx/dy; each lit with probability `lit`."""
    for y in range(y0 + phase, y1 + 1, dy):
        for x in range(x0, x1 + 1, dx):
            if rng.random() < lit:
                g(cv.m_rect(x, y, x, min(y + h - 1, y1)), cols[rng.integers(len(cols))])

# building faces and the dark between them
g(cv.m_rect(0, 0, 19, 24), NV); g(cv.m_rect(21, 0, 29, 24), NV)
g(cv.m_rect(31, 0, 54, 24), AB)
g(cv.m_rect(101, 0, 118, 24), AB)
g(cv.m_rect(146, 0, 175, 24), AB)
# a lower block in the alley, its roof edge catching the street light
g(cv.m_rect(66, 9, 98, 24), AB); g(cv.m_rect(66, 9, 98, 9), DU)
# window grids (the scene above uses 1px slits, columns every 4, in amber and pale)
windows(32, 53, 0, 24, 4, 4, 3, 0.55, [AM, PL, PL])
windows(1, 18, 3, 24, 5, 5, 2, 0.25, [AM, PL])
windows(102, 110, 0, 24, 3, 4, 2, 0.5, [PL, AM])
windows(67, 97, 11, 24, 4, 3, 1, 0.45, [AM, AM, PL, PK])
windows(124, 144, 2, 24, 5, 3, 1, 0.35, [AM, PL])
# pink vertical sign at x 55-62: frame W1, flat PK, black core with a pale tube; it ends at y 6
g(cv.m_rect(55, 0, 62, 7), W1); g(cv.m_rect(56, 0, 61, 6), PK); g(cv.m_rect(57, 0, 60, 4), K)
g(cv.m_rect(58, 0, 59, 4), PL)
# pink box sign at x 111-118, carried on down to y 5
g(cv.m_rect(111, 0, 118, 6), W1); g(cv.m_rect(112, 0, 118, 5), PK); g(cv.m_rect(113, 0, 117, 4), K)
g(cv.m_rect(114, 2, 116, 2), PK)
# the cyan striped sign at x 147-175: dark blue ground, cyan tubes, ends at y 9 with a bracket below
g(cv.m_rect(147, 0, 175, 9), DB)
for y in (0, 3, 6, 9):
    g(cv.m_rect(149, y, 175, y), CY)
g(cv.m_rect(148, 0, 148, 9), CY)
g(cv.m_rect(150, 10, 151, 12), DU); g(cv.m_rect(172, 10, 173, 12), DU)
windows(150, 174, 14, 24, 4, 4, 2, 0.4, [AM, PL])
# street glow rising from below: banded tiles over the dark at the foot of the glass
cv.fill(cv.m_rect(0, 21, 175, 22) & G & cv.m_where(K), T('1/4', None, DU))
cv.fill(cv.m_rect(0, 23, 175, 24) & G & cv.m_where(K), T('1/2', None, DU))
