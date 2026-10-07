# 06 the butterfly, again. The first one (9x5, blue on the black city) couldn't be found. Out it goes, and the TV
# from the bookshelf top with it (the TV comes back bigger in 07): their pixels restored from mahou-pc replayed to
# just before them. The new butterfly rests on the left curtain at eye height, where the sheer glows with the moon
# behind it: a dark silhouette with translucent wings, blue lit through, Bluesky's shape (upper wings flared to the
# outer corners, small round lower wings). 19x14, wings open, the edges facing the window catching the moon.
PRE, _ = easel.run('mahou-pc', upto=11, pre={'NO_PAPER': True})
for _k in ('butterfly', 'tv'):
    _m = cv.masks.pop(_k)
    _yy, _xx = np.nonzero(_m)
    _box = cv.m_rect(_xx.min() - 1, _yy.min() - 1, _xx.max() + 1, _yy.max() + 1)
    _old = np.zeros_like(cv.idx); _old[TOP:TOP + PRE.h] = PRE.idx
    cv.idx[_box] = _old[_box]

BF_X, BF_Y = 162, 110
BF_ART = '''
KKK.............KKK
KFSKK.........KKFSK
KFGGFKK.....KKFGGSK
KFGGGFFK...KFFGGGFK
KFGGGGFFK.KFFGGGGFK
.KFGGGFFFKFFFGGGFK.
.KFFGGFFDKDFFGGFFK.
..KFFFFFDKDFFFFFK..
...KKKFDDKDDFKKK...
..KFFFFDDKDDFFFFK..
.KFGGFFFKKKFFFGGSK.
.KFGFFFK.K.KFFFGFK.
..KFFFK.....KFFFK..
...KKK.......KKK...
'''
cv.stamp(BF_X, BF_Y, BF_ART, {'K': BLACK, 'F': FLOOR, 'G': GLOW, 'S': SCREEN, 'D': SLATE})
_rows = BF_ART.strip('\n').splitlines()
BUTTERFLY = cv._mask_pts([(BF_X + x, BF_Y + y) for y, r in enumerate(_rows) for x, ch in enumerate(r) if ch not in '. '])
cv.masks['butterfly'] = BUTTERFLY
