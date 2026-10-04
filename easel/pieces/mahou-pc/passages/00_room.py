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
    n = [r * 0.36 + 4, g * 0.38 + 6, b * 0.56 + 31]          # toward navy, hue relations kept (the scout's recipe,
                                                              # a step deeper so the screen is the room's light)
    night[i] = '#%x%x%x' % tuple(min(15, round(v / 17)) for v in n)
for i, h in night.items():
    cv.pal_set(i, h)
# Three pairs land at most one 4096-grid step apart at night (#45a/#55a, #547/#447, #112/#112): merge each pair, and
# the freed registers become the computer's light. Nobody can see the merges; everybody will see the light.
cv.replace(3, 2); cv.replace(4, 6); cv.replace(14, 15)
SCREEN = cv.pal_set(3, '#bef', 'screen')          # the CRT's face
GLOW = cv.pal_set(4, '#89d', 'glow')              # surfaces in its strongest light
WHITE = cv.pal_set(14, '#fff', 'white')           # glare, the hottest pixels
names = dict(paper=0, desk=1, curtain=2, bedspread=5, wall=6, wall_shade=7, desk_shade=8, wood=9, floor=10,
             slate=11, red=12, dark=13, black=15)
for n, i in names.items():
    cv.names[n] = i
globals().update({k.upper(): v for k, v in names.items()})

# The balcony glass: the real PC-98 night skyline (city_overlook) where the day view was, snapped to these 16 inks.
city = np.asarray(Image.open(resolve('explore/places/city_overlook.png')).convert('RGB')).astype(float)
# Only night-sky inks: the overlook's warm haze would otherwise land on the bedspread's brown and read as dusk.
sky = np.array([BLACK, DARK, SLATE, FLOOR, CURTAIN, PAPER, GLOW, SCREEN, WHITE, RED])
pal_rgb = cv.pal[sky].astype(float) * 17
for i, (x0, y0, x1, y1) in enumerate([(191, 32, 235, 118), (240, 32, 283, 118)]):
    cx = 30 + i * 60
    crop = city[18:18 + (y1 - y0), cx:cx + (x1 - x0)]
    d = ((crop[..., None, :] - pal_rgb[None, None]) ** 2).sum(-1)
    d[(crop @ [0.299, 0.587, 0.114] < 70)[..., None] & (np.arange(len(sky)) >= 4)[None, None]] = 1e9   # haze stays dark
    cv.idx[y0:y1, x0:x1] = sky[d.argmin(-1)]
cv.base = cv.idx.copy()                            # the night room is the "before"; what follows is the painting
