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

# Round 4: bigger (rank 6: above the letter, the tapes and the duck in size): 31x22, a big swallowtail's span, its
# wings lit through brighter. Drawn as the left half and mirrored; the edges facing the glass (its right) catch the
# moon.
BF_X, BF_Y = 153, 101
_BF_LEFT = [
    "KKK............", "KGGKK..........", "KGGGGKK........", "KFGGGGGKK......", "KFGGGGGGGKK....",
    "KFGGGGGGGGFKK..", "KFGGGGGGGGFFFK.", ".KFGGGGGGGGFFFD", ".KFGGGGGGGGFFDD", ".KFFGGGGGGFFFDD",
    "..KFFGGGGFFFFDD", "..KFFFGGFFFFDDD", "...KFFFFFFFFDDD", "....KKKKFFFFDDD", "....KFFFFFFFDDD",
    "...KFGGGFFFFFDK", "...KFGGGGFFFFK.", "...KFGGGGFFFK..", "...KFGGGFFFK...", "....KFGGFFK....",
    ".....KFFFK.....", "......KKK......",
]
_BF_BODY = "." * 7 + "K" * 8 + "." * 7
_rows = []
for _y, _l in enumerate(_BF_LEFT):
    _r = list(_l + _BF_BODY[_y] + _l[::-1])
    for _x in range(len(_r) - 1, 15, -1):                  # the right wing's outer edge, toward the glass
        if _r[_x] in 'FG' and (_x + 1 == len(_r) or _r[_x + 1] in 'K.'):
            _r[_x] = 'S'
    _rows.append(''.join(_r))
BF_ART = '\n' + '\n'.join(_rows) + '\n'
cv.stamp(BF_X, BF_Y, BF_ART, {'K': BLACK, 'F': FLOOR, 'G': GLOW, 'S': SCREEN, 'D': SLATE})
_rows = BF_ART.strip('\n').splitlines()
BUTTERFLY = cv._mask_pts([(BF_X + x, BF_Y + y) for y, r in enumerate(_rows) for x, ch in enumerate(r) if ch not in '. '])
cv.masks['butterfly'] = BUTTERFLY
print('butterfly area', int(BUTTERFLY.sum()))
