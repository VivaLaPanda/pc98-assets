# 09 the letter (email): an envelope standing on the back of the desk, leaned against the wall beside the monitor,
# its flap toward us, sealed with a heart. The room's paper ink with a black edge so it parts from the lit wall
# behind; its right edge takes the CRT's light, its left throws a 1px shadow on the wall.
# Round 4: bigger (rank 8: a greeting-card envelope, 26x18 against the old 19x12), standing in the same place.
LT_X, LT_Y, LT_W, LT_H = 347, 155, 26, 18
LETTER = cv.m_rect(LT_X, LT_Y, LT_X + LT_W - 1, LT_Y + LT_H - 1)
cv.line(LT_X - 1, LT_Y + 1, LT_X - 1, LT_Y + LT_H - 2, DARK)          # its shadow on the wall, left
cv.fill(LETTER, PAPER)
cv.line(LT_X + 1, LT_Y + 1, LT_X + 12, LT_Y + 10, WALL)                # the flap
cv.line(LT_X + LT_W - 2, LT_Y + 1, LT_X + 13, LT_Y + 10, WALL)
cv.fill(cv.m_edge(LETTER), BLACK)
cv.stamp(LT_X + 10, LT_Y + 8, """
.RR.RR.
RHRRRRR
RRRRRRR
.RRRRR.
..RRR..
...R...
""", {'R': RED, 'H': DESK_SHADE})                                        # the heart seal at the flap's point
for _y in range(LT_Y + 2, LT_Y + LT_H - 1):                           # the CRT's side
    if cv.idx[_y, LT_X + LT_W - 2] == PAPER:
        cv.dot(LT_X + LT_W - 2, _y, GLOW)
cv.dots([(LT_X + LT_W - 3, LT_Y + LT_H - 3), (LT_X + LT_W - 4, LT_Y + LT_H - 2)], GLOW)
cv.masks['letter'] = LETTER
print('letter area', int(LETTER.sum()))

# vp-check: an envelope standing against the back wall is frontal: level and plumb
cv.persp.edge('letter', (LT_X + 1, LT_Y), (LT_X + LT_W - 2, LT_Y), 'h')
cv.persp.edge('letter', (LT_X, LT_Y + 1), (LT_X, LT_Y + LT_H - 2), 'v')
cv.persp.edge('letter', (LT_X + LT_W - 1, LT_Y + 1), (LT_X + LT_W - 1, LT_Y + LT_H - 2), 'v')
cv.persp.edge('letter', (LT_X + 1, LT_Y + LT_H - 1), (LT_X + LT_W - 2, LT_Y + LT_H - 1), 'h')
