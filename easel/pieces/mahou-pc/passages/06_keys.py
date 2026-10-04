# 06 the keyboard: rows of key tops (light) between gap lines, each row following the slab's slanted ends; the space
# bar in the front row. At this size a keyboard is three rows of broken 1px dashes, as in the period's own rooms.
BLk, BRk, FRk, FLk = KB
kb_x = lambda p, q, y: p[0] + (y - p[1]) * (q[0] - p[0]) / (q[1] - p[1])
rows = range(BLk[1] + 1, FLk[1])
for y in rows:
    x0, x1 = round(kb_x(BLk, FLk, y)) + 2, round(kb_x(BRk, FRk, y)) - 2
    if (y - BLk[1]) % 2 == 0:
        cv.line(x0 - 1, y, x1 + 1, y, WALL_SHADE)                            # the gap between rows, in shade
        continue
    step = 3 if y == BLk[1] + 1 else 2                                      # the function row's keys are wider
    for x in range(x0, x1 + 1):
        if (x - x0) % step != step - 1:
            cv.dot(x, y, PAPER)
y = FLk[1] - 1
if (y - BLk[1]) % 2 == 1:
    xm = round((kb_x(BLk, FLk, y) + kb_x(BRk, FRk, y)) / 2)
    cv.line(xm - 7, y, xm + 5, y, PAPER)                                    # space bar
cv.line(FLk[0] + 1, FLk[1] + 1, FRk[0] - 1, FRk[1] + 1, WALL)              # the lip's top edge
