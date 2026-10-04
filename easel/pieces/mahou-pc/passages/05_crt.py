# 05 the CRT: bevels, the glass and what's on it, controls. The glass is the room's light source, so it is a hard
# flat of the brightest inks; its corners dim like a real tube; the glare is a stepped curve in the top left.
g = GL
# bezel bevel: a light line along the top and left (the window side), shade along the bottom and right
cv.line(b['l'] + 1, b['t'] + 1, b['r'] - 1, b['t'] + 1, PAPER)
cv.line(b['l'] + 1, b['t'] + 1, b['l'] + 1, b['b'] - 1, PAPER)
cv.line(b['l'] + 2, b['b'] - 1, b['r'] - 1, b['b'] - 1, WALL_SHADE)
cv.line(b['r'] - 1, b['t'] + 2, b['r'] - 1, b['b'] - 1, WALL_SHADE)
# the recess: shadow under its top and left lip, its bottom and right chamfers catch the screen
cv.line(RC['l'] + 1, RC['b'] - 1, RC['r'] - 1, RC['b'] - 1, PAPER)
cv.line(RC['r'] - 1, RC['t'] + 2, RC['r'] - 1, RC['b'] - 1, PAPER)
cv.line(RC['l'] + 1, RC['t'] + 1, RC['r'] - 1, RC['t'] + 1, BLACK)
cv.line(RC['l'] + 1, RC['t'] + 1, RC['l'] + 1, RC['b'] - 2, BLACK)
# the glass: phosphor dims toward the edge (a ring of GLOW, 1/2 tile inside it), corners rounded off
glass = cv.m_rect(g['l'], g['t'], g['r'], g['b'])
ring = cv.m_edge(glass, 'all', inside=True)
cv.fill(ring, GLOW)
cv.fill(cv.m_edge(glass & ~ring, 'all', inside=True), T('1/4', None, GLOW))
for x, y in ((g['l'], g['t']), (g['r'], g['t']), (g['l'], g['b']), (g['r'], g['b'])):
    cv.dot(x, y, DARK)
# on screen: a window with a title bar and a few lines of text (abstract clusters: too small to letter)
cv.rect(g['l'] + 2, g['t'] + 2, g['r'] - 2, g['t'] + 3, FLOOR)                 # title bar, the room's blue
cv.dots([(g['l'] + 4 + k * 2, g['t'] + 2) for k in range(4)], WHITE)           # its title
cv.rect(g['r'] - 4, g['t'] + 2, g['r'] - 3, g['t'] + 3, SCREEN)                # close box
for k, (x0, x1) in enumerate([(4, 18), (4, 21), (4, 14), (4, 19), (4, 11)]):
    y = g['t'] + 6 + k * 2
    cv.line(g['l'] + x0, y, g['l'] + x1, y, CURTAIN)                          # text rows
cv.rect(g['r'] - 6, g['t'] + 6, g['r'] - 3, g['t'] + 9, FLOOR, fill=False)     # a picture
cv.dot(g['r'] - 5, g['t'] + 8, CURTAIN)
# glare: two stepped arcs of white in the top-left corner
cv.dots([(g['l'] + 2, g['t'] + 6), (g['l'] + 2, g['t'] + 5), (g['l'] + 3, g['t'] + 4), (g['l'] + 4, g['t'] + 3)], WHITE)
cv.dots([(g['l'] + 2, g['t'] + 9), (g['l'] + 3, g['t'] + 8)], WHITE)
cv.dot(g['r'] - 2, g['b'] - 2, WHITE)
# chin: maker's badge left, three knobs, the power switch and its LED right
cv.line(b['l'] + 4, b['b'] - 4, b['l'] + 8, b['b'] - 4, PAPER); cv.dot(b['l'] + 4, b['b'] - 3, DARK)
for x in (b['r'] - 18, b['r'] - 15, b['r'] - 12):
    cv.dot(x, b['b'] - 4, DARK); cv.dot(x, b['b'] - 5, PAPER)
cv.rect(b['r'] - 8, b['b'] - 5, b['r'] - 5, b['b'] - 3, BLACK, fill=False)
cv.dot(b['r'] - 7, b['b'] - 4, WALL_SHADE); cv.dot(b['r'] - 6, b['b'] - 4, WALL_SHADE)
cv.dot(b['r'] - 3, b['b'] - 4, SCREEN)                                        # power LED
# housing: a light edge where the side turns the corner to the bezel, vent slots toward the back, a seam
cv.line(b['l'] - 1, b['t'] + 3, b['l'] - 1, b['b'] - 5, PAPER)
for k in range(4):
    p0 = (TOP_BL[0] + 2, TOP_BL[1] + 4 + k * 2)
    cv.line(p0[0], p0[1] + 1, p0[0] + 4, p0[1] + 2, WALL_SHADE)
cv.polyline([toward((b['l'], b['t'] + 4), 0.035), toward((b['l'], b['b'] - 5), 0.035)], WALL_SHADE)
