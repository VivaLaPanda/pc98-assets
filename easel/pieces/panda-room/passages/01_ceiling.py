# 01 ceiling: the 34 new rows above. On the back wall the ceiling line sits 16 rows above the old top (a 2.5m room
# under this camera, and the slim AC needs 12 of those rows for its upper body), so the strip is: the back wall's last
# rows in its own dither, the AC's intake grille, the corner posts, the side walls with the right wall's picture rail,
# and the ceiling plane receding to the VP. The window and the CRT are both below everything here: the ceiling takes
# a little of the city's glow over the window and falls off toward us, and the AC throws a soft shadow up the wall.
YY, XX = np.mgrid[0:cv.h, 0:cv.w]
J = TOP - 16                                   # the ceiling line on the back wall
CL, CR = 46, 426                               # the corner lines (the posts' black seams)
AC_X0, AC_X1, AC_TOP = 50, 193, TOP - 12


def along_vp(x0, y0, x):
    """y at x on the line from (x0, y0) through the VP: where a receding edge runs."""
    return y0 + (x - x0) * (VP[1] - y0) / (VP[0] - x0)


STRIP = YY < TOP
CEIL_EDGE = np.where(XX < CL, along_vp(CL, J, XX), np.where(XX > CR, along_vp(CR, J, XX), J))
CEIL = STRIP & (YY < CEIL_EDGE)
BELOW = STRIP & ~CEIL
AC = BELOW & (XX >= AC_X0) & (XX <= AC_X1) & (YY >= AC_TOP)
POST_L = BELOW & (XX >= 37) & (XX <= np.where(YY < AC_TOP, 58, 49))
POST_R = BELOW & (XX >= 412) & (XX <= 437)
LEFT_WALL = BELOW & (XX < 37)
RIGHT_WALL = BELOW & (XX > 437)
BACK_WALL = BELOW & ~AC & ~POST_L & ~POST_R & ~LEFT_WALL & ~RIGHT_WALL


def clone_from(mask, src_ok, dx, dy):
    """Each pixel takes the first allowed source k steps of (dx, dy) away (8px steps keep the tiles' phase)."""
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        k = 1
        while True:
            sy, sx = y + k * dy, x + k * dx
            if not (0 <= sy < cv.h and 0 <= sx < cv.w):
                break
            if src_ok[sy, sx]:
                cv.idx[y, x] = cv.idx[sy, sx]
                break
            k += 1


# the back wall: each column's own dither from 16 rows down (the old top rows are clean wall from x 196 to the right
# post); above the AC, the nearest clean column with the same 8px phase
WALL_SRC = OLD & (YY < TOP + 16) & (XX >= 196) & (XX < 412)
for y, x in zip(*np.nonzero(BACK_WALL)):
    sx = x if x >= 196 else x + 8 * int(np.ceil((196 - x) / 8))
    cv.idx[y, x] = cv.idx[y + 16, sx]
# the posts are vertical grain: from below, skipping the AC and the picture rail
RAIL = (YY >= TOP + 18) & (YY <= TOP + 27)
clone_from(POST_L | POST_R, OLD & ~RAIL & ~(XX >= AC_X0) | OLD & ~RAIL & (XX >= 412), 0, 8)
clone_from(POST_L & (XX >= 50), OLD & (YY >= TOP + 28), 0, 8)

# the side walls: the left a WALL/WALL_SHADE dither darkening into the corner (as the old top rows run, 6 -> 7);
# the right WALL_SHADE with a sparse dot, and its picture rail climbing toward us (its top edge through (470, TOP+3))
cv.grad(LEFT_WALL, WALL, WALL_SHADE, cv.lin((0, 0), (36, 0)) * 0.6 + 0.15, steps=P.STEPS_FINE)
cv.tile(RIGHT_WALL, '1/16', WALL_SHADE, DESK_SHADE)
RAIL_TOP = along_vp(CR, TOP + 18, XX)
R_RAIL = RIGHT_WALL & (YY >= RAIL_TOP) & (XX >= 466)
cv.fill(R_RAIL, DESK_SHADE)
cv.fill(cv.m_edge(R_RAIL, 'top', inside=True), DARK)

# the AC's upper body: its intake grille, slats repeating the old top row's (grille texture over a dark gap), up to a
# rounded lip and the outline; its end caps carry on from below
for y in range(AC_TOP + 2, TOP):
    src = TOP + (0 if (TOP - y) % 2 == 0 else 1)
    cv.idx[y, AC_X0 + 1:AC_X1 - 3] = cv.idx[src, AC_X0 + 1:AC_X1 - 3]
clone_from(AC & ((XX <= AC_X0) | (XX >= AC_X1 - 3)), OLD & (YY < TOP + 12), 0, 8)
GRILLE = AC & (YY >= AC_TOP + 2) & (XX > AC_X0) & (XX < AC_X1 - 3)
cv.replace(BEDSPREAD, WALL_SHADE, GRILLE)      # the old row's warm dots, repeated ten times, buzzed: the slats stay slate
cv.replace(DESK_SHADE, WALL_SHADE, GRILLE)
cv.fill(AC & (YY == AC_TOP + 1), WALL)                          # the lip, turned down to the room's light
cv.fill(AC & (YY == AC_TOP), BLACK)
for x, y in ((AC_X0, AC_TOP), (AC_X1, AC_TOP), (AC_X0, AC_TOP + 1), (AC_X1, AC_TOP + 1)):
    cv.idx[y, x] = cv.idx[y, x - 3] if x == AC_X0 else cv.idx[y, x + 3]   # corners rounded into the wall
cv.dot(AC_X0 + 1, AC_TOP + 1, BLACK); cv.dot(AC_X1 - 1, AC_TOP + 1, BLACK)
# its shadow up the wall: the CRT's light comes from below right
SHADOW = BACK_WALL & (YY >= AC_TOP - 3) & (YY < AC_TOP) & (XX >= AC_X0 + 2) & (XX <= AC_X1 - 1)
cv.tile(SHADOW & (YY >= AC_TOP - 1), '1/2', WALL_SHADE, DARK)
cv.tile(SHADOW & (YY < AC_TOP - 1), '1/4', WALL_SHADE, DARK)
cv.replace(WALL, WALL_SHADE, SHADOW & (YY >= AC_TOP - 1))

# the ceiling: WALL_SHADE darkening toward us, a little of the city's glow on it over the window
t = np.clip((J - YY) / 26.0, 0, 1)
cv.grad(CEIL, WALL_SHADE, DARK, t * 0.85, steps=P.STEPS_FINE)
GLOWED = CEIL & (np.hypot((XX - 238) / 70.0, (YY - J) / 9.0) < 1)
cv.tile(GLOWED & (np.hypot((XX - 238) / 46.0, (YY - J) / 6.0) < 1), '1/4', WALL_SHADE, WALL)
# the moulding where the walls meet it: a dark seam on the ceiling side, the wood strip under it
SEAM = cv.m_edge(CEIL, 'bottom', inside=True) & (YY >= 0)
cv.fill(SEAM, BLACK)
MOULD = cv.m_edge(CEIL, 'bottom', inside=False) & STRIP & ~AC
cv.fill(MOULD, WOOD)
# the corner seams run up to it
cv.fill(BELOW & (XX == CL) & ~AC, BLACK)
cv.fill(BELOW & (XX == CR), BLACK)
