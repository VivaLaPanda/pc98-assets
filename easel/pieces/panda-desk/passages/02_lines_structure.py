# 02 line art, structure, back to front: unbroken 1px black lines on every silhouette and construction edge.
# Each object clears its own silhouette to the ground before it is inked, so lines behind it don't show through.
L = K
cv.fill(cv.m_all(), PL)                         # ink on a light ground; flats flood each enclosed area later

def clear(mask):
    cv.fill(mask, PL)

# --- back: window rail, sill, mullion, wall/desk line
cv.line(0, GLASS_B, 175, GLASS_B, L)
cv.line(0, RAIL_B, 175, RAIL_B, L)
cv.line(0, SILL_B, 175, SILL_B, L)
MULL = (119, 122)                               # the frame mullion, continuing the scene's above the seam
cv.line(MULL[0], 0, MULL[0], GLASS_B, L); cv.line(MULL[1], 0, MULL[1], GLASS_B, L)
cv.line(0, DESK_BACK, 175, DESK_BACK, L)

# --- desk top and edge band (in front of the wall)
end_back = toward((DESK_R, DESK_FRONT), (DESK_FRONT - DESK_BACK) / (DESK_FRONT - VP[1]))   # meets the wall line
desk_top = cv.m_poly([(0, DESK_BACK), (end_back[0], DESK_BACK), (DESK_R, DESK_FRONT), (0, DESK_FRONT)])
cv.line(0, DESK_FRONT, DESK_R, DESK_FRONT, L)
cv.line(0, DESK_EDGE, DESK_R, DESK_EDGE, L)
cv.line(DESK_R, DESK_FRONT, *end_back, L)
cv.line(DESK_R, DESK_FRONT, DESK_R, DESK_EDGE, L)

# --- tower: front face, side face to the VP, top sliver
t = TW
top_l = toward((t['l'], t['t']), 0.06)
tower_sil = cv.m_poly([(t['l'], t['t']), top_l, TW_SIDE_T, TW_SIDE_B, (t['r'], t['b']), (t['l'], t['b'])])
clear(tower_sil)
cv.rect(t['l'], t['t'], t['r'], t['b'], L, fill=False)
cv.polyline([(t['r'], t['t']), TW_SIDE_T, TW_SIDE_B, (t['r'], t['b'])], L)
cv.polyline([(t['l'], t['t']), top_l, TW_SIDE_T], L)

# --- CRT: bezel, screen opening, body (side and top faces receding, tapering back), stand
b = BZ
back_tr = (BZ_TR_BACK[0], BZ_TR_BACK[1] + 3)        # the tube housing tapers: back corners sit inside the rays
back_br = (BZ_BR_BACK[0], BZ_BR_BACK[1] - 2)
back_tl = (BZ_TL_BACK[0] + 6, BZ_TL_BACK[1] + 1)
stand = [(70, b['b']), (72, 74), (88, 74), (90, b['b'])]
foot = [(62, 74), (98, 74), (100, 77), (60, 77)]
crt_sil = (cv.m_poly([(b['l'], b['t']), back_tl, back_tr, back_br, (b['r'], b['b']), (b['l'], b['b'])])
           | cv.m_poly(stand) | cv.m_poly(foot))
clear(crt_sil)
cv.rect(b['l'], b['t'], b['r'], b['b'], L, fill=False)
cv.rect(SC['l'] - 1, SC['t'] - 1, SC['r'] + 1, SC['b'] + 1, L, fill=False)
cv.polyline([(b['r'], b['t']), back_tr, back_br, (b['r'], b['b'])], L)
cv.polyline([(b['l'], b['t']), back_tl, back_tr], L)
cv.polyline(stand, L)
cv.polyline(foot, L, closed=True)
SIL = dict(tower=tower_sil, crt=crt_sil, desk_top=desk_top)
