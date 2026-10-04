# 07 the screen's light, traced. Every lit surface is put back into the room (inverse projection onto its plane) and
# takes light from a grid of points on the glass: the glass emits forward along its normal (cos), the surface takes it
# by its own facing (cos), 1/r^2, and the desk top, keyboard and stool seat cast shadows. That irradiance is tone
# mapped to ramp steps, and each surface steps up its own ramp in banded tiles (relight). So the cone's edges are the
# glass's plane and the shadow lines of real objects, not a circle: the light is the screen's shape.
ys, xs = np.mgrid[0:cv.h, 0:cv.w].astype(float)

def on_plane_y(Yp):
    """Every pixel as the point of the horizontal plane at height Yp that it shows (below eye level)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        Z = np.where(ys > VP[1], -D * Yp / (ys - VP[1]), np.inf)
        return (xs - VP[0]) * Z / D, np.full_like(xs, Yp), Z

NRM = np.array([-np.sin(TH), 0.0, -np.cos(TH)])                    # the glass faces the stool and the room
SAMPLES = [mon3(u, v, -0.5) for u in np.linspace(-HW + 5, HW - 5, 4) for v in np.linspace(9, H - 4.5, 3)]

def blocked_by_slab(g, X, Y, Z, y_top, x0, x1, z0, z1):
    """Rays from g to points below a horizontal slab's top that cross it inside its extent."""
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (y_top - g[1]) / (Y - g[1])
    xc, zc = g[0] + t * (X - g[0]), g[2] + t * (Z - g[2])
    return (Y < y_top - 0.5) & (t > 0) & (t < 1) & (xc >= x0) & (xc <= x1) & (zc >= z0) & (zc <= z1)

SEAT = dict(c=(70, 178), r=23, y=-93)                              # the stool's seat, from its 58x28px ellipse
def occluded(g, X, Y, Z, desk=True):
    with np.errstate(invalid='ignore'):
        b = blocked_by_slab(g, X, Y, Z, DESK_Y, 106, 215, 166, 226) if desk else np.zeros_like(X, bool)  # desk top
        b |= blocked_by_slab(g, X, Y, Z, DESK_Y + KB_T, KB_X[0], KB_X[1], KB_Z[0], KB_Z[1])  # the keyboard
        t = (SEAT['y'] - g[1]) / (Y - g[1])
        xc, zc = g[0] + t * (X - g[0]), g[2] + t * (Z - g[2])
        b |= (Y < SEAT['y']) & (np.hypot(xc - SEAT['c'][0], zc - SEAT['c'][1]) < SEAT['r'])  # the seat
    return b

def irradiance(pts, normal, mask, desk=True):
    X, Y, Z = pts
    E = np.zeros_like(xs)
    for g in SAMPLES:
        dx, dy, dz = X - g[0], Y - g[1], Z - g[2]
        with np.errstate(invalid='ignore', over='ignore'):
            r = np.sqrt(dx * dx + dy * dy + dz * dz)
            emit = np.clip((NRM[0] * dx + NRM[2] * dz) / r, 0, 1)
            take = np.clip(-(normal[0] * dx + normal[1] * dy + normal[2] * dz) / r, 0, 1)
            e = np.nan_to_num(emit * take / r ** 2)
        e[occluded(g, X, Y, Z, desk)] = 0
        E += e
    return np.where(mask, E / len(SAMPLES), 0)

objects = SIL['crt'] | SIL['kb'] | SIL['paper']
lightable = ~cv.m_where(BLACK)
E_KB = irradiance(on_plane_y(DESK_Y + KB_T), (0, 1, 0), SIL['kb_top'] & lightable)
E_REF = float(np.median(E_KB[E_KB > 0]))                           # the reference: light on the keys
def steps(E, top, per_stop=0.5, at=None, q=4):
    """Irradiance to ramp steps. The traced light gives each surface its shape (terminator, shadow lines, falloff);
    its strength is set per surface, as a painter does: `top` steps where it is brightest (or at `at`, a reference
    irradiance), `per_stop` steps lost per halving. Quantised to 1/q steps so the bands are the tiles' (q=2 on a
    flat printed surface: a 1/4 tile of dots over print reads as dust, a 1/2 checker as light)."""
    ref = at if at is not None else (np.percentile(E[E > 0], 97) if (E > 0).any() else 1)
    with np.errstate(divide='ignore'):
        lv = top + per_stop * np.log2(np.maximum(E, 1e-15) / ref)
    return np.where(E > 0, np.floor(np.clip(lv, 0, top) * q) / q, 0)

