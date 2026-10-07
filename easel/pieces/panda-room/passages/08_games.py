# 08 the games (Steam): a grey 16-bit console on the floor in front of the TV, a cartridge standing in its slot, and
# its pad lying on the floor out toward the room on its cord. Lavender-grey plastic, the room's paper and curtain
# inks; the pad's four buttons in the scene's accents. The top faces the TV and takes its light, the side toward the
# window a step lighter than the front (the picture's rule again).
GM_X0, GM_X1, GM_Z0, GM_Z1, GM_H = 101., 120., 130., 145., 6.
_t, _b = FLOOR_Y + GM_H, FLOOR_Y


def gm(x, y, z):
    return pf((x, y, z))


GM_TOP = cv.m_poly([gm(GM_X0, _t, GM_Z0), gm(GM_X1, _t, GM_Z0), gm(GM_X1, _t, GM_Z1), gm(GM_X0, _t, GM_Z1)])
GM_FRONT = cv.m_poly([gm(GM_X0, _t, GM_Z0), gm(GM_X1, _t, GM_Z0), gm(GM_X1, _b, GM_Z0), gm(GM_X0, _b, GM_Z0)])
GM_LEFT = cv.m_poly([gm(GM_X0, _t, GM_Z0), gm(GM_X0, _t, GM_Z1), gm(GM_X0, _b, GM_Z1), gm(GM_X0, _b, GM_Z0)])
GM_BOX = GM_TOP | GM_FRONT | GM_LEFT
cv.fill(GM_TOP, CURTAIN)                      # below the TV's picture in value: lit, but not the corner's brightest
cv.fill(GM_LEFT, WALL)
cv.tile(GM_LEFT, '1/2', WALL, CURTAIN)
cv.fill(GM_FRONT, WALL_SHADE)
# the top's darker middle panel, the slot, two switches
_mid = cv.m_poly([gm(GM_X0 + 4, _t, GM_Z0 + 5), gm(GM_X1 - 4, _t, GM_Z0 + 5), gm(GM_X1 - 4, _t, GM_Z1 - 3),
                  gm(GM_X0 + 4, _t, GM_Z1 - 3)])
cv.fill(_mid & ~cv.m_edge(GM_TOP), WALL)
for _x in (GM_X0 + 6, GM_X1 - 7):                                                  # power, reset
    _p = gm(_x, _t, GM_Z0 + 6.5)
    cv.dots([(round(_p[0]), round(_p[1])), (round(_p[0]) + 1, round(_p[1]))], GLOW)
# the cartridge, standing in the slot: a dark box, a label, its top edge catching the TV
_ct0, _ct1, _cz, _ch = GM_X0 + 5, GM_X1 - 5, GM_Z1 - 6, 7.
_cart = cv.m_poly([gm(_ct0, _t, _cz), gm(_ct1, _t, _cz), gm(_ct1, _t + _ch, _cz), gm(_ct0, _t + _ch, _cz)])
cv.fill(_cart, DARK)
_lab = cv.m_poly([gm(_ct0 + 2, _t + 1.5, _cz), gm(_ct1 - 2, _t + 1.5, _cz), gm(_ct1 - 2, _t + _ch - 1, _cz),
                  gm(_ct0 + 2, _t + _ch - 1, _cz)])
cv.fill(_lab, BEDSPREAD)
cv.tile(_lab & (cv.lin(gm(0, _t + _ch, _cz), gm(0, _t, _cz)) > 0.55), '1/2', BEDSPREAD, RED)
cv.fill(cv.m_edge(_cart, 'top'), SLATE)
cv.fill(cv.m_edge(_cart, 'left,right'), BLACK)
# the front: two pad ports and the power lamp
for _x in (GM_X0 + 3, GM_X0 + 7):
    _p = gm(_x, _t - 2.5, GM_Z0)
    cv.rect(round(_p[0]), round(_p[1]), round(_p[0]) + 1, round(_p[1]) + 1, BLACK)
_p = gm(GM_X1 - 3, _t - 2.5, GM_Z0)
cv.dot(round(_p[0]), round(_p[1]), RED)
GM_CONSOLE = GM_BOX | _cart
cv.fill(cv.m_edge(GM_CONSOLE, 'all'), BLACK)
cv.polyline([gm(GM_X0, _t, GM_Z0), gm(GM_X1, _t, GM_Z0)], PAPER)                # the front top edge, lit
cv.polyline([gm(GM_X0, _t, GM_Z0 + 1), gm(GM_X0, _t, GM_Z1)], PAPER)            # and the left one

