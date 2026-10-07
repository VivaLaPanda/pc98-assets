# 04 objects: the site's eight hotspots as masks on this canvas (the export cuts hit polygons and lit sprites from
# them). The plush, phone, butterfly and TV came with their passages in mahou-pc; here the three the room already
# had (the newspaper moved to the bed in round 3: 16).
SILM = M['SIL']
cv.masks['pc'] = shifted(SILM['crt'] | SILM['bezel'] | SILM['side'] | SILM['top'] | SILM['foot'] | SILM['kb'])
# the balcony door with its glass, frame and curtains, from the rod to the sill; the bed's footboard covers the left
# curtain's foot and the stool's back the right one's, and neither should light up with it
cv.masks['window'] = cv.m_poly([(146, 60), (327, 60), (327, 161), (305, 161), (300, 240), (163, 240), (162, 206),
                                (146, 204)])
# the bookshelf's front, from its top board (the TV sits on it) to its floor line
cv.masks['bookshelf'] = cv.m_poly([(431, 73), (471, 65), (471, 317), (452, 300), (437, 286), (431, 284)])
