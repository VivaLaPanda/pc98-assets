# 19 the desk lamp (not one of Panda's real lights: a visitor can click it on and off, the site lights it): the arm
# lamp over the monitor, its head turned down to the desk. Nothing is painted; its masks: the lamp, and the head's
# opening (what glows when it's on).
DESK_LAMP = cv.m_poly([(388, 108), (398, 101), (410, 101), (418, 108), (418, 138), (410, 138), (406, 128), (394, 126),
                       (388, 118)]) & ~cv.m_where(WALL, WALL_SHADE)
cv.masks['desk_lamp'] = DESK_LAMP
cv.masks['shade_desk'] = DESK_LAMP & cv.m_poly([(389, 116), (397, 119), (405, 123), (404, 127), (393, 126), (388, 119)])
