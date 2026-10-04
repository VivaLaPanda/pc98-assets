# 00 the room at night. The ground is a real PC-98 background (mahou_bedroom, from the site's library; never committed):
# its 16 inks recovered, then re-tinted for night the way PC-98 games did time of day (same pixels, new registers).
idx, day = quantize('explore/places/mahou_bedroom.png')
cv.start_from(idx, day)
# the room's inks, by what they paint (day colour)
#  0 #fff paper/highlight   1 #fca desk/skin   2 #cde curtain     3 #abf curtain shade  4 #daa pink
#  5 #e92 bedspread         6 #aa9 wall        7 #897 wall shade  8 #c77 desk shade     9 #743 wood/pillar
# 10 #46d floor            11 #557 slate      12 #c14 red        13 #344 dark grey     14 #311 maroon line  15 #111 black
night = {}
for i, h in enumerate(day):
    r, g, b = (int(c, 16) * 17 for c in h[1:])
    n = [r * 0.42 + 8, g * 0.44 + 10, b * 0.56 + 30]         # toward navy, hue relations kept. Lifted a step from the
                                                              # pilot's (.36/.38/.56): the room was murky; the screen and
                                                              # its glow carry the right half, the glass the whole room
    night[i] = '#%x%x%x' % tuple(min(15, round(v / 17)) for v in n)
for i, h in night.items():
    cv.pal_set(i, h)
# Three pairs land one 4096-grid step apart at this tint (#55a/#66a, #657/#557, #212/#112): merge each pair, and the
# freed registers become the computer's light. Nobody can see the merges; everybody will see the light.
cv.replace(3, 2); cv.replace(4, 6); cv.replace(14, 15)
SCREEN = cv.pal_set(3, '#cff', 'screen')          # the CRT's face
GLOW = cv.pal_set(4, '#9be', 'glow')              # surfaces in its strongest light
WHITE = cv.pal_set(14, '#fff', 'white')           # glare, the hottest pixels
names = dict(paper=0, desk=1, curtain=2, bedspread=5, wall=6, wall_shade=7, desk_shade=8, wood=9, floor=10,
             slate=11, red=12, dark=13, black=15)
for n, i in names.items():
    cv.names[n] = i
globals().update({k.upper(): v for k, v in names.items()})

# The balcony glass: the real PC-98 night skyline (city_overlook) where the day view was. The overlook is drawn in
# nine inks; each is given one of ours by its role, not by nearest colour (nearest dims every light to lavender):
# the window must stay the room's brightest, busiest region, the glow of the computer second.
city = np.asarray(Image.open(resolve('explore/places/city_overlook.png')).convert('RGB'))
CITY_INKS = {'000000': BLACK, '424242': SLATE,          # night sky, the haze over the skyline
             '5263bd': GLOW, 'adbdff': SCREEN,          # lit windows: the cool lights
             'ffad00': WHITE, '52bd73': GLOW,           # street lamps and signs: the sparkle
             'de0042': RED, '738c9c': PAPER, '106342': FLOOR}

def city_patch(cx, cy, w, h):
    """city_overlook's pixels at (cx, cy) in the room's inks."""
    crop = city[cy:cy + h, cx:cx + w]
    out = np.full(crop.shape[:2], BLACK, np.uint8)
    for hx, ink in CITY_INKS.items():
        out[(crop == [int(hx[i:i + 2], 16) for i in (0, 2, 4)]).all(-1)] = ink
    return out

PANES = [(191, 235), (240, 284)]                   # the two leaves of the balcony door (x0, x1)
for i, (x0, x1) in enumerate(PANES):
    cv.idx[32:118, x0:x1] = city_patch(30 + i * 60, 18, x1 - x0, 86)

# Daylight that survived the re-tint goes (this is the scene's timing, so it belongs to the "before", not the painting).
# 1 Behind the railing (y 134-172) the day view of a sunlit building and stairs: the street-level city instead, the
#   balusters left standing as silhouettes against it (their pale sunlit bodies dropped to the dark ramp).
POSTS = [194, 208, 221, 245, 258, 271]             # each baluster's left edge (5px wide), from the day picture
posts = np.zeros((cv.h, cv.w), bool)
for x in POSTS:
    posts[134:173, x:x + 5] = True
# a near block of lit windows low in the view (the overlook's rows 172-211), continuous across the mullion
low = cv.m_rect(188, 134, 230, 172) | cv.m_rect(237, 134, 283, 172)
sub = np.zeros((cv.h, cv.w), np.uint8)
sub[134:173, 188:284] = city_patch(162, 172, 96, 39)
cv.idx[low & ~posts] = sub[low & ~posts]
# the balusters as silhouettes against it: dark body, black outline, one slate line where the room's light catches them
for x in POSTS:
    cv.idx[134:173, x:x + 5] = DARK
    cv.idx[134:173, [x, x + 4]] = BLACK
    cv.idx[134:173, x + 3] = SLATE
# 2 The balcony deck and door track under it (y 173-197) were sunlit slats: two steps down the dark ramp, so the slats
#   still read but lie in the night.
DIM = {PAPER: SLATE, CURTAIN: SLATE, DESK: DESK_SHADE, WALL: WALL_SHADE, WALL_SHADE: DARK, DESK_SHADE: WOOD,
       BEDSPREAD: WOOD, FLOOR: SLATE, SLATE: DARK, WOOD: DARK, DARK: BLACK, RED: WOOD}
deck = cv.m_rect(188, 173, 283, 197)
for _ in range(2):
    new = cv.idx.copy()
    for k, v in DIM.items():
        new[deck & (cv.idx == k)] = v
    cv.idx[:] = new
# 3 The sun patch on the floor in front of the door (the day's pale floor ink, cut by the mullion's shadow): floor again.
#   The whole floor is one connected field of the two inks (the patch's dithered edge included); objects standing on it
#   are walled off by their outlines, so their own pale-blue pixels survive.
floor = cv.m_region(270, 240, inks=(CURTAIN, FLOOR), within=cv.m_rect(140, 200, 345, 267))
floor |= cv.m_region(152, 262, inks=(CURTAIN, FLOOR), within=cv.m_rect(140, 236, 175, 267))   # cut off by the bolster
cv.idx[floor & (cv.idx == CURTAIN)] = FLOOR
cv.idx[cv.m_rect(229, 205, 237, 216) & (cv.idx == SLATE)] = FLOOR                    # the mullion's shadow, its stub
# 4 The curtains' white sun highlights (the day's #fff on the folds): down to the curtain's own ink.
curtains = cv.m_rect(143, 28, 186, 206) | cv.m_rect(285, 28, 326, 206)
cv.idx[curtains & (cv.idx == PAPER)] = CURTAIN
cv.base = cv.idx.copy()                            # the night room is the "before"; what follows is the painting
