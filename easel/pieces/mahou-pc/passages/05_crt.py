# 05 the CRT: the recess, the glass and what's on it, the chin. The glass is the room's light, so it is hard flats of
# the brightest inks; its edge dims like a real tube; the glare is a stepped curve. Everything on the face follows the
# face's own perspective through quad(), so rows of text slant with the bezel.
def quad(q, s, t):
    """Bilinear point at (s across, t down) of a quad TL TR BR BL."""
    (ax, ay), (bx, by), (cx, cy), (dx, dy) = q
    x = (1 - t) * ((1 - s) * ax + s * bx) + t * ((1 - s) * dx + s * cx)
    y = (1 - t) * ((1 - s) * ay + s * by) + t * ((1 - s) * dy + s * cy)
    return (round(x), round(y))

def qline(q, s0, s1, t, c):
    cv.line(*quad(q, s0, t), *quad(q, s1, t), c)

def qrect(q, s0, t0, s1, t1, c):
    cv.poly([quad(q, s0, t0), quad(q, s1, t0), quad(q, s1, t1), quad(q, s0, t1)], c)

glass = cv.m_poly(GLASS)
# the recess: its top and left lips throw shadow inward (dark), its bottom and right chamfers catch the glass
rc = cv.m_poly(RECESS) & ~glass
with cv.only_over(DARK, BLACK):
    cv.fill(rc & cv.m_poly([RECESS[3], RECESS[2], GLASS[2], GLASS[3]]), WALL_SHADE)       # bottom chamfer
    cv.fill(rc & cv.m_poly([RECESS[1], RECESS[2], GLASS[2], GLASS[1]]), WALL_SHADE)       # right chamfer
# the bezel's bevel: a light line just outside the recess on the top and left (it faces the room)
cv.polyline([quad(FACE, 0.03, 0.93), quad(FACE, 0.03, 0.03), quad(FACE, 0.97, 0.03)], PAPER)

# the glass: the desktop in the cool glow ink, the phosphor's edge a slate ring, corners rounded into the recess
ring = cv.m_edge(glass, 'all', inside=True)
cv.fill(ring, SLATE)
for p in GLASS:
    cv.dot(*p, DARK)
G2 = [quad(GLASS, 0.03, 0.04), quad(GLASS, 0.97, 0.04), quad(GLASS, 0.97, 0.96), quad(GLASS, 0.03, 0.96)]

# on screen: one editor window full of code (the PC is the GitHub link) on a plain desktop, two icons left of it
W = [quad(G2, 0.14, 0.07), quad(G2, 0.95, 0.07), quad(G2, 0.95, 0.93), quad(G2, 0.14, 0.93)]
cv.poly(W, SCREEN)                                               # the client, the palest ink but white
cv.polyline(W + [W[0]], SLATE)                                   # its frame
qrect(W, 0.0, 0.0, 1.0, 0.09, FLOOR)                             # title bar in the room's blue
for s in (0.08, 0.12, 0.16, 0.20, 0.24):
    cv.dot(*quad(W, s, 0.045), WHITE)                            # its title
cv.dot(*quad(W, 0.94, 0.045), SCREEN)                            # close box
qline(W, 0.03, 0.03, 0.12, GLOW); qline(W, 0.03, 0.03, 0.98, GLOW)
cv.poly([quad(W, 0.0, 0.10), quad(W, 0.06, 0.10), quad(W, 0.06, 1.0), quad(W, 0.0, 1.0)], GLOW)   # line-number gutter
# code: indented rows in three syntax inks (keyword blue, plain slate, a red string), a cursor
ROWS = [(0.10, 0.55, FLOOR), (0.16, 0.78, SLATE), (0.22, 0.62, SLATE), (0.22, 0.44, FLOOR), (0.28, 0.70, SLATE),
        (0.16, 0.30, FLOOR), (0.10, 0.18, FLOOR), (0.10, 0.66, SLATE), (0.16, 0.52, SLATE)]
for k, (s0, s1, c) in enumerate(ROWS):
    t = 0.17 + k * 0.095
    qline(W, s0, s1, t, c)
    if c == SLATE and s1 - s0 > 0.35:
        qline(W, s0 + 0.14, s0 + 0.24, t, RED)                   # a string inside the line
cv.dot(*quad(W, 0.33, 0.17 + 5 * 0.095), DARK)                   # the cursor
for t in (0.20, 0.42):                                           # desktop icons
    qrect(G2, 0.03, t, 0.08, t + 0.08, FLOOR)
    cv.dot(*quad(G2, 0.055, t + 0.14), SCREEN)
# glare: a stepped arc of white where the curved glass catches the room, top left; a glint bottom right
cv.dots([quad(GLASS, 0.06, 0.30), quad(GLASS, 0.06, 0.24), quad(GLASS, 0.08, 0.17), quad(GLASS, 0.11, 0.12),
         quad(GLASS, 0.15, 0.08), quad(GLASS, 0.20, 0.07)], WHITE)
cv.dots([quad(GLASS, 0.06, 0.42), quad(GLASS, 0.07, 0.38)], WHITE)
cv.dot(*quad(GLASS, 0.93, 0.88), WHITE)

# chin: maker's badge left, the power switch and its lit LED right, a row of knobs between
chin = [quad(FACE, 0, 0.83), quad(FACE, 1, 0.83), quad(FACE, 1, 1), quad(FACE, 0, 1)]
qline(chin, 0.08, 0.20, 0.45, PAPER)                             # badge
qline(chin, 0.08, 0.20, 0.65, WALL_SHADE)
for s in (0.58, 0.63, 0.68):
    cv.dot(*quad(chin, s, 0.45), DARK)                           # knobs, lit on top
    cv.dot(*quad(chin, s, 0.30), PAPER)
qline(chin, 0.79, 0.86, 0.45, DARK)                              # power switch
cv.dot(*quad(chin, 0.92, 0.45), SCREEN)                          # power LED
# housing: the corner where the side turns to the bezel catches the room's light; vent slots toward the back
SL = [SIDE[0], SIDE[1]]
cv.line(SL[0][0] + 1, SL[0][1] + 3, SL[1][0] + 1, SL[1][1] - 4, PAPER)
for k in range(5):
    p0 = mon(-HW + 1.5, H - 6 - k * 2.5, 12)
    p1 = mon(-HW + 2.5, H - 7 - k * 2.5, 22)
    cv.line(*p0, *p1, DARK)
