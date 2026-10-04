# 04 line art, construction detail: bevels, controls, bays, vents, key grid, print columns, cables.
# Everything that breaks a surface is a 1px line or a 1-2px cluster (technique step 3 + 7).
b, s = BZ, SC
# CRT: an inner bevel 2px inside the bezel opening (the recess the glass sits in), controls on the chin
cv.rect(s['l'] - 3, s['t'] - 3, s['r'] + 3, s['b'] + 3, L, fill=False)
cv.line(b['l'] + 4, b['b'] - 4, b['l'] + 14, b['b'] - 4, L)          # brand plate
for x in (95, 99, 103):                                              # three knobs
    cv.rect(x, b['b'] - 6, x + 2, b['b'] - 4, L, fill=False)
cv.rect(108, b['b'] - 6, 111, b['b'] - 4, L, fill=False)             # power button
# vents on the CRT body's side: short receding slots
for k in range(4):
    p0 = toward((b['r'] + 3, b['t'] + 10 + k * 5), 0.0)
    p1 = toward((b['r'] + 3, b['t'] + 10 + k * 5), 0.08)
    cv.line(*p0, *p1, L)

# tower front: two 5.25" bays, a 3.5" floppy slot, a turbo/power panel, a vent grille near the base
t = TW
for y in (t['t'] + 5, t['t'] + 12):
    cv.rect(t['l'] + 3, y, t['r'] - 3, y + 5, L, fill=False)
    cv.line(t['l'] + 5, y + 3, t['r'] - 9, y + 3, L)                   # tray slot
cv.rect(t['l'] + 7, t['t'] + 21, t['r'] - 7, t['t'] + 25, L, fill=False)
cv.line(t['l'] + 9, t['t'] + 23, t['r'] - 9, t['t'] + 23, L)          # floppy slot
cv.rect(t['l'] + 3, t['t'] + 30, t['l'] + 9, t['t'] + 34, L, fill=False)   # power button
for y in range(t['b'] - 22, t['b'] - 4, 2):                           # grille
    cv.line(t['l'] + 4, y, t['r'] - 4, y, L)
# tower side: a seam along the panel
cv.line(*toward((t['r'], t['t'] + 3), 0.01), *toward((t['r'], t['b'] - 3), 0.01), L)

# keyboard: key rows following the slab's perspective, gaps as lines; a wider space bar row at the front
rows = [(78, 80), (80, 82), (82, 84), (84, 86)]
for k, (y0, y1) in enumerate(rows):
    xl = 62 - (y0 - 77) * 5 // 11
    xr = 126 + (y0 - 77) * 5 // 11
    cv.line(xl, y1, xr, y1, L)
    step = 5
    for x in range(xl + 3 + (k % 2) * 2, xr - 2, step):
        cv.dot(x, y0 + 1, L)
cv.line(80, 86, 80, 88, L); cv.line(108, 86, 108, 88, L)             # space bar ends

# newspaper: masthead, a photo box, column rules
cv.line(9, 90, 28, 88, L); cv.line(9, 91, 28, 89, L)                 # masthead
cv.rect(41, 88, 50, 94, L, fill=False)                               # photo
for x0, x1 in ((10, 28), (11, 29), (12, 30)):
    pass
for k in range(4):                                                    # print lines, left page
    y = 94 + k * 2
    cv.line(10 + k // 2, y, 29 + k // 2, y - 2, L)
for k in range(3):                                                    # right page
    y = 97 + k * 2
    cv.line(44, y - 1, 64, y - 3, L)

# cables: from behind the CRT down the wall to the desk, and the keyboard lead
cv.polyline([(118, 66), (121, 70), (124, 76), (127, 80)], L)
cv.polyline([(98, 77), (110, 78), (116, 76), (120, 72)], L)
