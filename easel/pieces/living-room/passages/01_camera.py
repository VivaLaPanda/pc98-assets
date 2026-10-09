# 01 the room's camera and regions. Fermion's room is drawn loosely one-point (its left wall's lines and its table's
# edges disagree by ~15px on eye level), so new things are built in one camera fitted to the cues that matter where
# they stand: the floorboards' spacing and the table's edges (VP), the back wall's glass door (200cm) against its floor
# line (eye height), a 120x75cm table (focal distance). Y up from the eye (cm), Z into the room, X to the right.
VP, D, EYE = (265, 165), 170, 116
FLOOR_Y = -EYE
BACK_Z = D * EYE / (240 - VP[1])                    # the back wall's floor line, y 240: Z ~263
YY, XX = np.mgrid[0:cv.h, 0:cv.w]


def pf(p):
    """A room point (X, Y, Z) cm on the canvas."""
    X, Y, Z = p
    return (VP[0] + D * X / Z, VP[1] - D * Y / Z)


def on_floor(x, y):
    """The floor point under a canvas pixel (X, Z cm), below eye level."""
    Z = D * EYE / np.maximum(np.asarray(y, float) - VP[1], 1e-6)
    return (np.asarray(x, float) - VP[0]) * Z / D, Z


# the room's surfaces, as drawn (canvas px): the walls meet the ceiling at y 78 on the back wall, the left wall's top
# runs (0,49)-(57,77); the back wall's corners are x 57 and x 382; its floor line is y 240
CEIL_POLY = [(0, 30), (437, 30), (395, 48), (383, 62), (382, 78), (57, 78), (0, 49)]
BACK_POLY = [(58, 79), (381, 79), (381, 240), (58, 240)]
LEFT_POLY = [(0, 50), (57, 78), (57, 240), (0, 246)]
RIGHT_UPPER_POLY = [(383, 62), (395, 48), (437, 30), (500, 30), (500, 34), (383, 100)]   # above the curtain rod
REGION = {k: cv.m_poly(v) for k, v in (('ceil', CEIL_POLY), ('back', BACK_POLY), ('left', LEFT_POLY),
                                       ('right_upper', RIGHT_UPPER_POLY))}

# what stands on or against the back wall, as drawn
OBJ_POLY = {
    'glass_door': [(62, 100), (129, 100), (129, 238), (62, 238)],
    'left_door': [(10, 86), (47, 98), (47, 236), (10, 240)],
    'clock': [(204, 91), (236, 91), (236, 125), (204, 125)],
    'switch': [(133, 150), (140, 150), (140, 162), (133, 162)],
    'sideboard': [(143, 160), (285, 160), (285, 241), (143, 241)],
    'vent': [(276, 101), (303, 101), (303, 178), (276, 178)],
    'tv': [(288, 154), (377, 154), (377, 242), (288, 242)],
    'ac': [(350, 48), (397, 48), (397, 108), (350, 108)],
}
OBJ = {k: cv.m_poly(v) for k, v in OBJ_POLY.items()}
