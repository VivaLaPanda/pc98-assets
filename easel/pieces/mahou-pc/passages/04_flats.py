# 04 flats, by plane. This room is lit from the window on the left: left-facing planes are light, fronts a step
# darker (see the desk's own pedestal). Machines: beige plastic = paper (#77b) / wall (#558) / wall-shade (#446).
def flat(mask, c):
    with cv.only_over(G):
        cv.fill(mask, c)

# keyboard and newspaper first (nearest), then the CRT, then the case
flat(cv.m_poly(KB), WALL)
flat(SIL['kb'], WALL_SHADE)
flat(cv.m_poly([NP[0], FOLD[0], FOLD[1], NP[3]]), WALL)                    # the left half of the fold, turned from the light
flat(SIL['paper'], PAPER)
flat(cv.m_rect(GL['l'], GL['t'], GL['r'], GL['b']), SCREEN)
flat(cv.m_rect(RC['l'], RC['t'], RC['r'], RC['b']), DARK)
flat(cv.m_poly(top), PAPER)
flat(cv.m_poly(side), WALL)
flat(cv.m_poly(bezel), WALL)
flat(cv.m_poly(case_top), PAPER)
flat(cv.m_poly(case_side), WALL)
flat(cv.m_poly(case_front), WALL_SHADE)
left = int((cv.idx == G).sum())
assert left == 0, f'{left} ground pixels unfilled'
