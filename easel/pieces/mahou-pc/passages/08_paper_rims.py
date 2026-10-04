# 08 after the light: the newspaper, then rims and contact shadows.
# The newspaper (Substack) is the brightest thing on the desk after the glass: its traced light as hard bands, the
# half turned away from the screen (the left of the fold, tented up) a step lower, and its print laid after the light
# so it stays dark and crisp. Print is placed in the paper's own frame (x across, z down the page, cm), so every row
# follows the sheet's perspective and its skew on the desk.
PAPER_RAMP = {PAPER: GLOW, GLOW: SCREEN, SCREEN: SCREEN}
turned = SIL['paper'] & cv.m_poly([NP[0], FOLD[0], FOLD[1], NP[3]])
cv.relight(SIL['paper'] & lightable, np.where(turned, np.clip(LV_PAPER - 0.5, 1.0, 1.25), np.maximum(LV_PAPER, 1.25)),
           PAPER_RAMP, tile_on={PAPER, GLOW})
# a light sheet's edge is drawn in a dark of its own colour, not the line black (as the room draws its calendar's
# pages): the outline where it lies on the desk goes to wall shade
ring = cv.m_edge(SIL['paper'], 'all', inside=False) & cv.m_where(BLACK) & ~SIL['crt'] & ~SIL['kb']
cv.fill(ring, WALL_SHADE)
cv.fill(cv.m_line(*FOLD[0], *FOLD[1]) & SIL['paper'] & cv.m_where(BLACK), PAPER)

def pp(x, z):
    """A point of the newspaper's page on the canvas."""
    return on_desk(NP_C, NP_DEG, x, z)

INKIER = {SCREEN: GLOW, GLOW: PAPER, PAPER: WALL}                    # small print: one step under its paper

def prow(x0, x1, z, c=None, gaps=()):
    """A row of print across the page at z, broken at the column gaps (each a pair of x). c=None prints small text:
    each pixel one step darker than the paper under it, so from this far the columns read as grey, not black."""
    cuts = [x0] + [g for gap in sorted(gaps) for g in gap] + [x1]
    m = np.zeros_like(SIL['paper'])
    for a, b in zip(cuts[::2], cuts[1::2]):
        m |= cv.m_line(*pp(a, z), *pp(b, z))
    m &= SIL['paper'] & cv.m_where(PAPER, GLOW, SCREEN)
    if c is None:
        for k, v in INKIER.items():
            cv.idx[m & (cv.idx == k)] = v
    else:
        cv.fill(m, c)

with cv.only_over(PAPER, GLOW, SCREEN):
    cv.poly([pp(-8.5, 15.5), pp(-5, 15.5), pp(-5, 12), pp(-8.5, 12)], BEDSPREAD)    # the orange mark...
prow(-3.5, 7.5, 13.8, DARK)                                                        # masthead
prow(-8, 7, 9.0, WALL_SHADE, gaps=[(-0.6, 0.6)])                                   # headline, across the fold
for z in (3.5, -5.5):                                                              # columns of small print
    prow(-8, -1.2, z, gaps=[(-4.8, -4.2)])
    prow(1.2, 8, z)
with cv.only_over(GLOW, SCREEN):
    cv.poly([pp(3, 1.5), pp(7.5, 1.5), pp(7.5, -6), pp(3, -6)], PAPER)             # a photo on the right half
    cv.dot(*pp(5, -2), WALL)

# rims: 1px of the light ink along edges turned toward the glass
with cv.only_over(WALL, WALL_SHADE, PAPER, GLOW):
    cv.line(KB[3][0] + 1, KB[3][1] + 1, KB[2][0] - 1, KB[2][1] + 1, GLOW)        # the keyboard lip's top edge
with cv.only_over(DESK_SHADE, DESK, PAPER, WOOD):
    cv.line(379, DESK_FRONT_Y, KB[3][0] - 1, DESK_FRONT_Y, PAPER)                 # the desk's front edge, left of the keys
# contact shadows: where things meet the desk the light cannot reach
with cv.only_over(DESK_SHADE, DESK, PAPER, GLOW):
    cv.line(KB[3][0], KB[3][1] + 4, KB[2][0], KB[2][1] + 4, WOOD)                 # under the keyboard's front lip
foot_line = cv.m_edge(SIL['foot'], 'bottom', inside=False) & ~objects
cv.fill(foot_line & cv.m_where(DESK_SHADE, DESK, PAPER, GLOW), WOOD)               # under the swivel foot
