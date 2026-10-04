"""Layout round for panda-room: crop each generated reference to the scene window's 740:528 aspect, give it a quick
PC-98 pass with the site's own cover filter (js/pc98.js, illustration preset) at native 448x320, and annotate the
object map.  Run: uv run python assets/panda-room/layouts.py  (needs node and the sibling site checkout)."""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
GEN = HERE / 'refs' / 'gen'
OUT = HERE / 'out' / 'layouts'
W, H = 448, 320                      # native scene size; the site shows it in the 740x528 window (~1.65x)
SCENE_W, SCENE_H = 740, 528
CROP_TOP = 30                        # 1200x896 refs -> 1200x857 (aspect 1.40), mostly from the ceiling
SITE = Path.home() / 'git' / 'vivalapanda.moe'

RANK = {'window': (1, 'Twitter'), 'phone': (2, 'Signal / Discord'), 'pc': (3, 'GitHub'), 'paper': (4, 'Substack'),
        'shelf': (5, 'Reading list'), 'butterfly': (6, 'Bluesky'), 'tv': (7, 'Letterboxd')}

# object centres in the 1200x896 references, read off the images by eye
OPTIONS = {
    'A_window_behind_bed': ('Window centred behind the bed', {
        'window': (600, 300), 'phone': (695, 600), 'pc': (95, 500), 'paper': (115, 655),
        'shelf': (990, 520), 'butterfly': (808, 440), 'tv': (1110, 640)}),
    'B_window_left_desk': ('Big window left, desk under it', {
        'window': (300, 330), 'phone': (790, 712), 'pc': (220, 560), 'paper': (105, 712),
        'shelf': (850, 420), 'butterfly': (570, 492), 'tv': (1110, 575)}),
    'C_corner_wrap': ('Corner room, city panorama on two walls', {
        'window': (500, 330), 'phone': (360, 812), 'pc': (265, 450), 'paper': (185, 556),
        'shelf': (870, 590), 'butterfly': (598, 420), 'tv': (1110, 770)}),
    'D_from_the_bed': ('From the bed, looking out', {
        'window': (600, 280), 'phone': (675, 805), 'pc': (115, 400), 'paper': (80, 540),
        'shelf': (1040, 550), 'butterfly': (795, 460), 'tv': (1090, 140)}),
}

PC98_JS = r"""
const png = require(process.argv[2]), PC98 = require(process.argv[3]);
const [src, dst, w, h] = process.argv.slice(4);
const img = png.decode(src);
const res = PC98.process(img.data, img.width, img.height, {width: +w, height: +h, preset: 'illustration'});
require('fs').writeFileSync(dst, png.encode({width: res.width, height: res.height, data: res.rgba}));
console.log(JSON.stringify({colours: res.palette.length, preset: res.preset}));
"""


def font(size):
    for f in ('/System/Library/Fonts/Menlo.ttc', '/System/Library/Fonts/Monaco.ttf'):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def annotate(img, objects, sx, sy):
    """Rank badges on each object (coordinates scaled from the reference)."""
    d = ImageDraw.Draw(img)
    f = font(13)
    for key, (x, y) in objects.items():
        rank, name = RANK[key]
        cx, cy = x * sx, (y - CROP_TOP) * sy
        label = f'{rank} {name}'
        tw = d.textlength(label, font=f)
        bx, by = cx - tw / 2 - 5, cy - 9
        d.rounded_rectangle((bx, by, bx + tw + 10, by + 18), 4, fill=(255, 0, 102), outline=(255, 255, 255))
        d.text((bx + 5, by + 2), label, font=f, fill=(255, 255, 255))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    js = OUT / '_pc98.js'
    js.write_text(PC98_JS)
    tiles = []
    for name, (title, objects) in OPTIONS.items():
        ref = Image.open(GEN / f'{name}_0.png').convert('RGBA')
        crop = ref.crop((0, CROP_TOP, ref.width, CROP_TOP + round(ref.width / 1.4)))
        src = OUT / f'{name}_crop.png'
        crop.save(src)
        dst = OUT / f'{name}_pc98.png'
        meta = subprocess.run(['node', str(js), str(HERE.parents[1] / 'filter' / 'pngio.js'),
                               str(SITE / 'js' / 'pc98.js'), str(src), str(dst), str(W), str(H)],
                              check=True, capture_output=True, text=True).stdout
        print(name, meta.strip())
        src.unlink()
        pc98 = Image.open(dst).convert('RGB')
        shown = pc98.resize((SCENE_W, SCENE_H), Image.NEAREST)      # as the scene window would show it
        shown.save(OUT / f'{name}_shown.png')
        labelled = annotate(shown.copy(), objects, SCENE_W / ref.width, SCENE_H / crop.height)
        labelled.save(OUT / f'{name}_annotated.png')
        tiles.append((name, title, ref.resize((SCENE_W, round(SCENE_W * ref.height / ref.width))), labelled))
    js.unlink()

    # contact sheet: reference | PC-98 pass with the object map, one row per option
    pad, head = 16, 30
    rows_h = [max(r.height, a.height) for _, _, r, a in tiles]
    sheet = Image.new('RGB', (pad * 3 + SCENE_W * 2, pad + sum(h + head + pad for h in rows_h) + 40), (17, 17, 34))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 10), "Panda's Room: layout options (left: generated reference; right: PC-98 pass at the "
                      "scene window's 740x528, with the object map by rank)", font=font(15), fill=(255, 170, 187))
    y = 40
    for (name, title, ref, ann), rh in zip(tiles, rows_h):
        d.text((pad, y + 6), f'{name[0]}: {title}', font=font(17), fill=(136, 153, 255))
        sheet.paste(ref, (pad, y + head))
        sheet.paste(ann, (pad * 2 + SCENE_W, y + head))
        y += rh + head + pad
    sheet.save(HERE / 'out' / 'layouts_contact_sheet.png')
    print('sheet:', HERE / 'out' / 'layouts_contact_sheet.png')


if __name__ == '__main__':
    main()
