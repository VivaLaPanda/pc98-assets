# 00 the room: mahou-pc replayed in full (the night room, the computer, the plush, the phone, the butterfly, the TV),
# set into the scene window's 740:528 shape. 500 wide that is 357 tall: 89 new rows, 34 of ceiling above and 55 of
# floor below (the bed's legs reach the floor at ~286 of the old rows, the bolster's end cap at ~285).
import easel

ROOM, _ = easel.run('mahou-pc')
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
