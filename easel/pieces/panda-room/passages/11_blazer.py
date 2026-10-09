# 11 the blazer (LinkedIn): the work jacket, home and thrown over the bed's headboard (the user, 2026-10-09: "the
# blazer should be bigger. Maybe draped over/hanging off the headboard of the bed?"; it used to hang on the desk
# chair, small). Its collar over the rail at the headboard's right end, its two fronts hanging open toward us over
# the pillow (lapels, the lining between them, a pocket square, two buttons, pocket flaps), the right sleeve hanging
# off the headboard's end and down its side, the left one folded back along the rail. Navy (slate, dark); the moon
# from the window on its right rims that side. This is the drawing that evokes it: 20 brings back an image model's
# polish of it.

PRE_BZ = cv.idx.copy()                                     # the headboard and pillow without it (for 20)


def bzp(pts):
    return cv.m_poly(pts)


_collar = bzp([(117, 163), (145, 163), (148, 168), (114, 168)])
_left = bzp([(111, 166), (130, 166), (131, 172), (130, 202), (121, 205), (111, 202), (109, 172)])
_right = bzp([(132, 166), (150, 166), (152, 172), (152, 202), (144, 205), (134, 202), (132, 172)])
_gap = bzp([(129, 167), (134, 167), (133, 200), (130, 200)])
_sleeve_r = bzp([(149, 167), (156, 168), (163, 176), (165, 209), (158, 212), (155, 205), (153, 180)])
_sleeve_l = bzp([(97, 165), (112, 165), (112, 171), (103, 172), (99, 180), (94, 178), (95, 170)])
BLAZER = _collar | _left | _right | _gap | _sleeve_r | _sleeve_l

cv.fill(BLAZER, SLATE)
cv.tile(_left | _sleeve_l, '1/2', SLATE, DARK)                       # the side away from the window
cv.fill(_gap, RED)                                                    # the lining
cv.fill(_collar, DARK)
# lapels: from the collar down to the top button, each a lit fold on its window side
for _x0, _x1, _lit in ((123, 130, CURTAIN), (132, 139, GLOW)):
    _lap = bzp([(_x0, 167), (_x1, 167), (131 if _x0 < 131 else 132, 186)])
    cv.fill(_lap, SLATE)
    cv.fill(cv.m_edge(_lap, 'right'), _lit)
    cv.fill(cv.m_edge(_lap, 'left'), BLACK)
cv.dots([(135, 189), (135, 195)], PAPER)                              # buttons
cv.line(113, 192, 121, 192, BLACK); cv.line(139, 192, 148, 192, BLACK)    # pocket flaps
cv.dots([(144, 175), (145, 175), (145, 174), (146, 174)], PAPER)      # the pocket square
cv.line(153, 180, 155, 205, BLACK)                                    # the sleeve parts from the body
cv.line(158, 208, 164, 207, CURTAIN)                                  # its cuff
cv.fill(cv.m_edge(BLAZER, 'all'), BLACK)
cv.fill(cv.m_edge(_sleeve_r | _right, 'right') & ~cv.m_edge(BLAZER, 'top,bottom'), CURTAIN)   # the moon's rim
cv.fill(cv.m_edge(_collar, 'top') & (XX > 120), WALL)
cv.masks['linkedin'] = BLAZER
