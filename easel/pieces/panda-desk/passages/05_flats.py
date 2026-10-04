# 05 flats: each enclosed area gets its base tone. No shading yet.
# Front to back, fenced to the untouched ground: whatever is already painted (nearer objects, the line art) wins,
# so occlusion comes for free. Night: the dark ramp (AB NV DU SL) carries the room; the CRT is the cool light.
def flat(mask, c):
    with cv.only_over(PL):
        cv.fill(mask, c)

b, s, t = BZ, SC, TW
# chair + hoodie: the nearest thing, in shadow against the room
flat(cv.m_poly(chair), NV)
# newspaper: pale paper in the screen's light; the stack's edge a step down
flat(cv.m_poly(np_top), LV)
flat(cv.m_poly([(11, 105), (68, 99), (68, 101), (11, 107)]), SL)
# keyboard: top plane mid, lip in shade; mug body dark, mouth darker
flat(cv.m_poly(kb_top), SL)
flat(cv.m_poly(kb_lip), DU)
flat(cv.m_ellipse(127, 63, 4, 1), AB)
flat(mug_sil, DU)
# CRT: screen face (dark blue screen with text, drawn later), the recess the glass sits in, bezel, body, stand
flat(cv.m_rect(s['l'], s['t'], s['r'], s['b']), DB)
flat(cv.m_rect(s['l'] - 2, s['t'] - 2, s['r'] + 2, s['b'] + 2), NV)
flat(cv.m_rect(b['l'], b['t'], b['r'], b['b']), SL)
flat(cv.m_poly([(b['r'], b['t']), back_tr, back_br, (b['r'], b['b'])]), DU)     # side, away from the window light
flat(cv.m_poly([(b['l'], b['t']), back_tl, back_tr, (b['r'], b['t'])]), LV)      # top, catches the window
flat(cv.m_poly(stand), NV)
flat(cv.m_poly(foot), DU)
# tower: front mid, side dark, top light; the bays get their own tone later
flat(cv.m_rect(t['l'], t['t'], t['r'], t['b']), SL)
flat(cv.m_poly([(t['r'], t['t']), TW_SIDE_T, TW_SIDE_B, (t['r'], t['b'])]), DU)
flat(cv.m_poly([(t['l'], t['t']), top_l, TW_SIDE_T, (t['r'], t['t'])]), LV)
# desk: dark wood top, edge band in shade, the dark under it and past its end
flat(desk_top, W1)
flat(cv.m_rect(0, DESK_FRONT, DESK_R, DESK_EDGE), AB)
flat(cv.m_rect(0, DESK_EDGE, 175, 127), K)
flat(cv.m_rect(DESK_R, DESK_BACK, 175, 127), K)
# wall under the window, sill, rail, mullion, glass (the city goes in the glass next)
flat(cv.m_rect(0, SILL_B, 175, DESK_BACK), NV)
flat(cv.m_rect(0, RAIL_B, 175, SILL_B), DU)
flat(cv.m_rect(0, GLASS_B, 175, RAIL_B), SL)
flat(cv.m_rect(MULL[0], 0, MULL[1], GLASS_B), NV)
flat(cv.m_rect(0, 0, 175, GLASS_B), K)
holes = int((cv.idx == PL).sum())
assert holes == 0, f'{holes} ground pixels left unfilled'
