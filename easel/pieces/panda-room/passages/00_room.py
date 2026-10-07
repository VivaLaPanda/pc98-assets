# 00 the room: mahou-pc replayed in full (the night room, the computer, the plush, the phone, the butterfly, the TV),
# set into the scene window's 740:528 shape. 500 wide that is 357 tall: 89 new rows, 34 of ceiling above and 55 of
# floor below (the bed's legs reach the floor at ~286 of the old rows, the bolster's end cap at ~285).
import easel

ROOM, _ = easel.run('mahou-pc', pre={'NO_PAPER': True})   # the newspaper moves to the bed (16)
M = ROOM.ns                                   # mahou-pc's names: its camera, light, ramps and object masks
TOP, BOTTOM = 34, 55
assert TOP + ROOM.h + BOTTOM == cv.h
_idx = np.zeros((cv.h, cv.w), np.uint8)
_idx[TOP:TOP + ROOM.h] = ROOM.idx
cv.start_from(_idx, [ROOM.hex(i) for i in range(16)], dict(ROOM.names))
globals().update({k.upper(): v for k, v in ROOM.names.items()})
LIT = M['LIT']
OLD = np.zeros((cv.h, cv.w), bool)            # the old rows: never painted over by the strips
OLD[TOP:TOP + ROOM.h] = True


def shifted(m):
    out = np.zeros((cv.h, cv.w), bool)
    out[TOP:TOP + ROOM.h] = m
    return out


cv.masks = {k: shifted(m) for k, m in ROOM.masks.items()}

# the camera, moved down with the room
VP, D = (M['VP'][0], M['VP'][1] + TOP), M['D']


def proj(X, Y, Z):
    return (round(VP[0] + D * X / Z), round(VP[1] - D * Y / Z))


# -- perspective declarations for `easel vp-check` (paint nothing). The room is one-point: everything square to it
# recedes to VP, its fronts are level, its uprights plumb. Loose things lying askew get their own VP, on the horizon.
def own_vp(dx, dz):
    """The vanishing point of the horizontal direction (dx, dz) (X across, Z into the room)."""
    return (VP[0] + D * dx / dz, VP[1])


cv.persp.vp('room', VP, horizon=True)
# controls: the base picture's own edges (the original artist's room)
cv.persp.edge('back rail', (60, 59.5), (420, 59.5), 'h', control=True)
cv.persp.edge('left rail', (0, 39), (40, 51), control=True)
cv.persp.edge('left scroll', (0, 65), (30, 71), control=True)
cv.persp.edge('right rail', (432, 58), (466, 48), control=True)
cv.persp.edge('closet sill', (482, 329), (497, 343), control=True)      # its far end is behind the tapes (13)
cv.persp.edge('desk', (345, 171), (378, 191), control=True)
cv.persp.edge('desk', (383, 191), (430, 191), 'h', control=True)
cv.persp.edge('door frame', (186, 150), (186, 225), 'v', control=True)
cv.persp.edge('door frame', (287, 150), (287, 225), 'v', control=True)
cv.persp.edge('shelf front', (432, 80), (432, 230), 'v', control=True)
cv.persp.edge('closet post', (469, 100), (469, 300), 'v', control=True)
cv.persp.edge('poster', (65, 75), (65, 145), 'v', control=True)


def _up(p):
    return (p[0], p[1] + TOP)


# mahou-pc's objects, kept: the monitor (a swivel set turned 24 degrees to the room) and the phone (thrown down
# askew). (Its newspaper is left out: round 3 moves it to the bed, 16.) Each runs to its own VPs, which must sit on the horizon.
_th = M['TH']
_F = [_up(p) for p in M['FACE']]                        # TL TR BR BL
cv.persp.edge('pc', _F[0], _F[1], own_vp(np.cos(_th), -np.sin(_th)))
cv.persp.edge('pc', _F[0], _F[3], 'v')
cv.persp.edge('pc', _F[1], _F[2], 'v')
_a = np.radians(M['PH_DEG'])
_ph = lambda u, v: _up(M['ph'](u, v, M['PH_T']))
_w, _l = M['PH_W'] / 2, M['PH_L'] / 2
cv.persp.edge('phone', _ph(-_w, -_l), _ph(-_w, _l), own_vp(np.sin(_a), -np.cos(_a)))
cv.persp.edge('phone', _ph(_w, -_l), _ph(_w, _l), own_vp(np.sin(_a), -np.cos(_a)))
# the rest of each one's edges (round 3: every added object gets a full set, not two or three)
cv.persp.edge('pc', _F[3], _F[2], own_vp(np.cos(_th), -np.sin(_th)))   # the face's bottom, to the same own VP
_K = [_up(p) for p in M['KB']]                                       # BL BR FR FL: the keyboard, square to the desk
cv.persp.edge('keyboard', _K[3], _K[2], 'h')
cv.persp.edge('keyboard', _K[3], _K[0])
_a = np.radians(M['PH_DEG'])
cv.persp.edge('phone', _ph(-_w, -_l), _ph(_w, -_l), own_vp(np.cos(_a), np.sin(_a)))     # its two ends
cv.persp.edge('phone', _ph(-_w, _l), _ph(_w, _l), own_vp(np.cos(_a), np.sin(_a)))
# the plush sits up straight against the headboard: its body's centre line plumb (head to paws)
cv.persp.axis('plush', cv.masks['plush'])