desk_top = cv.m_poly([(345, 137), (431, 137), (431, 157), (378, 157)]) & ~objects & lightable
floor = cv.m_region(270, 240, inks=(FLOOR, SLATE, DARK), within=cv.m_rect(140, 196, 480, 267)) & lightable
_fx, _fy, _fz = on_plane_y(-141)
under_desk = (_fx > 104) & (_fz > 164)                              # the floor in the desk's knee space stays dark
seat = cv.m_poly([(302, 178), (330, 168), (358, 175), (356, 192), (318, 196), (300, 190)]) & lightable
E = dict(desk=irradiance(on_plane_y(DESK_Y), (0, 1, 0), desk_top),
         paper=irradiance(on_plane_y(DESK_Y + 0.2), (0, 1, 0), SIL['paper'] & lightable),
         kb=E_KB,
         floor=irradiance(on_plane_y(-141), (0, 1, 0), floor & ~under_desk, desk=False),
         seat=irradiance(on_plane_y(SEAT['y']), (0, 1, 0), seat))

# each surface up its own ramp. Ramps run toward the glow's cool white; line art (BLACK) never lightens.
LIT = {DARK: SLATE, SLATE: FLOOR, FLOOR: GLOW, CURTAIN: PAPER, WALL_SHADE: WALL, WALL: PAPER, WOOD: DESK_SHADE,
       DESK_SHADE: DESK, DESK: PAPER, RED: DESK_SHADE, BEDSPREAD: DESK, PAPER: GLOW, GLOW: SCREEN, SCREEN: WHITE}
KEYS = {**LIT, PAPER: GLOW, GLOW: SCREEN, SCREEN: SCREEN}          # key tops stop at the screen's own ink
cv.relight(desk_top, steps(E['desk'], 2.5, 0.5), LIT, tile_on={DESK_SHADE, DESK, PAPER})
cv.relight(SIL['kb'] & lightable, steps(E['kb'], 1.75, 0.4), KEYS, tile_on={WALL, WALL_SHADE})
# the floor: the cone fanning front-left from the desk, its edge the glass's own plane, cut by the seat's shadow.
# A deliberate cheat, logged in the journal: the desk top would shadow the floor beside it (only the floor out by
# the door is lit in the strict trace, and there it reads as the day's sun come back). The cone is let spill over
# the desk's left edge, as PC-98 rooms let light read by where it falls; the knee space under the desk stays dark.
cv.relight(floor, steps(E["floor"], 0.75, 0.4), {DARK: SLATE, SLATE: FLOOR, FLOOR: GLOW}, tile_on={FLOOR, SLATE, DARK})
cv.relight(seat, steps(E['seat'], 1.5, 0.4), LIT, tile_on={DESK_SHADE, DESK, PAPER, WALL, CURTAIN})
LV_PAPER = steps(E['paper'], 1.5, 0.5)                              # the newspaper takes its light in 08, with its print

# bounce: the newspaper and the desk's lit front-left throw the light back up the wall and onto the calendar.
# Lambertian from each lit pixel (strength = its irradiance) to the wall plane (Z 226, facing us), with the monitor's
# body in the way of whatever lies behind it.
WALL_Z = 226
bx0, by0, bx1, by1 = 330, 28, 436, 140
sub_y, sub_x = ys[by0:by1, bx0:bx1], xs[by0:by1, bx0:bx1]
WX, WY = (sub_x - VP[0]) * WALL_Z / D, -(sub_y - VP[1]) * WALL_Z / D
src = (E['paper'] + E['desk']) * (SIL['paper'] | desk_top)
qy, qx = np.nonzero(src)
keep = np.arange(len(qx)) % 2 == 0
QX, QY, QZ = on_plane_y(DESK_Y)
def inside_monitor(X, Y, Z):
    dX, dZ = X - MC[0], Z - MC[1]
    u = dX * np.cos(TH) - dZ * np.sin(TH)
    w = dX * np.sin(TH) + dZ * np.cos(TH)
    v = Y - (DESK_Y + FOOT_H)
    return (np.abs(u) < HW) & (w > 0) & (w < DEPTH) & (v > 0) & (v < H)
