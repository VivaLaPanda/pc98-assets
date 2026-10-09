# 06 the butterfly, again. The first one (9x5, blue on the black city) couldn't be found. Out it goes, and the TV
# from the bookshelf top with it (the TV comes back bigger in 07): their pixels restored from mahou-pc replayed to
# just before them. The new butterfly rests on the left curtain at eye height, where the sheer glows with the moon
# behind it: a dark silhouette with translucent wings, blue lit through, Bluesky's shape (upper wings flared to the
# outer corners, small round lower wings). 19x14, wings open, the edges facing the window catching the moon.
PRE, _ = easel.run('mahou-pc', upto=11, pre={'NO_PAPER': True, 'NO_PHONE': True})
for _k in ('butterfly', 'tv'):
    _m = cv.masks.pop(_k)
    _yy, _xx = np.nonzero(_m)
    _box = cv.m_rect(_xx.min() - 1, _yy.min() - 1, _xx.max() + 1, _yy.max() + 1)
    _old = np.zeros_like(cv.idx); _old[TOP:TOP + PRE.h] = PRE.idx
    cv.idx[_box] = _old[_box]

# Round 5 (the user, 2026-10-09: "way too big. I rarely use bluesky. Should be the same size as the duck"): 15x11,
# the duck's 13x10. Same place on the curtain, same shape (upper wings flared to the corners, small round lower ones),
# drawn whole; the right wing's outer edge, toward the glass, catches the moon.
BF_X, BF_Y = 161, 106
_BF = [
    "KK...........KK",
    "KGK.........KGK",
    "KGGK.......KGGK",
    "KFGGK.....KGGFK",
    "KFGGGK...KGGGFK",
    ".KFGGGKKKGGGFK.",
    ".KFFGGKKKGGFFK.",
    "..KKFFFKFFFKK..",
    "..KFGFKKKFGFK..",
    "..KFFK.K.KFFK..",
    "...KK.....KK...",
]
_rows = []
for _l in _BF:
    _r = list(_l)
    for _x in range(len(_r) - 1, 7, -1):                   # the right wing's outer edge, toward the glass
        if _r[_x] in 'FG' and (_x + 1 == len(_r) or _r[_x + 1] in 'K.'):
            _r[_x] = 'S'
    _rows.append(''.join(_r))
BF_ART = '\n' + '\n'.join(_rows) + '\n'
cv.stamp(BF_X, BF_Y, BF_ART, {'K': BLACK, 'F': FLOOR, 'G': GLOW, 'S': SCREEN, 'D': SLATE})
BUTTERFLY = cv._mask_pts([(BF_X + x, BF_Y + y) for y, r in enumerate(_rows) for x, ch in enumerate(r) if ch not in '. '])
cv.masks['butterfly'] = BUTTERFLY
print('butterfly area', int(BUTTERFLY.sum()))
