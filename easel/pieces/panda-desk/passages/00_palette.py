# 00 palette, planned by role before a single pixel (technique: order of work, step 1).
# Night room lit by a CRT (cool) with a city behind the glass (amber/pink accents). Black dominates.
K  = cv.pal_set(0,  '#000', 'black')
AB = cv.pal_set(1,  '#112', 'abyss')      # room dark ramp: carries everything in shadow
NV = cv.pal_set(2,  '#223', 'navy')
DU = cv.pal_set(3,  '#335', 'dusk')
SL = cv.pal_set(4,  '#557', 'slate')
LV = cv.pal_set(5,  '#99b', 'lavender')   # cool-lit plastic and paper
WH = cv.pal_set(6,  '#fff', 'white')      # light sources and speculars only
DB = cv.pal_set(7,  '#236', 'deepblue')   # screen-light ramp: glass, glow, screen face
BL = cv.pal_set(8,  '#47b', 'blue')
CY = cv.pal_set(9,  '#8ce', 'cyan')
PL = cv.pal_set(10, '#def', 'pale')
W1 = cv.pal_set(11, '#322', 'wood_dk')    # desk wood ramp
W2 = cv.pal_set(12, '#543', 'wood')
W3 = cv.pal_set(13, '#865', 'wood_lt')
AM = cv.pal_set(14, '#fb5', 'amber')      # city windows, a warm accent
PK = cv.pal_set(15, '#e5a', 'pink')       # neon, LEDs
