# 01 underdrawing: the room's own camera, then every new object built in it. Nothing on the canvas yet.
# One-point room: the desk's receding left edge (345,137)->(378,157) and the floor lines meet at VP, eye level y 80.
# The room is drawn wide-angle, as PC-98 rooms are: the desk's depth against its height, and the stool's round seat
# (58 wide, 28 tall, 102px below eye level) both give a focal distance of ~200px. So the camera: eye at height 0,
# Y up in cm, Z into the room. Scale from the balcony door (200cm = 177px at the back wall): back wall Z 226,
# floor Y -141, desk top Y -64 (front edge Z 166, back Z 225), desk's left edge X 106.
VP, D = (250, 80), 200

def proj(X, Y, Z):
    """A point of the room (cm) on the canvas."""
    return (round(VP[0] + D * X / Z), round(VP[1] - D * Y / Z))

def toward(p, f):
    """The point a fraction f of the way from p to the vanishing point (what recedes into the room)."""
    return (round(p[0] + (VP[0] - p[0]) * f), round(p[1] + (VP[1] - p[1]) * f))

DESK_Y, DESK_BACK_Y, DESK_FRONT_Y = -64, 137, 157
ud.ray(VP, (378, 157), '#8f8'); ud.ray(VP, (432, 157), '#8f8')
ud.line((330, DESK_BACK_Y), (440, DESK_BACK_Y), '#f84'); ud.line((370, DESK_FRONT_Y), (440, DESK_FRONT_Y), '#f84')
ud.label(252, 82, 'VP', col='#ff4')

# The monitor: a 17" CRT on a swivel foot, turned 24 degrees toward the room (its glass now faces the stool and the
# viewer; the right edge comes forward). Built in its own frame: u along the face (left to right), v up, w back.
TH = np.radians(24)
MC = (137, 183)                       # face centre (X, Z): its right edge stops short of the bookshelf
FOOT_H = 6                            # a tilt-swivel base: the chin stands clear of the desk
def mon3(u, v, w):
    """A point of the monitor (u right, v up from its underside, w back into the tube) in the room (cm)."""
    return (MC[0] + u * np.cos(TH) + w * np.sin(TH), DESK_Y + FOOT_H + v, MC[1] - u * np.sin(TH) + w * np.cos(TH))
def mon(u, v, w):
    """The same point on the canvas."""
    return proj(*mon3(u, v, w))
HW, H = 19.5, 37                      # bezel half width, height (cm)
FACE = [mon(-HW, H, 0), mon(HW, H, 0), mon(HW, 0, 0), mon(-HW, 0, 0)]                 # TL TR BR BL
# glass: 4cm sides, 3.5cm top, an 8cm chin with the controls
GLASS = [mon(-HW + 4, H - 3.5, -0.5), mon(HW - 4, H - 3.5, -0.5), mon(HW - 4, 8, -0.5), mon(-HW + 4, 8, -0.5)]
RECESS = [mon(-HW + 3, H - 2.5, 0), mon(HW - 3, H - 2.5, 0), mon(HW - 3, 7, 0), mon(-HW + 3, 7, 0)]
# the tube housing: a flat top for 18cm behind the bezel (a 2px sliver from this eye height), then the tube tapers
# to a 24x22 back 38cm deep that sits low
BACK_HW, BACK_V0, BACK_V1, DEPTH = 12, 5, 27, 38
SIDE = [mon(-HW, H, 2), mon(-HW, 0, 2), mon(-HW + 1, 1, 8), mon(-BACK_HW, BACK_V0, DEPTH), mon(-BACK_HW, BACK_V1, DEPTH),
        mon(-HW + 1, H - 0.5, 18), mon(-HW, H, 2)]
TOP = [mon(-HW, H, 0), mon(HW, H, 0), mon(HW, H, 2), mon(HW - 1, H - 0.5, 18), mon(-HW + 1, H - 0.5, 18), mon(-HW, H, 2)]
# swivel foot: a low drum under the tube's centre of mass
FOOT_C, FOOT_R = (0, 14), (9, 7)     # (u, w) centre and radii
FOOT = [mon(FOOT_C[0] + FOOT_R[0] * np.cos(a), 0, FOOT_C[1] + FOOT_R[1] * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)]
for q, c in ((FACE, '#4af'), (GLASS, '#4ff'), (SIDE, '#4af'), (TOP, '#4af'), (FOOT, '#a6f')):
    ud.poly(q, c)
ud.label(FACE[0][0], FACE[0][1] - 8, 'crt 17in, 24deg', '#4af')

# keyboard: square to the desk, tucked under the chin (3cm tall, the bezel's 4cm up), 1cm back from the edge
KB_X, KB_Z, KB_T = (117, 150), (167, 178), 3
KB = [proj(KB_X[0], DESK_Y + KB_T, KB_Z[1]), proj(KB_X[1], DESK_Y + KB_T, KB_Z[1]),
      proj(KB_X[1], DESK_Y + KB_T, KB_Z[0]), proj(KB_X[0], DESK_Y + KB_T, KB_Z[0])]               # BL BR FR FL
KB_LIP = [KB[3], KB[2], proj(KB_X[1], DESK_Y, KB_Z[0]), proj(KB_X[0], DESK_Y, KB_Z[0])]
# newspaper: a broadsheet folded in half and thrown down at the desk's front left corner, a little askew; its near
# right corner goes under the keyboard's end
def desk(X, Z):
    return proj(X, DESK_Y, Z)
def on_desk(c, deg, x, z):
    """A point (x across, z along) of something lying on the desk at c, turned deg."""
    a = np.radians(deg)
    return desk(c[0] + x * np.cos(a) - z * np.sin(a), c[1] + x * np.sin(a) + z * np.cos(a))
NP_C, NP_DEG, NP_HALF = (116, 186), -14, (9, 16)
NP = [on_desk(NP_C, NP_DEG, sx * NP_HALF[0], sz * NP_HALF[1]) for sx, sz in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
FOLD = (on_desk(NP_C, NP_DEG, 0, NP_HALF[1]), on_desk(NP_C, NP_DEG, 0, -NP_HALF[1]))
if globals().get('NO_PAPER'):        # a piece built on this one puts the newspaper elsewhere (panda-room: on the bed)
    NP, FOLD = [(-50, -50)] * 4, ((-50, -50), (-50, -50))       # off the canvas: nothing is cleared, drawn or lit
for q, lab in ((KB, 'kbd'), (NP, 'paper')):
    ud.poly(q, '#a6f'); ud.label(q[0][0], q[0][1] - 8, lab, '#a6f')

# the lamp keeps the original artist's stem: it now stands on the desk behind the monitor (its foot hidden by it)

# the light: the glass is the source, its normal (-sin, 0, -cos) turned toward the stool and the floor in front
GC = mon(0, (H - 3.5 + 8) / 2, -0.5)
LIGHT = GC
NORMAL = (-np.sin(TH), -np.cos(TH))
ud.cross(*GC, '#ff4')
ud.ray(GC, proj(MC[0] - 120 * np.sin(TH), DESK_Y + 20, MC[1] - 120 * np.cos(TH)), '#ff4')
