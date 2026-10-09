"""Time of day as registers, for both rooms: each register between its day colour (the room's own day inks) and its
night colour (the bedroom's night as it is today), with a phase tint. Same pixels, new palette: the PC-98 way."""
import numpy as np

PHASES = ['night', 'dawn', 'morning', 'noon', 'afternoon', 'evening', 'sunset', 'dusk']
# how far toward night, and a tint multiplied in linear light (r, g, b)
LOOK = {
    'noon':      (0.00, (1.00, 1.00, 1.00)),
    'morning':   (0.06, (0.97, 0.99, 1.04)),
    'afternoon': (0.06, (1.03, 1.00, 0.93)),
    'evening':   (0.22, (1.10, 0.93, 0.78)),
    'sunset':    (0.40, (1.25, 0.82, 0.72)),
    'dusk':      (0.72, (0.95, 0.88, 1.12)),
    'dawn':      (0.60, (1.12, 0.92, 1.05)),
    'night':     (1.00, (1.00, 1.00, 1.00)),
}


def lin(h: str) -> np.ndarray:
    v = np.array([int(c, 16) * 17 for c in h.lstrip('#')], float) / 255
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def srgb_hex(v: np.ndarray) -> str:
    v = np.clip(v, 0, 1)
    s = np.where(v <= 0.0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - 0.055)
    return '#%x%x%x' % tuple(int(round(c * 255 / 17)) for c in s)


def palette(day: list[str], night: list[str], phase: str, keep: set[int] = frozenset()) -> list[str]:
    """16 registers at `phase`. `keep`: registers that are lights (a screen, lamplight): their own colour always."""
    if phase == 'night':
        return list(night)
    t, tint = LOOK[phase]
    out = []
    for i, (d, n) in enumerate(zip(day, night)):
        if i in keep:
            out.append(day[i])
            continue
        # mix in a perceptual-ish space (sRGB-ish via sqrt) so the night's lifted darks arrive smoothly
        a, b = np.sqrt(lin(d)), np.sqrt(lin(n))
        m = ((1 - t) * a + t * b) ** 2 * np.array(tint)
        out.append(srgb_hex(m))
    return out
