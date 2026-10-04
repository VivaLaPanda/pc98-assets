# 04b form shading on the machine, before any detail: 2-3 values per plane with banded tiles between ramp neighbours
# (never a flat 16x16 patch). Ambient night light from the window side (left) and above; the glass's own light on
# what faces it comes in 07.
TL, TR, BR, BL = FACE
with cv.only_over(WALL, WALL_SHADE, PAPER):
    # bezel: its top band catches the room's light, the chin turns down into shade toward the foot
    cv.grad(SIL['bezel'], PAPER, WALL, cv.lin((0, TL[1] + 1), (0, TL[1] + 6)))
    cv.grad(SIL['bezel'] & cv.m_poly([RECESS[3], RECESS[2], BR, BL]), WALL, WALL_SHADE,
            cv.lin((0, RECESS[3][1] + 2), (0, BL[1] + 2)))
    # the side: lit at its front corner (it faces the window), falling into shade toward the tube's back and foot
    cv.grad(SIL['side'] & ~SIL['bezel'], WALL, WALL_SHADE, cv.lin((TL[0] - 1, TL[1] + 8), (TL[0] + 3, BL[1] - 6)),
            offset=-0.2)
    # the foot: in the chin's shadow
    cv.grad(SIL['foot'] & ~SIL['bezel'], SLATE, DARK, cv.lin((0, BL[1]), (0, BL[1] + 4)))
