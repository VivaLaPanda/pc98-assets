# 14 the duck (Stack Overflow): a rubber duck on the newspaper at the keyboard's left end, facing the screen it
# helps debug. The bed's yellow (the room's only yellow, mustard at night), outlined; the CRT's glass is above and
# to its right, so its crown, face and breast take a cyan rim and a catchlight, and the back and belly fall into
# the bed's dark brown. A 1px contact shadow on the paper, on the side away from the screen.
DK_X, DK_Y = 368, 177                                       # top-left; its belly sits on the paper at y 186
DK_ART = '''
......KKKK...
.....KLLLLK..
.....KYYEHLK.
.....KYYYYRRK
K....KYYYLKK.
KK..KLLYYYLK.
KLYKYYYYYYYLK
KYYYYYYYYYYLK
.KSSYYYYYYLK.
..KKKKKKKKK..
'''
_rows = DK_ART.strip('\n').splitlines()
DUCK = cv._mask_pts([(DK_X + x, DK_Y + y) for y, r in enumerate(_rows) for x, ch in enumerate(r) if ch not in '. '])
# its shadow first: under the belly and out to the left on the paper (the screen is up and to the right)
_sh = (np.roll(DUCK, 1, 0) | np.roll(np.roll(DUCK, 1, 0), -1, 1)) & ~DUCK
_sh &= (_ys - 0.5 >= DK_Y + 8)
for _a, _c in {PAPER: CURTAIN, CURTAIN: WALL, GLOW: CURTAIN, DESK: DESK_SHADE, WALL: WALL_SHADE}.items():
    cv.replace(_a, _c, _sh)
cv.stamp(DK_X, DK_Y, DK_ART, {'K': BLACK, 'Y': BEDSPREAD, 'L': GLOW, 'S': WOOD, 'E': BLACK, 'H': SCREEN, 'R': RED})
cv.masks['stackoverflow'] = DUCK

# vp-check: it sits level on the paper (its belly's flat run)
cv.persp.edge('duck', (DK_X + 2, DK_Y + 9.5), (DK_X + 10, DK_Y + 9.5), 'h')
