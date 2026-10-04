# 11 phone: Panda's phone, face up on the bedspread with a chat open. After the window and the CRT it's the
# brightest thing in the room, and it lights a small pool of the bedspread around it.
# The mattress top: the pillow line (y 180) sits at the back wall (Z 226) and the front edge (y 237) at Z 137,
# both on one plane Y -113 under this camera.
BED_Y = -113


def bed_inv(x, y):
    """The point of the mattress plane (X, Z in cm) under a canvas pixel."""
    Z = D * -BED_Y / np.maximum(y - VP[1], 1e-6)
    return (x - VP[0]) * Z / D, Z


PH_C, PH_DEG, PH_W, PH_L, PH_T = np.array([-128.0, 178.0]), 78, 7.6, 16.0, 0.8   # a 6.5" phone, lying askew
_th = np.radians(PH_DEG)
PH_A = np.array([np.sin(_th), -np.cos(_th)])        # along the phone, toward its bottom (nearer the viewer)
PH_B = np.array([np.cos(_th), np.sin(_th)])         # across it, left to right


def ph(u, v, y=0.0):
    X, Z = PH_C + u * PH_B + v * PH_A
    return proj(X, BED_Y + y, Z)


def ph_rect(u0, v0, u1, v1, y=0.0):
    return [ph(u0, v0, y), ph(u1, v0, y), ph(u1, v1, y), ph(u0, v1, y)]


PH_TOP = cv.m_poly(ph_rect(-PH_W / 2, -PH_L / 2, PH_W / 2, PH_L / 2, PH_T))
PH_BODY = PH_TOP | np.roll(PH_TOP, 1, axis=0)       # with its near sides: 0.8cm is under a pixel, so one row
ud.poly(ph_rect(-PH_W / 2, -PH_L / 2, PH_W / 2, PH_L / 2, PH_T), '#4ff')

# phone-local (u, v) of every pixel, through the mattress plane (the screen is 0.8cm up: close enough at this size)
_X, _Z = bed_inv(XX + 0.5, YY + 0.5)
_d = np.stack([_X - PH_C[0], _Z - PH_C[1]])
PU, PV = PH_B[0] * _d[0] + PH_B[1] * _d[1], PH_A[0] * _d[0] + PH_A[1] * _d[1]

PH_GLASS = PH_TOP & (np.abs(PV) <= PH_L / 2 - 0.9) & ~cv.m_edge(PH_TOP)    # side bezels are under a pixel

cv.fill(PH_BODY, BLACK)
cv.fill(PH_BODY & ~PH_TOP, SLATE)                                   # the near sides catch the screen's spill
# the chat: a light theme (Signal's): header, blue sent bubbles at the right, grey received ones at the left,
# the input bar at the bottom
v0 = -PH_L / 2 + 0.9
UI = [((v0, v0 + 2.0), (-9, 9), GLOW),
      ((v0 + 3.6, v0 + 4.8), (-9, 0.6), GLOW),
      ((v0 + 6.2, v0 + 7.6), (-0.8, 9), FLOOR),
      ((v0 + 9.0, v0 + 10.2), (-9, 1.2), GLOW),
      ((v0 + 11.0, v0 + 12.4), (0.2, 9), FLOOR)]
cv.fill(PH_GLASS, SCREEN)
for (va, vb), (ua, ub), c in UI:
    cv.fill(PH_GLASS & (PV >= va) & (PV < vb) & (PU >= ua) & (PU < ub), c)

# the pool: light from a face-up screen grazes the cloth around it; traced as distance on the mattress (cm),
# strength chosen: a step and a bit at the phone's edge, gone by 9cm. Capped at GLOW (the screen stays hotter).
_du = np.maximum(np.abs(PU) - PH_W / 2, 0)
_dv = np.maximum(np.abs(PV) - PH_L / 2, 0)
PH_DIST = np.hypot(_du, _dv)
CLOTH = cv.m_rect(70, 186, 140, 236) & cv.m_where(BEDSPREAD, DESK, PAPER, RED, DESK_SHADE, CURTAIN, WOOD) & ~PH_BODY
POOL_RAMP = {k: v for k, v in LIT.items() if k not in (GLOW, SCREEN)}
cv.relight(CLOTH, np.clip(1.7 - PH_DIST / 6.0, 0, None), POOL_RAMP,
           tile_on=(BEDSPREAD, DESK, RED, DESK_SHADE, WOOD))     # the lit PAPER folds step only whole: no sparkle

cv.masks['phone'] = PH_BODY.copy()
