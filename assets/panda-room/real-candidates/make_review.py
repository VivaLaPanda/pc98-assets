"""Builds review.png for the real-PC-98-base option (gitignored: contains third-party art).

Run after composite_test.py and `pc98 preview ... preview_night`:
    uv run python assets/panda-room/real-candidates/make_review.py
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent
SITE = Path("/Users/vivalapanda/git/vivalapanda.moe/img/explore/places")
BG, FG, HI = (18, 18, 28), (235, 225, 240), (255, 170, 200)
W = 1600

blocks = []

def title(text, sub=None):
    im = Image.new("RGB", (W, 46 if sub else 28), BG); d = ImageDraw.Draw(im)
    d.text((10, 6), text, fill=HI)
    if sub: d.text((10, 26), sub, fill=FG)
    blocks.append(im)

def row(images, captions, scale_to=None, gap=12):
    if scale_to:
        images = [im.resize((round(im.width * scale_to / im.height), scale_to), Image.NEAREST) for im in images]
    h = max(i.height for i in images) + 20
    im = Image.new("RGB", (W, h), BG); d = ImageDraw.Draw(im); x = 10
    for img, cap in zip(images, captions):
        im.paste(img, (x, 18)); d.text((x, 3), cap, fill=FG); x += img.width + gap
    blocks.append(im)

# 1. the recommended route, in the real site frame
title("Option: a real PC-98 room as the base (mahou_bedroom.png, already in the site's library)",
      "Night = the same 16 inks re-tinted (how PC-98 games did time of day); window = real PC-98 skyline (city_overlook.png); new objects = image-model edit, snapped to the room's palette")
ctx = Image.open(HERE / "preview_night/context.png").convert("RGB")
row([ctx.resize((W - 20, round(ctx.height * (W - 20) / ctx.width)), Image.LANCZOS)], ["in the site frame (stand-in dialog)"])

# 2. original / day composite / night, at 2x
src = Image.open(HERE / "mahou_bedroom_src.png").convert("RGB")
day = Image.open(HERE / "test_day.png").convert("RGB")
night = Image.open(HERE / "test_night.png").convert("RGB")
row([src, day, night], ["original (real PC-98)", "+ added objects (day)", "night palette + real night city"], scale_to=290)

# 3. the edited regions, 3x: original vs result
meta = json.load(open(HERE / "test_meta.json"))
crops_o, crops_d, caps = [], [], []
for name, (x0, y0, x1, y1) in meta["boxes"].items():
    pad = 4
    box = (max(0, x0 - pad), max(0, y0 - pad), min(src.width, x1 + pad), min(src.height, y1 + pad))
    crops_o.append(src.crop(box)); crops_d.append(day.crop(box)); caps.append(name)
title("Edited regions at 3x: original (top) vs with the added object (bottom)")
row([c.resize((c.width * 3, c.height * 3), Image.NEAREST) for c in crops_o], caps)
row([c.resize((c.width * 3, c.height * 3), Image.NEAREST) for c in crops_d], caps)

# 4. the other real-room candidates from the site's library, with their object fit
cands = [
    ("mahou_bedroom.png", "1 PICK: big balcony window centre (Twitter), bed + plush, desk (add PC, newspaper), bookshelf; add phone, butterfly, TV"),
    ("day_simple_bedroom.png", "2: window centre (smaller), bed, desk+lamp (add PC), 2 bookshelves, teddy on chair; add phone, TV, butterfly"),
    ("day_bedroom.png", "3: pristine 640x400 16-colour; window, TV, figure shelves, bed - but TV dominates (rank 7) and no desk for a PC"),
    ("messy_bedroom.webp", "4: otaku room - TV centre-stage, bookshelf, bed; window curtained, no desk"),
    ("day_clean_room.png", "5: window, L-desk (add PC), big shelves; no bed (phone would go on the desk)"),
]
title("Real PC-98 rooms in the site's library (all character-free; most are resampled copies, only day_bedroom.png is the native 16-colour original)",
      "VNDB's PC-98 screenshots (643 native 640x400 captures scanned) almost always include characters; MobyGames blocks scripted access")
for i in range(0, len(cands), 3):
    chunk = cands[i:i+3]
    row([Image.open(SITE / n).convert("RGB") for n, _ in chunk], [c[:62] for _, c in chunk], scale_to=250)
    im = Image.new("RGB", (W, 18 * len(chunk) + 6), BG); d = ImageDraw.Draw(im)
    for j, (n, c) in enumerate(chunk): d.text((10, 4 + 18 * j), f"{n}: {c}", fill=FG)
    blocks.append(im)

sheet = Image.new("RGB", (W, sum(b.height for b in blocks)), BG); y = 0
for b in blocks: sheet.paste(b, (0, y)); y += b.height
sheet.save(HERE / "review.png"); print(HERE / "review.png", sheet.size)
