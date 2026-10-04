import numpy as np
import pytest

from easel.canvas import Canvas, T, nib, bresenham, ellipse_points
from easel import patterns as P


def test_palette_is_the_4096_grid():
    assert nib('#2a4') == (2, 10, 4)
    assert nib('#2233aa') == (2, 3, 10)
    with pytest.raises(ValueError):
        nib('#2234aa')          # 0x34 is off the grid


def test_register_change_recolours_everything():
    cv = Canvas(8, 8)
    cv.pal_set(1, '#f00')
    cv.rect(0, 0, 3, 3, 1)
    cv.pal_set(1, '#00f')
    assert tuple(cv.rgb()[0, 0]) == (0, 0, 255)


def test_tiles_anchor_to_the_screen():
    a = Canvas(16, 16, ox=0, oy=0)
    b = Canvas(16, 16, ox=1, oy=0)      # the same tile, one pixel along the screen
    for cv in (a, b):
        cv.fill(cv.m_all(), T('1/2', 0, 1))
    assert (a.idx[:, 1:] == b.idx[:, :-1]).all()


def test_fences():
    cv = Canvas(8, 8)
    cv.rect(0, 0, 7, 3, 2)
    with cv.only_over(2):
        cv.rect(0, 0, 7, 7, 5)          # paints only the top half (index 2)
    assert (cv.idx[:4] == 5).all() and (cv.idx[4:] == 0).all()
    cv.protect(5)
    cv.rect(0, 0, 7, 7, 7)
    assert (cv.idx[:4] == 5).all() and (cv.idx[4:] == 7).all()


def test_over_tile_keeps_ground():
    cv = Canvas(8, 8)
    cv.rect(0, 0, 7, 7, 3)
    cv.fill(cv.m_all(), T('1/4', None, 9))
    assert set(np.unique(cv.idx)) == {3, 9}
    assert (cv.idx == 9).mean() == pytest.approx(0.25)


def test_geometry_is_hard_pixels():
    assert bresenham(0, 0, 3, 1) == [(0, 0), (1, 0), (2, 1), (3, 1)]
    pts = set(ellipse_points(10, 10, 4, 3))
    assert all((20 - x, y) in pts and (x, 20 - y) in pts for x, y in pts)   # symmetric
    cv = Canvas(10, 10)
    cv.poly([(1, 1), (8, 1), (8, 8), (1, 8)], 4)
    assert (cv.idx[1:9, 1:9] == 4).all() and cv.idx[0].sum() == 0


def test_grad_bands_use_period_tiles():
    cv = Canvas(40, 8)
    cv.grad(cv.m_all(), 0, 1, cv.lin((0, 0), (40, 0)))
    bands = [(cv.idx[:, x:x + 8] == 1).mean() for x in (0, 8, 16, 24, 32)]
    assert bands == [0.0, 0.25, 0.5, 0.75, 1.0]


def test_start_from_crops_the_base_and_keeps_it():
    idx = np.arange(64, dtype=np.uint8).reshape(8, 8) % 16
    cv = Canvas(4, 4, ox=2, oy=3)
    cv.start_from(idx, ['#000'] * 15 + ['#fff'])
    assert (cv.idx == idx[3:7, 2:6]).all() and (cv.base == cv.idx).all()
    assert cv.hex(15) == '#fff'


def test_relight_steps_each_ink_up_its_ramp_in_tiles():
    cv = Canvas(8, 8)
    cv.rect(0, 0, 7, 3, 1); cv.rect(0, 4, 7, 7, 5)          # two surfaces, two ramps
    cv.dot(3, 3, 0)                                          # a line pixel: not in the ramp, stays
    cv.relight(cv.m_all(), np.full((8, 8), 1.5), {1: 2, 2: 3, 5: 6, 6: 7})
    top, bot = cv.idx[:4], cv.idx[4:]
    assert set(np.unique(top)) == {0, 2, 3} and set(np.unique(bot)) == {6, 7}
    assert (bot == 7).mean() == pytest.approx(0.5)           # one full step, then a 1/2 tile of the next
    assert cv.idx[3, 3] == 0


def test_dist_from_rings_a_shape():
    cv = Canvas(9, 9)
    d = cv.dist_from(cv.m_rect(4, 4, 4, 4))
    assert d[4, 4] == 0 and d[3, 3] == 1 and d[4, 6] == 2 and d[0, 0] == 4