B = np.zeros_like(sub_x)
for y, x in zip(qy[keep], qx[keep]):
    q = (QX[y, x], DESK_Y, QZ[y, x])
    dx, dy, dz = WX - q[0], WY - q[1], WALL_Z - q[2]
    r = np.sqrt(dx * dx + dy * dy + dz * dz)
    b = src[y, x] * np.clip(dy / r, 0, 1) * np.clip(dz / r, 0, 1) / r ** 2
    for f in (0.25, 0.5, 0.75):
        b[inside_monitor(q[0] + f * dx, q[1] + f * dy, q[2] + f * dz)] = 0
    B += b
bounce = np.zeros_like(xs)
bounce[by0:by1, bx0:bx1] = B
lamp = cv.m_rect(388, 66, 421, 97) & ~cv.m_where(WALL, WALL_SHADE)
wall = cv.m_rect(bx0, by0, bx1 - 1, DESK_BACK_Y - 1) & ~objects & ~lamp & lightable & ~cv.m_rect(431, 0, 499, 267)
ref = np.percentile(bounce[wall & (bounce > 0)], 97)
# plus the glass's own spill hugging the bezel's left side (the curved tube leaks light at grazing angles)
gap = cv.dist_from(SIL['crt'])
spill = np.where(xs < FACE[0][0] + 2, np.where(gap <= 3, 1.0, np.where(gap <= 8, 0.5, 0)), 0) * (ys > FACE[0][1] - 6)
# in half steps (dither -> solid -> dither): the wall is a paper/wall dither and the calendar flat print, and a
# quarter tile over either reads as dust. At most a paper/glow checker on the wall, never a solid of the glow ink.
cv.relight_halves(wall, np.maximum(steps(bounce, 1.0, 1.1, at=ref, q=2), spill), LIT)

# grazing rims: the lamp shade's lower lip leans out over the glass; the bookshelf's side panel stands beside the lit
# keys and takes their bounce, fading up from the desk
shade_lip = cv.m_edge(lamp & ~cv.m_where(DARK), 'bottom', inside=True) & cv.m_rect(388, 86, 421, 97)
cv.relight(shade_lip, np.full_like(xs, 1.5), LIT)
panel = cv.m_rect(431, 112, 433, 157) & lightable
cv.relight(panel, np.floor(np.clip(1.25 - (153 - ys) / 32, 0, 1.25) * 4) / 4, LIT)
# things standing in the floor's cone take it on the faces turned up and toward the glass: the chair's chrome star
# and casters (top and right edges), the bin (its right flank and the lip of its mouth)
star = cv.m_rect(294, 197, 366, 238) & cv.m_where(PAPER, WALL, WALL_SHADE, CURTAIN, SLATE) & ~floor
cv.relight((cv.m_edge(star, 'top', inside=True) | cv.m_edge(star, 'right', inside=True)),
           np.full_like(xs, 1.0), LIT)
binm = cv.m_rect(367, 206, 386, 250) & ~cv.m_where(BLACK)            # the bin (x 366-386, y 206-252), inside its outline
cv.relight(cv.m_edge(binm, 'right', inside=True) | (cv.m_edge(binm, 'top', inside=True) & cv.m_rect(366, 205, 387, 210)),
           np.full_like(xs, 1.0), LIT)
# the seat's back: its edge toward the desk catches the screen
back = cv.m_rect(303, 128, 323, 170) & ~cv.m_where(FLOOR, BLACK) & lightable
cv.relight(cv.m_edge(back, 'right', inside=True) & cv.m_rect(316, 128, 323, 170), np.full_like(xs, 1.0), LIT)
