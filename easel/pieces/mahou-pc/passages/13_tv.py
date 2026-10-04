# 13 tv: a small portable CRT on top of the bookshelf where the striped box was. Same footprint (the box's front
# recedes to the VP like the shelf's top; its near side is the 1px column at x 467), so nothing behind needs painting.
# The screen is turned toward the bed and left on, dim: rank 7, the least of the objects, a FLOOR glow, no glare.
TV_FACE = [(442, 14), (466, 6), (466, 31), (442, 36)]          # TL TR BR BL
TV_SIDE = cv.m_rect(467, 7, 467, 31)
TV_BODY = cv.m_poly(TV_FACE) | TV_SIDE

cv.fill(TV_BODY, SLATE)                                          # dark plastic, its face toward the window's light
cv.fill(TV_SIDE, DARK)
cv.fill(cv.m_edge(cv.m_poly(TV_FACE), 'top,left,bottom', inside=True), DARK)
TV_SCREEN_Q = [quad(TV_FACE, 0.08, 0.16), quad(TV_FACE, 0.66, 0.16), quad(TV_FACE, 0.66, 0.82), quad(TV_FACE, 0.08, 0.82)]
TV_BEZEL = cv.m_poly([quad(TV_FACE, 0.05, 0.11), quad(TV_FACE, 0.70, 0.11), quad(TV_FACE, 0.70, 0.87), quad(TV_FACE, 0.05, 0.87)])
cv.fill(TV_BEZEL, BLACK)
TV_GLASS = cv.m_poly(TV_SCREEN_Q) & ~cv.m_edge(TV_BEZEL)
cv.fill(TV_GLASS, FLOOR)
# a dim picture: the tube's centre a half step up, its corners falling off into the bezel
cv.tile(TV_GLASS & ~cv.m_edge(TV_GLASS) & (cv.rad(quad(TV_FACE, 0.37, 0.48), 0, 7, sy=1.3) < 0.6), '1/4', FLOOR, GLOW)
cv.fill(cv.m_edge(TV_GLASS, 'top,left', inside=True), SLATE)
# controls on the near end: two knobs (a glint each, toward the window) over a speaker grille
for t in (0.24, 0.42):
    x, y = quad(TV_FACE, 0.83, t)
    cv.dot(x, y, BLACK); cv.dot(x - 1, y, BLACK); cv.dot(x - 1, y - 1, PAPER)
GRILLE = cv.m_poly([quad(TV_FACE, 0.75, 0.58), quad(TV_FACE, 0.93, 0.58), quad(TV_FACE, 0.93, 0.84), quad(TV_FACE, 0.75, 0.84)])
cv.tile(GRILLE, 'hline', SLATE, DARK)
# a telescoping antenna, up and back from the near top corner, a glint on its tip
ax0, ay0 = quad(TV_FACE, 0.78, 0.0)
cv.line(ax0, ay0 - 1, ax0 - 6, ay0 - 7, DARK)
cv.dot(ax0 - 6, ay0 - 7, PAPER)
TV_ANT = cv.m_line(ax0, ay0 - 1, ax0 - 6, ay0 - 7)

cv.masks['tv'] = TV_BODY | TV_ANT
