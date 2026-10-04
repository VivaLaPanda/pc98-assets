# 08 after the light: the newspaper, then rim lights on every edge that faces the glass.
# the newspaper is the brightest thing on the desk after the glass: hard flats, lettered after the lighting so its
# print stays dark and crisp. The half facing the screen is GLOW, the turned half PAPER with a 1/4 GLOW toward it.
lit_half = SIL['paper'] & ~cv.m_poly([NP[0], FOLD[0], FOLD[1], NP[3]]) & lightable
turned = SIL['paper'] & cv.m_poly([NP[0], FOLD[0], FOLD[1], NP[3]]) & lightable
cv.fill(lit_half, GLOW)
cv.fill(turned, PAPER)
cv.fill(turned & cv.m_poly([(357, 138), FOLD[0], FOLD[1], (376, 153)]), T('1/4', None, GLOW))
# a broadsheet folded in half. Lit half (right): masthead with the orange Substack mark, a headline, a
# photo, columns. Turned half (left): columns only. Rows follow the paper's slant (its top edge drops 1 per 12).
def prow(x0, x1, y, c, step=None):
    """A row of print from x0 to x1 that follows the sheet's slant (top edge rises to the right)."""
    for x in range(x0, x1 + 1):
        if step and (x - x0) % step == step - 1:
            continue
        cv.dot(x, y - (x - 350) // 12, c)
cv.rect(365, 140, 367, 141, BEDSPREAD)                                      # the mark: an orange block...
cv.dot(366, 140, PAPER)                                                     # ...with its pale bar
prow(369, 377, 140, BLACK)                                                  # masthead name
prow(366, 380, 142, DARK, step=7)                                           # headline
cv.rect(375, 144, 380, 147, SLATE)                                          # photo
cv.dots([(376, 145), (378, 146)], WALL)
for y in (145, 147, 149):
    prow(366 + (y - 145), 372 + (y - 145) // 2, y, WALL_SHADE)
prow(369, 383, 151, WALL_SHADE, step=8)
for y in (142, 144, 146, 148, 150):
    x0 = 352 + (y - 139) * 15 // 14
    prow(x0, x0 + 6, y, WALL_SHADE, step=4)

# rims: 1px of the light colour along edges turned toward the screen
cv.line(KB_F[0] + 1, KB_F[2] + 1, KB_F[1] - 1, KB_F[2] + 1, GLOW)                # keyboard lip's top edge
cv.line(CASE['l'] + 1, CASE['t'] - 1, CASE['r'] - 1, CASE['t'] - 1, GLOW)       # case top's front edge
cv.line(BZ['l'] + 2, BZ['b'] + 1, BZ['r'] - 2, BZ['b'] + 1, PAPER)              # where the bezel's foot meets the case
with cv.only_over(DESK_SHADE, DESK, PAPER, GLOW):
    cv.line(379, DESK_FRONT_Y - 1, 431, DESK_FRONT_Y - 1, GLOW)                 # the desk's front edge, near the keys
    cv.line(KB_F[0], KB_F[2] + 3, KB_F[1], KB_F[2] + 3, DESK_SHADE)             # the keyboard's shadow in front of it
