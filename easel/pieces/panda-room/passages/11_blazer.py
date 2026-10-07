# 11 the blazer (LinkedIn): the work jacket, home and hung on its hanger from the desk chair's back, its front to
# us (from behind, slung over the chair, it read as a dark locker): sloped shoulders, the lapels' V with the tie
# hanging in it, two buttons, the hem's cutaway, pocket flaps and a pocket square. Navy (slate, dark); lit from both
# sides like the chair under it: the moon rims the window side, the PC's cyan the desk side.
BZ_X, BZ_Y = 303, 158                                       # top-left; the chair back's pad is x 309-322, y 164-203


def bz(pts):
    return cv.m_poly([(BZ_X + x, BZ_Y + y) for x, y in pts])


def bzl(x0, y0, x1, y1, c):
    cv.line(BZ_X + x0, BZ_Y + y0, BZ_X + x1, BZ_Y + y1, c)


# the hanger's hook over the chair back's top
cv.dots([(BZ_X + x, BZ_Y + y) for x, y in ((13, 5), (13, 4), (13, 3), (14, 2), (15, 2), (16, 3))], PAPER)
_body = bz([(9, 6), (17, 6), (24, 10), (25, 13), (23, 40), (18, 42), (13.5, 37), (8, 42), (3, 40), (1, 13), (2, 10)])
_sl_l = bz([(1, 11), (5, 12), (5, 44), (1, 45), (0, 41)])
_sl_r = bz([(21, 12), (25, 11), (26, 41), (25, 45), (21, 44)])
BLAZER = _body | _sl_l | _sl_r
_vee = bz([(9, 6), (17, 6), (13.5, 22)])                    # the open front above the buttons: lining and tie
cv.fill(BLAZER, SLATE)
cv.tile(BLAZER & (_xs - 0.5 > BZ_X + 15), '1/2', SLATE, DARK)        # turning away from the window
cv.fill(_sl_r, DARK)
cv.fill(_vee, BLACK)
# lapels along the V, the notch where collar meets lapel
for _s in (-1, 1):
    _cx = 13.5 + _s * 4.5
    bzl(round(_cx), 6, round(13.5 + _s * 1), 21, DARK)
    bzl(round(_cx + _s * 1), 7, round(13.5 + _s * 2), 21, CURTAIN if _s < 0 else GLOW)
    cv.dot(BZ_X + round(_cx + _s * 2), BZ_Y + 10, BLACK)
# the tie, from the hanger's neck down the V
_tie = bz([(12.5, 6), (14.5, 6), (15, 19), (13.5, 23), (12, 19)])
cv.fill(_tie, RED)
cv.line(BZ_X + 13, BZ_Y + 7, BZ_X + 13, BZ_Y + 19, DESK_SHADE)
cv.dots([(BZ_X + 13, BZ_Y + 6), (BZ_X + 14, BZ_Y + 6)], BLACK)      # the knot's shadow under the hook
# buttons, the hem's cutaway, pockets, the pocket square
cv.dots([(BZ_X + 13, BZ_Y + 26), (BZ_X + 13, BZ_Y + 31)], PAPER)
bzl(13, 34, 9, 41, BLACK); bzl(14, 34, 18, 41, BLACK)
bzl(6, 33, 10, 33, DARK); bzl(17, 33, 21, 33, BLACK)
bzl(17, 16, 20, 16, BLACK)
cv.dots([(BZ_X + 18, BZ_Y + 15), (BZ_X + 19, BZ_Y + 15), (BZ_X + 19, BZ_Y + 14)], PAPER)
# sleeves part from the body; cuffs with a button
bzl(5, 14, 5, 42, BLACK); bzl(21, 14, 21, 42, BLACK)
bzl(1, 41, 4, 41, DARK); bzl(22, 41, 25, 41, BLACK)
cv.fill(cv.m_edge(BLAZER, 'all'), BLACK)
cv.fill(cv.m_edge(_sl_l, 'left') & ~cv.m_edge(_sl_l, 'top,bottom'), CURTAIN)     # the moon's rim
cv.fill(cv.m_edge(_body, 'top') & (_xs - 0.5 < BZ_X + 10), CURTAIN)
cv.fill(cv.m_edge(_sl_r, 'right') & ~cv.m_edge(_sl_r, 'top,bottom'), GLOW)       # the PC's
cv.masks['linkedin'] = BLAZER | cv.m_rect(BZ_X + 13, BZ_Y + 2, BZ_X + 16, BZ_Y + 5) & cv.m_where(PAPER)

# vp-check: a jacket on a hanger hangs plumb: its sleeves' seams, its hook, and the centre line of its body
cv.persp.edge('blazer', (BZ_X + 5, BZ_Y + 14), (BZ_X + 5, BZ_Y + 42), 'v')
cv.persp.edge('blazer', (BZ_X + 21, BZ_Y + 14), (BZ_X + 21, BZ_Y + 42), 'v')
cv.persp.axis('blazer', BLAZER, rows=(BZ_Y + 8, BZ_Y + 40))
