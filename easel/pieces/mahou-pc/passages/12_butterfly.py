# 12 butterfly: a little blue butterfly resting on the balcony rail, wings open, seen through the left pane. Rank 6:
# it should be found, not shine, so it's FLOOR blue on the black city (Bluesky's blue, in this palette) and only
# its wingtips catch the room's light, the CRT side a step brighter.
BF_X, BF_Y = 212, 113                   # top-left of the 9x5 stamp; its feet are on the rail's top (y 118)
cv.stamp(BF_X, BF_Y, '''
CF.....FS
FFF...FFG
FFFF.FFFF
.FFDKDFF.
..FF.FF..
''', {'F': FLOOR, 'G': GLOW, 'S': SCREEN, 'C': GLOW, 'D': SLATE, 'K': BLACK})
BUTTERFLY = cv.m_rect(BF_X, BF_Y, BF_X + 8, BF_Y + 4) & cv.m_where(FLOOR, GLOW, SCREEN, SLATE, BLACK) & ~cv.m_where(BLACK)
BUTTERFLY |= cv.m_rect(BF_X + 4, BF_Y + 3, BF_X + 4, BF_Y + 3)
cv.masks['butterfly'] = BUTTERFLY
