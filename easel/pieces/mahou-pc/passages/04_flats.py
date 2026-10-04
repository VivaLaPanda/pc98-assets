# 04 flats, by plane. The room is lit (at night, faintly) from the window on the left, so left-facing planes are a
# step lighter; the machine is 90s beige plastic, which this night palette carries as paper (#77a) / wall (#557) /
# wall shade (#456). The glass is the brightest flat in the room's right half: it is the light.
def flat(mask, c):
    with cv.only_over(G):
        cv.fill(mask, c)

flat(SIL['paper'], PAPER)
flat(SIL['kb_top'], WALL)
flat(SIL['kb_lip'], WALL_SHADE)
flat(cv.m_poly(GLASS), GLOW)
flat(cv.m_poly(RECESS), DARK)
flat(SIL['top'] & ~SIL['bezel'], PAPER)
flat(SIL['side'] & ~SIL['bezel'], WALL_SHADE)
flat(SIL['bezel'], WALL)
flat(SIL['foot'], SLATE)
objects = SIL['crt'] | SIL['kb'] | SIL['paper']
left = int((objects & (cv.idx == G)).sum())
assert left == 0, f'{left} ground pixels unfilled'
