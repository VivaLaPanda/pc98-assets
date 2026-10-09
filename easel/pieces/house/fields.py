"""Lamplight for the house's rooms, traced: every pixel as a point of the room (a G-buffer from the room's camera: its
floor, walls and ceiling as planes, the things built as surfaces with their own depth and normals), each lamp a point
(or a small disc) that lights it by distance and facing. The strength curve is a painter's choice (true 1/r^2 leaves
anything a metre off invisible): the field is tone-mapped to 0..255, which the site's renderer scales by the lamp's
brightness and colours by its Kelvin."""
from dataclasses import dataclass

import numpy as np


@dataclass
class GBuffer:
    P: np.ndarray        # (h, w, 3) cm: the room point each pixel shows (nan where none: the sky)
    N: np.ndarray        # (h, w, 3) its normal (unit)


@dataclass
class Lamp:
    pos: tuple[float, float, float]
    kind: str = 'omni'   # omni | down (a dome over a seat) | up (a torchiere: lights the ceiling, which lights the room)
    reach: float = 160.0  # cm where the field falls to about a quarter
    gain: float = 1.0


def irradiance(g: GBuffer, lamp: Lamp) -> np.ndarray:
    d = np.asarray(lamp.pos, float)[None, None] - g.P
    r = np.linalg.norm(d, axis=-1)
    ok = np.isfinite(r)
    r = np.where(ok, np.maximum(r, 8.0), 1e9)
    L = d / r[..., None]
    facing = np.clip((g.N * L).sum(-1), 0, 1) * 0.75 + 0.25        # a wrap: soft things take light round their edges
    fall = 1.0 / (1.0 + (r / lamp.reach) ** 2 * 3.0)
    if lamp.kind == 'down':
        below = np.clip(d[..., 1] / r, 0, 1)                          # cos of the angle under the dome's axis
        fall = fall * np.where(d[..., 1] > 0, 0.25 + 0.75 * below, 0.08)
    E = np.where(ok, facing * fall, 0.0) * lamp.gain
    return E


def ceiling_bounce(g: GBuffer, lamp: Lamp, ceiling_y: float) -> np.ndarray:
    """An uplight: its pool on the ceiling, then that pool as a broad source for the room below."""
    pool = Lamp((lamp.pos[0], ceiling_y - 5, lamp.pos[2]), 'omni', lamp.reach * 1.6, lamp.gain * 0.7)
    on_ceiling = np.isfinite(g.P[..., 1]) & (g.P[..., 1] > ceiling_y - 3)
    near = Lamp(lamp.pos, 'omni', lamp.reach * 0.45, lamp.gain * 0.5)
    E = irradiance(g, pool) + irradiance(g, near)
    d = np.linalg.norm(g.P - np.asarray(pool.pos)[None, None], axis=-1)
    E = np.where(on_ceiling, np.maximum(E, lamp.gain / (1 + (np.nan_to_num(d, nan=1e9) / (lamp.reach * 0.9)) ** 2)), E)
    return E


def window(g: GBuffer, points: np.ndarray, inward: tuple[float, float, float], reach: float) -> np.ndarray:
    """Daylight through glass: a grid of points on the pane, each sending light inward (cos to the pane's normal),
    each lit surface taking it by its own facing and the distance."""
    n_in = np.asarray(inward, float)
    E = np.zeros(g.P.shape[:2])
    for p in points:
        d = np.asarray(p, float)[None, None] - g.P                    # surface -> pane point
        r = np.linalg.norm(d, axis=-1)
        ok = np.isfinite(r)
        r = np.where(ok, np.maximum(r, 10.0), 1e9)
        L = d / r[..., None]
        emit = np.clip(-(L * n_in).sum(-1), 0, 1)                     # how squarely the pane faces the surface
        take = np.clip((g.N * L).sum(-1), 0, 1) * 0.8 + 0.2
        E += np.where(ok, emit * take / (1.0 + (r / reach) ** 2 * 3.0), 0.0)
    return E / len(points)


def reference(lamp: Lamp, r: float) -> float:
    """The irradiance a surface facing the lamp gets at `r` cm: one scale for every lamp, so a sofa right under a
    lamp doesn't set the scale (and saturate) for the whole room."""
    return lamp.gain / (1.0 + (r / lamp.reach) ** 2 * 3.0)


def to_field(E: np.ndarray, top: float) -> np.ndarray:
    """0..255 greyscale: `top` maps to 255 (beyond it saturates), a gentle curve below."""
    t = np.clip(E / top, 0, 1)
    return np.round(255 * t ** 0.8).astype(np.uint8)
