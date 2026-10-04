# 03 line art, back to front: newspaper, monitor (foot, side, top, bezel), keyboard. Each object clears its silhouette
# to a ground ink (WHITE: the room never uses it here) and gets an unbroken 1px outline in the room's line ink.
L = BLACK
G = WHITE
def clear(mask):
    cv.fill(mask, G)

def clipped(q):
    """A quad (TL TR BR BL) with its corners cut a pixel: moulded plastic, not a box."""
    (a, b), (c, d), (e, f), (g, h) = q
    return [(a + 1, b), (c - 1, d), (c, d + 1), (e, f - 1), (e - 1, f), (g + 1, h), (g, h - 1), (a, b + 1)]

# newspaper, flat on the desk; the monitor and keyboard come down over its far and near ends
clear(cv.m_poly(NP))
cv.polyline(NP, L, closed=True)
cv.line(*FOLD[0], *FOLD[1], L)                                    # the fold

# the swivel foot: a short neck under the tube flaring to a round plate on the desk
ring = lambda r, v: [mon(FOOT_C[0] + r * FOOT_R[0] * np.cos(a), v, FOOT_C[1] + r * FOOT_R[1] * np.sin(a))
                     for a in np.linspace(0, 2 * np.pi, 32, endpoint=False)]
foot_top, foot_bot = ring(0.6, 0), ring(1, -FOOT_H)
foot = cv.m_poly(foot_top) | cv.m_poly(foot_bot) | cv.m_poly(
    [min(foot_top), max(foot_top), max(foot_bot), min(foot_bot)])
clear(foot)
cv.fill(cv.m_edge(foot, 'all', inside=True), L)

# the tube housing's left side and top, then the bezel over them
side, top, bezel = cv.m_poly(SIDE), cv.m_poly(TOP), cv.m_poly(clipped(FACE))
clear(side | top | bezel)
crt = side | top | bezel
cv.fill(cv.m_edge(crt, 'all', inside=True), L)
cv.polyline(clipped(FACE), L, closed=True)                        # the bezel's own edge, inside the silhouette
# the opening in the bezel the glass sits in
cv.polyline(RECESS, L, closed=True)

# keyboard: a slab in perspective, top plane plus its front lip
kb_top, kb_lip = cv.m_poly(KB), cv.m_poly(KB_LIP)
clear(kb_top | kb_lip)
cv.fill(cv.m_edge(kb_top | kb_lip, 'all', inside=True), L)
cv.line(*KB[3], *KB[2], L)                                        # where the top turns down into the lip

SIL = dict(crt=crt | foot, bezel=bezel, side=side, top=top, foot=foot, kb=kb_top | kb_lip, kb_top=kb_top,
           kb_lip=kb_lip, paper=cv.m_poly(NP) & ~(crt | foot | kb_top | kb_lip))
