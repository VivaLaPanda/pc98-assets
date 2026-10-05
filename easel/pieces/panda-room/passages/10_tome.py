# 10 the tome (LessWrong): one thick, much-read book lying on the bed by the phone, apart from the bookshelf's
# rows: a navy hardcover with a gold title, its cream page block toward us, bristling with sticky tabs, a red
# ribbon trailing onto the bedspread. Built on the mattress plane (Y -113) so its edges run to the VP like the
# bed's own; turned so the long edge stays near the picture's horizontal (askew rectangles read as diamonds).
BED_Y = -113
TM_C, TM_DEG, TM_L, TM_W, TM_H = np.array([-157.0, 170.0]), -8, 24.0, 17.0, 6.0
_th = np.radians(TM_DEG)
TM_U = np.array([np.cos(_th), np.sin(_th)])           # along the book (X, Z), left to right
TM_V = np.array([-np.sin(_th), np.cos(_th)])          # across it, front to back


def tm(u, v, h=0.0):
    X, Z = TM_C + u * TM_U + v * TM_V
    return pf((X, BED_Y + h, Z))


_L2, _W2 = TM_L / 2, TM_W / 2
TM_TOP = cv.m_poly([tm(-_L2, -_W2, TM_H), tm(_L2, -_W2, TM_H), tm(_L2, _W2, TM_H), tm(-_L2, _W2, TM_H)])
TM_FRONT = cv.m_poly([tm(-_L2, -_W2, TM_H), tm(_L2, -_W2, TM_H), tm(_L2, -_W2), tm(-_L2, -_W2)])
TM_RIGHT = cv.m_poly([tm(_L2, -_W2, TM_H), tm(_L2, _W2, TM_H), tm(_L2, _W2), tm(_L2, -_W2)])
TM_BOOK = TM_TOP | TM_FRONT | TM_RIGHT
# its shadow on the bedspread, down and left, away from the phone and the window
_sh = np.roll(np.roll(TM_BOOK, 1, 0), -1, 1) & ~TM_BOOK
cv.replace(BEDSPREAD, WOOD, _sh); cv.replace(DESK, BEDSPREAD, _sh)
# the page block: cream, the page lines, the boards' edges above and below it
_pages = (TM_FRONT | TM_RIGHT) & ~cv.m_edge(TM_FRONT | TM_RIGHT, 'top,bottom')
cv.fill(TM_FRONT | TM_RIGHT, SLATE)
cv.fill(_pages, DESK)
cv.tile(_pages & TM_RIGHT, '1/2', DESK, DESK_SHADE)
for _h in (2.0, 3.6):
    cv.polyline([tm(-_L2 + 0.5, -_W2, _h), tm(_L2, -_W2, _h), tm(_L2, _W2 - 0.5, _h)], DESK_SHADE)
# the cover: navy, worn lighter along its edges, a gold panel with the title
cv.fill(TM_TOP, DARK)
cv.fill(cv.m_edge(TM_TOP, 'top,left'), SLATE)
_panel = cv.m_poly([tm(-_L2 + 6, -_W2 + 3.5, TM_H), tm(_L2 - 3, -_W2 + 3.5, TM_H), tm(_L2 - 3, _W2 - 3.5, TM_H),
                    tm(-_L2 + 6, _W2 - 3.5, TM_H)])
cv.fill(cv.m_edge(_panel, 'all'), BEDSPREAD)
cv.polyline([tm(-_L2 + 8.5, 0.5, TM_H), tm(_L2 - 5.5, 0.5, TM_H)], BEDSPREAD)        # the title
cv.polyline([tm(-_L2 + 1.5, -_W2 + 0.5, TM_H), tm(-_L2 + 1.5, _W2 - 0.5, TM_H)], BLACK)   # the spine's hinge
cv.fill(cv.m_edge(TM_BOOK, 'all'), BLACK)
# sticky tabs out of the pages, the ribbon onto the bedspread
TM_TABS = []
for (_u, _c) in ((-5.0, GLOW), (1.0, RED), (6.5, CURTAIN)):
    _x, _y = tm(_u, -_W2 - 0.6, 3.0)
    TM_TABS += [(round(_x), round(_y)), (round(_x), round(_y) + 1)]
    cv.dots(TM_TABS[-2:], _c)
_x, _y = tm(_L2 + 0.6, 2.0, 3.0)
TM_TABS += [(round(_x), round(_y)), (round(_x) + 1, round(_y))]
cv.dots(TM_TABS[-2:], GLOW)
_x, _y = tm(-2.0, -_W2, 0.5)
cv.line(round(_x), round(_y) + 1, round(_x) - 2, round(_y) + 4, RED)
TM_RIB = cv.m_line(round(_x), round(_y) + 1, round(_x) - 2, round(_y) + 4)
cv.masks['lesswrong'] = TM_BOOK | TM_RIB | cv._mask_pts(TM_TABS)

# vp-check: a book lying askew on the bed runs to its own VPs (on the horizon); its uprights are plumb
cv.persp.edge('tome', tm(-_L2, -_W2, TM_H), tm(_L2, -_W2, TM_H), own_vp(*TM_U))
cv.persp.edge('tome', tm(-_L2, -_W2), tm(_L2, -_W2), own_vp(*TM_U))
cv.persp.edge('tome', tm(_L2, -_W2, TM_H), tm(_L2, _W2, TM_H), own_vp(*TM_V))
