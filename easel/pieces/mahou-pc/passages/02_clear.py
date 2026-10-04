# 02 clear the desk: the radio deck, the lamp's foot, papers and a mouse stood where the computer goes. Paint the
# desk top back under them in its own ink (the original's right half is one flat desk-shade), and carry the pillar
# down behind where the radio was. The new objects then cover most of it.
diag = lambda y: 345 + (y - DESK_BACK_Y) * 33 / 20          # x of the desk's receding left edge at height y
desk_right = cv.m_poly([(345, 138), (431, 138), (431, 155), (378, 155)]) & ~cv.m_poly(
    [(330, 130), (366, 130), (380, 156), (330, 156)])        # leave the lit left part of the desk as painted
cv.fill(desk_right, DESK_SHADE)
# the pillar between the radio and the bookshelf, continued down to the desk (cloned from above, rows 100-109)
pill = cv.copy(421, 100, 430, 109)
for y in range(110, 137, 10):
    cv.paste(pill, 421, y)
cv.line(421, 137, 430, 137, BLACK)                           # where the pillar meets the desk
