# 06 the case front (PC-98: two 5.25" drives side by side, LEDs and badge on the left), the keyboard's keys. Every surface broken by 1px lines and 1-2px clusters.
c = CASE
cv.line(c['l'] + 1, c['t'] + 1, c['r'] - 1, c['t'] + 1, WALL)                  # top bevel of the front
for x0 in (c['l'] + 11, c['l'] + 26):                                        # the two drive bays
    cv.rect(x0, c['t'] + 2, x0 + 13, c['b'] - 2, DARK, fill=False)
    cv.line(x0 + 2, c['t'] + 5, x0 + 10, c['t'] + 5, BLACK)                  # disk slot
    cv.line(x0 + 2, c['t'] + 6, x0 + 10, c['t'] + 6, WALL)                   # its lower lip catches light
    cv.rect(x0 + 10, c['t'] + 7, x0 + 11, c['t'] + 8, PAPER)                 # lever
    cv.dot(x0 + 2, c['t'] + 8, RED)                                          # access LED (dark)
cv.dot(c['l'] + 3, c['t'] + 3, SCREEN)                                       # power LED, lit
cv.dot(c['l'] + 5, c['t'] + 3, RED)
cv.line(c['l'] + 2, c['b'] - 3, c['l'] + 7, c['b'] - 3, PAPER)               # the badge
cv.line(c['l'] + 2, c['b'] - 1, c['r'] - 1, c['b'] - 1, DARK)                # shadow along the foot
cv.line(*toward((c['l'], c['t'] + 5), 0.03), *toward((c['l'], c['t'] + 5), 0.08), DARK)   # side seam

# keyboard: rows of key tops (light) between gap lines, each row following the slab's slanted ends; space bar in front
kb_l = lambda y: KB_BL[0] + (y - 146) * (KB_F[0] - KB_BL[0]) / 7
kb_r = lambda y: KB_BR[0] + (y - 146) * (KB_F[1] - KB_BR[0]) / 7
for y in (148, 150):                                                          # the gaps between rows, in shade
    cv.line(round(kb_l(y)) + 1, y, round(kb_r(y)) - 1, y, WALL_SHADE)
for y in (147, 149, 151):
    x0, x1 = round(kb_l(y)) + 2, round(kb_r(y)) - 2
    for x in range(x0, x1):
        if (x - x0) % 3 != 2:
            cv.dot(x, y, PAPER)
y = 152
cv.line(round(kb_l(y)) + 12, y, round(kb_l(y)) + 26, y, PAPER)                   # space bar
cv.line(KB_F[0] + 1, KB_F[2] + 1, KB_F[1] - 1, KB_F[2] + 1, WALL)               # lip catches a little light
