"""Feasibility test: real PC-98 room (mahou_bedroom) + image-model additions + palette night.

Run: uv run python assets/panda-room/real-candidates/composite_test.py
Inputs live in this (gitignored) folder; outputs land next to it.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
SITE = Path("/Users/vivalapanda/git/vivalapanda.moe/img/explore/places")

src = Image.open(HERE / "mahou_bedroom_src.png").convert("RGB")
W, H = src.size
edit = Image.open(HERE / "edit1_aligned.png").convert("RGB")

# 1. the original's own 16-colour palette (the tumblr copy is resampled, so re-derive it):
#    k-means from a median-cut start, so small saturated areas (blue floor, pink cushion) keep their own ink
pal_img = src.quantize(colors=16, method=Image.MEDIANCUT, dither=Image.NONE)
palette = np.array(pal_img.getpalette()[:48], dtype=float).reshape(16, 3)
px = np.asarray(src).reshape(-1, 3).astype(float)
for _ in range(12):
    lab = ((px[:, None] - palette[None]) ** 2).sum(-1).argmin(1)
    for k in range(16):
        if (lab == k).any():
            palette[k] = px[lab == k].mean(0)
palette = np.round(palette / 17) * 17           # onto the PC-98's 4096-colour grid

def snap(rgb):
    """Nearest palette index per pixel (no dithering: PC-98 art places dither by hand)."""
    d = ((rgb[..., None, :].astype(float) - palette[None, None]) ** 2).sum(-1)
    return d.argmin(-1)

orig_idx = snap(np.asarray(src))

# 2. transplant only the added objects, and only pixels that really changed inside each box
boxes = {"plush": (24, 124, 70, 183), "phone": (90, 195, 123, 215), "butterfly": (215, 99, 235, 118),
         "pc_newspaper": (355, 95, 446, 158), "tv": (445, 207, 480, 258)}
e = np.asarray(edit).astype(float)
o = np.asarray(src).astype(float)
edit_idx = snap(e)
idx = orig_idx.copy()
changed = np.zeros((H, W), bool)
for name, (x0, y0, x1, y1) in boxes.items():
    diff = np.abs(e[y0:y1, x0:x1] - o[y0:y1, x0:x1]).sum(-1) > 90
    # grow by one pixel so the new objects keep their dark outlines
    grown = diff.copy()
    grown[1:] |= diff[:-1]; grown[:-1] |= diff[1:]; grown[:, 1:] |= diff[:, :-1]; grown[:, :-1] |= diff[:, 1:]
    region = idx[y0:y1, x0:x1]
    region[grown] = edit_idx[y0:y1, x0:x1][grown]
    changed[y0:y1, x0:x1] |= grown

def to_img(index_map, pal):
    return Image.fromarray(pal[index_map].clip(0, 255).astype(np.uint8))

day = to_img(idx, palette)
day.save(HERE / "test_day.png")

# 3. night by palette: the same 16 inks, darkened and pushed toward navy/violet while keeping their
#    saturation (how PC-98 games did time of day), snapped back onto the 4096-colour grid
# multiply toward a cool navy instead of rotating hues: keeps every ink's relationship (yellow stays a
# dim gold, not red), the way a hand-picked PC-98 night palette reads
night = palette * np.array([0.42, 0.44, 0.62]) + np.array([6, 8, 34])
night = np.round(night / 17) * 17
night_img = night[idx]

# emissive things keep (and gain) light: monitor screen, phone screen, lamp; picked from the day colours
day_rgb = palette[idx]
bright = (day_rgb @ [0.299, 0.587, 0.114]) > 170
emissive = np.zeros((H, W), bool)
for name in ("pc_newspaper", "phone"):
    x0, y0, x1, y1 = boxes[name]
    c = day_rgb[y0:y1, x0:x1]
    screen = (c[..., 2] > c[..., 0] + 15) & (c[..., 1] > c[..., 0])          # cyan-ish screen glow only
    emissive[y0:y1, x0:x1] = bright[y0:y1, x0:x1] & changed[y0:y1, x0:x1] & screen
lamp = (410, 72, 426, 86)                         # just the shade's opening, not the calendar beside it
emissive[lamp[1]:lamp[3], lamp[0]:lamp[2]] |= bright[lamp[1]:lamp[3], lamp[0]:lamp[2]]
night_img[emissive] = day_rgb[emissive]

# 4. the view through the balcony glass becomes a real PC-98 night city (city_overlook.png), above the rail:
#    fill each pane whole, leaving the frame and the centre mullion from the room
city = Image.open(SITE / "city_overlook.png").convert("RGB")
panes = [(191, 32, 235, 118), (240, 32, 283, 118)]
for i, (x0, y0, x1, y1) in enumerate(panes):
    cx = 30 + i * 60
    crop = np.asarray(city.crop((cx, 18, cx + (x1 - x0), 18 + (y1 - y0)))).astype(float)
    night_img[y0:y1, x0:x1] = crop

Image.fromarray(night_img.clip(0, 255).astype(np.uint8)).save(HERE / "test_night.png")
json.dump({"boxes": boxes, "palette": palette.astype(int).tolist(), "changed_px": int(changed.sum())},
          open(HERE / "test_meta.json", "w"), indent=1)
print("changed pixels:", int(changed.sum()), "of", W * H)
