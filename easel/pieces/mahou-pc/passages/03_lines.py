# 03 line art, back to front: case, CRT, newspaper, keyboard. Each object clears its silhouette to a ground ink
# nothing in the room uses yet (WHITE), then gets an unbroken 1px outline in the room's line ink (BLACK = #113).
L = BLACK
G = WHITE
def clear(mask):
    cv.fill(mask, G)

c = CASE
case_front = [(c['l'], c['t']), (c['r'], c['t']), (c['r'], c['b']), (c['l'], c['b'])]
case_top = [(c['l'], c['t']), CASE_TL, CASE_TR, (c['r'], c['t'])]
case_side = [(c['l'], c['t']), CASE_TL, CASE_BL, (c['l'], c['b'])]
clear(cv.m_poly(case_front) | cv.m_poly(case_top) | cv.m_poly(case_side))
cv.polyline(case_front, L, closed=True)
cv.polyline([(c['l'], c['t']), CASE_TL, CASE_TR, (c['r'], c['t'])], L)
cv.polyline([CASE_TL, CASE_BL, (c['l'], c['b'])], L)

# CRT: the bezel (corners clipped one pixel: it's moulded plastic), the tube housing behind it receding to the wall
b = BZ
bezel = [(b['l'] + 1, b['t']), (b['r'] - 1, b['t']), (b['r'], b['t'] + 1), (b['r'], b['b'] - 1),
         (b['r'] - 1, b['b']), (b['l'] + 1, b['b']), (b['l'], b['b'] - 1), (b['l'], b['t'] + 1)]
# the housing tapers hard toward the back (a tube): its back edge is shorter and lower than the bezel
TOP_BL, TOP_BR = toward((b['l'] + 2, b['t'] + 2), f_crt), toward((b['r'] - 3, b['t'] + 2), f_crt)
SIDE_BB = toward((b['l'] + 2, b['b'] - 10), f_crt)
side = [(b['l'], b['t'] + 1), TOP_BL, SIDE_BB, (b['l'], b['b'] - 3)]
top = [(b['l'] + 1, b['t']), TOP_BL, TOP_BR, (b['r'] - 1, b['t'])]
clear(cv.m_poly(bezel) | cv.m_poly(side) | cv.m_poly(top))
cv.polyline(bezel, L, closed=True)
cv.polyline(side, L)
cv.polyline([TOP_BL, TOP_BR, (b['r'] - 1, b['t'])], L)
# the opening in the bezel and the glass inside it (glass corners rounded a pixel)
cv.rect(RC['l'], RC['t'], RC['r'], RC['b'], L, fill=False)
SIL = dict(case=cv.m_poly(case_front) | cv.m_poly(case_top) | cv.m_poly(case_side),
           crt=cv.m_poly(bezel) | cv.m_poly(side) | cv.m_poly(top))

# newspaper, folded once, a corner tucked under the keyboard
clear(cv.m_poly(NP))
cv.polyline(NP, L, closed=True)
FOLD = ((362, 138), (381, 153))
cv.line(*FOLD[0], *FOLD[1], L)                                # the fold

# keyboard: a slab in perspective, top plane plus a 2px front lip
kb_lip = [(KB_F[0], KB_F[2]), (KB_F[1], KB_F[2]), (KB_F[1], KB_F[2] + 2), (KB_F[0], KB_F[2] + 2)]
clear(cv.m_poly(KB) | cv.m_poly(kb_lip))
cv.polyline(KB, L, closed=True)
cv.polyline([(KB_F[0], KB_F[2]), (KB_F[0], KB_F[2] + 2), (KB_F[1], KB_F[2] + 2), (KB_F[1], KB_F[2])], L)
SIL.update(kb=cv.m_poly(KB) | cv.m_poly(kb_lip), paper=cv.m_poly(NP))