# seated on the floor: a contact shadow along its bottom edges, a step darker than the floor (2px out on the right,
# away from the moon), so it stands rather than floats
_flo = {FLOOR: DARK, SLATE: DARK, GLOW: FLOOR}
_below, _right = np.roll(GM_BOX, 1, 0) & ~GM_BOX, np.roll(GM_BOX, 1, 1) & ~GM_BOX
_foot = _below | _right | np.roll(_right, 1, 1)
_foot &= ~GM_BOX & (np.arange(cv.h)[:, None] > gm(GM_X1, _t, GM_Z0)[1])          # on the floor, below its top
for _a, _c in _flo.items():
    cv.replace(_a, _c, _foot & ~GM_CONSOLE)

# the pad: a dogbone on the floor, the D-pad, select/start, the four buttons in a diamond
PAD_X, PAD_Y = 340, 333
PAD_ART = '''
..KKKKKKKKKKKKKKKKKK..
.KPPPPPPPPPPPPPPPPPPK.
KPPDPPPPPPPPPPPPPBPPPK
KPDDDPPPCCPCCPPPGPRPPK
KPPDPPPPPPPPPPPPPYPPPK
KCPPPPPKKKKKKKKPPPPPCK
.KCCCCK........KCCCCK.
..KKKK..........KKKK..
'''
cv.stamp(PAD_X, PAD_Y, PAD_ART, {'K': BLACK, 'P': PAPER, 'C': CURTAIN, 'D': DARK, 'B': FLOOR, 'G': GLOW,
                                  'R': RED, 'Y': BEDSPREAD})
_rows = PAD_ART.strip('\n').splitlines()
# its shadow: under the grips and in the gap between them, so it lies on the floor rather than over it
_psh = cv._mask_pts([(PAD_X + x, PAD_Y + 8) for x in list(range(2, 7)) + list(range(16, 21))]
                    + [(PAD_X + x, PAD_Y + 6) for x in range(7, 15)] + [(PAD_X + 22, PAD_Y + y) for y in range(2, 7)])
for _a, _c in _flo.items():
    cv.replace(_a, _c, _psh)
GM_PAD = cv._mask_pts([(PAD_X + x, PAD_Y + y) for y, r in enumerate(_rows) for x, ch in enumerate(r) if ch not in '. '])
# its cord: out of the top, a loose S across the floor to the first port
_p = gm(GM_X0 + 3, _t - 2.5, GM_Z0)
_cord = [(PAD_X + 11, PAD_Y - 1), (PAD_X + 13, PAD_Y - 4), (PAD_X + 19, PAD_Y - 7), (PAD_X + 28, PAD_Y - 7),
         (PAD_X + 38, PAD_Y - 5), (PAD_X + 47, PAD_Y - 6), (PAD_X + 55, PAD_Y - 9), (round(_p[0]), round(_p[1]) + 2)]
GM_CORD = np.zeros_like(GM_PAD)
for _a, _c in zip(_cord, _cord[1:]):
    GM_CORD |= cv.m_line(*_a, *_c)
GM_CORD &= ~GM_CONSOLE & ~GM_PAD
cv.fill(GM_CORD, BLACK)

cv.masks['controller'] = GM_CONSOLE | GM_PAD | GM_CORD

# vp-check: the console square to the room; the pad lies square too (its stamp's top and bottom level)
cv.persp.edge('console', gm(GM_X0, _t, GM_Z0), gm(GM_X1, _t, GM_Z0), 'h')
cv.persp.edge('console', gm(GM_X0, _b, GM_Z0), gm(GM_X1, _b, GM_Z0), 'h')
cv.persp.edge('console', gm(GM_X0, _t, GM_Z0), gm(GM_X0, _t, GM_Z1))
cv.persp.edge('console', gm(GM_X0, _b, GM_Z0), gm(GM_X0, _b, GM_Z1))
cv.persp.edge('console', gm(GM_X1, _t, GM_Z0), gm(GM_X1, _b, GM_Z0), 'v')
cv.persp.edge('pad', (PAD_X + 2, PAD_Y), (PAD_X + 19, PAD_Y), 'h')
cv.persp.edge('console', gm(GM_X1, _t, GM_Z0), gm(GM_X1, _t, GM_Z1))                 # the top's right edge
cv.persp.edge('cartridge', gm(_ct0, _t + _ch, _cz), gm(_ct1, _t + _ch, _cz), 'h')
cv.persp.edge('cartridge', gm(_ct0, _t + _ch, _cz), gm(_ct0, _t + 1, _cz), 'v')
cv.persp.edge('cartridge', gm(_ct1, _t + _ch, _cz), gm(_ct1, _t + 1, _cz), 'v')
