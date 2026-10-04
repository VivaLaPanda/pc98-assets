# 07 the screen's light. Each surface steps up its own ramp toward the CRT's cool light in banded tiles (relight):
# strong where it faces the glass and is near it, concentric bands fading outward, nothing on the far side of things.
# Line art (BLACK) is never lightened.
LIT = {DARK: SLATE, SLATE: FLOOR, FLOOR: CURTAIN, CURTAIN: PAPER, WALL_SHADE: WALL, WALL: PAPER, WOOD: DESK_SHADE,
       DESK_SHADE: DESK, DESK: PAPER, RED: DESK_SHADE, BEDSPREAD: DESK, PAPER: GLOW, GLOW: SCREEN, SCREEN: WHITE}
ys, xs = np.mgrid[0:cv.h, 0:cv.w]
S = LIGHT
dist = np.hypot(xs - S[0], ys - S[1])
lightable = ~cv.m_where(BLACK)
objects = SIL['crt'] | SIL['case'] | SIL['kb'] | SIL['paper']

def pool(cx, cy, rx, ry, amp):
    """A pool of light on a horizontal surface: elliptical, amp steps at its centre, banding out to nothing."""
    return amp * np.clip(1 - np.hypot((xs - cx) / rx, (ys - cy) / ry), 0, 1)

# the desk top in front of the machine: the brightest pool, centred where the glass throws forward and down
desk_top = cv.m_poly([(345, 138), (431, 138), (431, 156), (378, 156)])
cv.relight(desk_top & ~objects & lightable, pool(410, 150, 48, 15, 3.2), LIT, tile_on={DESK_SHADE, DESK})
cv.relight(SIL['kb'] & lightable, pool(410, 150, 40, 14, 1.4), LIT, tile_on={WALL})
cv.relight(cv.m_poly(case_top) & lightable, pool(410, 132, 30, 6, 1.0), LIT)
# the bezel just around the glass and the chin catch a little of it (light bouncing off the glass's own face)
cv.relight(SIL['crt'] & ~cv.m_rect(RC['l'], RC['t'], RC['r'], RC['b']) & lightable,
           0.6 * np.clip(1 - (dist - 12) / 10, 0, 1), LIT)
# the wall and calendar around the monitor: a halo in concentric bands, behind everything on the desk
# (wall inks only: the lamp and the calendar are separate objects and get their own light, not a smear)
gap = cv.dist_from(SIL['crt'])                                    # rings out from the monitor's silhouette
wall = cv.m_rect(330, 60, 430, 136) & ~objects & cv.m_where(WALL, WALL_SHADE)
cv.relight(wall, 1.6 * np.clip(1 - gap / 16, 0, 1) * np.clip(1.25 - (ys - LIGHT[1]) / -60, 0, 1), LIT,
           tile_on={WALL, WALL_SHADE})
# rims: the underside of the lamp shade and the bookshelf's side panel face the glass
shade = cv.m_rect(392, 84, 419, 96) & ~cv.m_where(WALL, WALL_SHADE, BLACK) & ~objects
cv.relight(cv.m_edge(shade, 'bottom', inside=True), np.full((cv.h, cv.w), 1.5), LIT)
panel = cv.m_rect(431, 92, 433, 170) & lightable
cv.relight(panel, 1.3 * np.clip(1 - np.abs(ys - 118) / 50, 0, 1), LIT)
# far: the stool's cushion, the floor beyond the desk's shadow and the bin's near side get the faintest bands
far = 0.9 * np.clip(1 - (dist - 60) / 90, 0, 1)
cushion = cv.m_poly([(302, 178), (330, 168), (358, 175), (356, 192), (318, 196), (300, 190)]) & lightable
cv.relight(cushion, far, LIT, tile_on={WALL, DESK})
floor = cv.m_poly([(300, 205), (440, 196), (470, 268), (300, 268)]) & cv.m_where(FLOOR, CURTAIN, SLATE)
cv.relight(floor, 0.8 * far, LIT, tile_on={FLOOR})
