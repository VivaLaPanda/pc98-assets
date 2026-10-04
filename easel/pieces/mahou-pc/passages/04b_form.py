# 04b form shading on the machine, before any detail: 2-3 values per plane with banded tiles between ramp neighbours
# (never a flat 16x16 patch). Light from the window side (left) and above; the screen's own light comes later.
with cv.only_over(WALL, WALL_SHADE, PAPER):
    # CRT side: lit at its front corner, falling to shade toward the back and the bottom
    cv.grad(cv.m_poly(side), WALL, WALL_SHADE, cv.lin((b['l'], b['t'] + 6), (TOP_BL[0] + 2, SIDE_BB[1])), offset=-0.15)
    # bezel: the top band catches the lamp-side light, the chin turns down into shade
    cv.grad(cv.m_poly(bezel), PAPER, WALL, cv.lin((0, b['t'] + 1), (0, b['t'] + 9)))
    cv.grad(cv.m_poly(bezel) & cv.m_rect(0, RC['b'] + 1, 499, b['b']), WALL, WALL_SHADE,
            cv.lin((0, RC['b'] + 2), (0, b['b'] + 1)))
    # case: top light to the front edge, side half in shade, front darkening to its foot
    cv.grad(cv.m_poly(case_side), WALL, WALL_SHADE, cv.lin((c['l'], 0), (CASE_TL[0], 0)))
    cv.grad(cv.m_poly(case_front), WALL, WALL_SHADE, cv.lin((0, c['t'] + 1), (0, c['t'] + 6)))
    cv.grad(cv.m_poly(case_front) & cv.m_rect(0, c['b'] - 3, 499, c['b']), WALL_SHADE, DARK,
            cv.lin((0, c['b'] - 4), (0, c['b'])))
