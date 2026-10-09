# 08b three devices from the image model's cleanup pass (fal, 2026-10-09: this picture in, "redraw these small things
# cleanly in place, off"), snapped to the house's inks: the Corner Table Lamp (a rose shade on a ceramic base), Nest
# Audio L on the sideboard, and the window corner's slender side table with the Windowside lamp and Nest Audio R. In
# each box only the redraw's object pixels are taken; its wall pixels give way to the room's own (its dither and the
# room's differ), and the TV's pixels stay ours.
_dev = np.load(str(SCRATCH / 'fal_living_devices_v2_idx.npy'))
_D = np.zeros((cv.h, cv.w), np.uint8)
_D[TOP:TOP + _dev.shape[0]] = _dev
_wallish = np.isin(_D, [WALL, WALL_SHADE])
_tvish = np.isin(PRE08, [BLACK, DARK, SLATE]) & np.isin(_D, [BLACK, DARK, SLATE])


def take(x0, y0, x1, y1):
    """The redraw's object pixels in a box (final coords); the room's own pixels behind them restored first."""
    box = cv.m_rect(x0, y0 + TOP, x1, y1 + TOP)
    cv.idx[box] = PRE08[box]
    m = box & ~_wallish & ~_tvish
    cv.idx[m] = _D[m]
    return m


SPK_L = take(144, 119, 162, 138)
LAMP_CORNER = take(246, 113, 271, 138)
WINDOW_GROUP = take(354, 145, 393, 212)
SPK_R = WINDOW_GROUP & cv.m_rect(359, 150 + TOP, 373, 167 + TOP) & cv.m_where(PAPER, CURTAIN, GLOW, SLATE)
LAMP_WINDOW_M = WINDOW_GROUP & ~SPK_R


def shade_of(m, frac=0.55):
    """A lamp's shade: its light inks in the top part of its own extent."""
    ys = np.nonzero(m)[0]
    if not len(ys):
        return m
    cut = ys.min() + (ys.max() - ys.min()) * frac
    return m & (YY <= cut) & cv.m_where(PAPER, DESK, DESK_SHADE)


def led_of(m):
    """A speaker's light bar: four pixels across its top row but one."""
    ys, xs = np.nonzero(m)
    if not len(ys):
        return m
    y = ys.min() + 2
    cx = int(round(xs.mean()))
    return cv._mask_pts([(cx - 2 + i, y) for i in range(4)])


cv.masks['speaker_l'] = SPK_L
cv.masks['speaker_r'] = SPK_R
cv.masks['lamp_corner'] = LAMP_CORNER
cv.masks['lamp_window'] = LAMP_WINDOW_M & (YY < 197 + TOP) | (LAMP_WINDOW_M & cv.m_rect(354, 160 + TOP, 393, 212 + TOP))
cv.masks['shade_corner'] = shade_of(LAMP_CORNER)
cv.masks['shade_window'] = shade_of(LAMP_WINDOW_M & cv.m_rect(372, 145 + TOP, 393, 165 + TOP), 0.8)
cv.masks['speaker_l_led'] = led_of(SPK_L)
cv.masks['speaker_r_led'] = led_of(SPK_R)
