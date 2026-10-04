# 03 line art, desk objects, back to front: mug, keyboard, newspaper, then the chair back cutting in front.
# Keyboard: a slab in perspective (top plane + front lip), key rows drawn later as a grid.
kb_top = [(62, 77), (126, 77), (131, 88), (57, 88)]
kb_lip = [(57, 88), (131, 88), (131, 91), (57, 91)]
clear(cv.m_poly(kb_top) | cv.m_poly(kb_lip))
cv.polyline(kb_top, L, closed=True)
cv.polyline([(57, 88), (57, 91), (131, 91), (131, 88)], L)

# mug right of the keyboard: a cylinder. Sides and the near half of the base first, then the full rim on top.
mug_sil = cv.m_ellipse(127, 63, 5, 2) | cv.m_rect(122, 63, 132, 73) | cv.m_ellipse(127, 73, 5, 2)
clear(mug_sil)
cv.line(122, 63, 122, 73, L); cv.line(132, 63, 132, 73, L)
cv.dots([p for p in ellipse_points(127, 73, 5, 2) if p[1] >= 73], L)
cv.ellipse(127, 63, 5, 2, L)
cv.polyline([(132, 65), (135, 65), (136, 66), (136, 69), (135, 70), (132, 70)], L)

# newspaper, folded, lying askew in front of the tower: a top sheet with a fold line, the stack's edge
np_top = [(5, 88), (58, 83), (68, 99), (11, 105)]
clear(cv.m_poly(np_top) | cv.m_poly([(11, 105), (68, 99), (68, 101), (11, 107)]))
cv.polyline(np_top, L, closed=True)
cv.polyline([(11, 105), (11, 107), (68, 101), (68, 99)], L)
cv.line(31, 86, 39, 102, L)                       # the fold

# chair back with a hoodie slung over it, in front of everything at the right edge
chair = [(143, 66), (151, 60), (163, 57), (175, 56), (175, 127), (149, 127), (146, 100), (144, 84)]
clear(cv.m_poly(chair))
cv.polyline(chair[:-1] + [chair[-1]], L, closed=False)
cv.line(chair[-1][0], chair[-1][1], chair[0][0], chair[0][1], L)
# hood fold and sleeve hanging off the back
cv.polyline([(152, 61), (156, 70), (158, 84), (155, 98)], L)
cv.polyline([(163, 58), (166, 72), (170, 92), (171, 112), (168, 127)], L)
