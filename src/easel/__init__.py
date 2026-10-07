"""The PC-98 easel: paint in a faithful 16-colour medium, one passage at a time, and step back.

A piece lives in easel/pieces/<name>/:
  piece.toml        canvas size and screen offset, references to compare against, where it goes on the site
  passages/NN_*.py  the painting: passages run in order in one shared namespace. They are the replayable log;
                    re-running them all from a blank canvas paints the same picture, always.
  journal.md        the painter's working notes (`easel note`)
  out/              renders: <name>.png (1x), @2x, @3x, steps.png, look.png (with reference crops: not committed);
                    a piece started from a real picture (cv.start_from) also gets <name>-layer.png, only what it changed

Commands:
  easel new <piece> --size 176x128 [--at 0,160]   start a piece (at = where it sits on the full screen)
  easel paint <piece> [--upto N]                   replay every passage, write the renders and the look sheet
  easel note <piece> "text"                        add a dated entry to the journal
  easel checkpoint <piece> [label]                 keep a copy of the current render under out/checkpoints/
  easel preview <piece>                            composite into the real site page and screenshot it
  easel metrics <img...>                           measure images against the pro PC-98 ranges
  easel vp-check <piece> [--tol 1] [--label x]     do the painted edges meet the vanishing points? (overlay + table)
Read easel/notes/easel_guide.md before painting.
"""

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tomllib
import traceback
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageDraw

from pc98.config import ROOT, SITE, font
from . import base as BASE
from . import metrics as MX
from . import patterns as P
from . import vpcheck as VPC
from .canvas import Canvas, T, Tile, Clip, bresenham, ellipse_points

PIECES = ROOT / 'easel' / 'pieces'

TEMPLATE_TOML = '''# {name}
[canvas]
w = {w}
h = {h}
at = [{ax}, {ay}]          # where this piece sits on the full screen (tiles anchor to screen pixels)
seed = 1

[look]
zoom = 3                   # zoom for the main view
detail_zoom = 4            # zoom for region and reference crops
# regions = {{ monitor = [10, 10, 80, 60] }}

# Reference crops shown beside yours at the same zoom (paths relative to the site's img/).
# [[refs]]
# path = "explore/places/night_musician_bedroom.png"
# box = [120, 60, 300, 180]
# label = "musician desk"

# Where the piece goes on the site, for `easel preview`.
# [site]
# page = "room.html"
# path = "img/room/room@4x.png"     # the site file to override
# base = "assets/panda-room/out/final/room.png"   # 1x image the piece is pasted into
# scale = 4
'''

TEMPLATE_PASSAGE = '''# 00 palette: set the 16 registers first, by role. Change them any time later: the whole picture follows.
# Names are yours; use them in every later passage.
K = cv.pal_set(0, '#000', 'black')
'''


def piece_dir(name):
    d = PIECES / name
    if not d.exists():
        raise SystemExit(f'no piece {name!r} in {PIECES}')
    return d


def load(name):
    d = piece_dir(name)
    cfg = tomllib.loads((d / 'piece.toml').read_text())
    return d, cfg


def passages(d):
    return sorted((d / 'passages').glob('*.py'))


def run(name, upto=None, pre=None):
    """Replay the passages onto a blank canvas. Returns (canvas, [(passage name, rgb after it)]).
    pre: names to seed the passages' namespace with (a piece built on this one switching something off)."""
    d, cfg = load(name)
    c = cfg['canvas']
    ax, ay = c.get('at', [0, 0])
    cv = Canvas(c['w'], c['h'], ax, ay)
    ns = {'cv': cv, 'ud': cv.ud, 'P': P, 'T': T, 'Tile': Tile, 'Clip': Clip, 'np': np,
          'rng': np.random.default_rng(c.get('seed', 1)), 'bresenham': bresenham, 'ellipse_points': ellipse_points,
          'quantize': BASE.quantize, 'resolve': BASE.resolve, 'Image': Image}
    ns.update(pre or {})
    steps = []
    for p in passages(d):
        num = p.stem.split('_', 1)[0]
        if upto is not None and num.isdigit() and int(num) > upto:
            break
        try:
            exec(compile(p.read_text(), str(p), 'exec'), ns)
        except Exception:
            traceback.print_exc()
            raise SystemExit(f'passage {p.name} failed; nothing written')
        steps.append((p.stem, cv.rgb().copy()))
    cv.ns = ns              # the passages' names (masks, geometry), for exporters and pieces built on this one
    return cv, steps


# ------------------------------------------------------------------------------------- sheets

BG = (24, 22, 34)
FG = (230, 225, 240)
DIM = (150, 145, 170)


def _zoom(img, z):
    return img.resize((img.width * z, img.height * z), Image.NEAREST)


def _label(img, text, f=None, color=FG):
    f = f or font(16)
    pad = 22
    out = Image.new('RGB', (max(img.width, int(f.getlength(text)) + 4), img.height + pad), BG)
    ImageDraw.Draw(out).text((2, 2), text, fill=color, font=f)
    out.paste(img, (0, pad))
    return out


def _row(imgs, gap=16):
    if not imgs:
        return Image.new('RGB', (1, 1), BG)
    w = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    h = max(i.height for i in imgs)
    out = Image.new('RGB', (w, h), BG)
    x = 0
    for i in imgs:
        out.paste(i, (x, 0)); x += i.width + gap
    return out


def _col(imgs, gap=20):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new('RGB', (w, h), BG)
    y = 0
    for i in imgs:
        out.paste(i, (0, y)); y += i.height + gap
    return out


def _under_view(cv, z, box=None):
    x0, y0, x1, y1 = box or (0, 0, cv.w, cv.h)
    base = _zoom(Image.fromarray(cv.rgb()).crop((x0, y0, x1, y1)), z).convert('RGBA')
    ud = _zoom(Image.fromarray(cv.ud.rgba, 'RGBA').crop((x0, y0, x1, y1)), z)
    out = Image.alpha_composite(base, ud).convert('RGB')
    d = ImageDraw.Draw(out)
    f = font(12)
    for x, y, text, col in cv.ud.labels:
        if x0 <= x < x1 and y0 <= y < y1:
            d.text(((x - x0) * z + 2, (y - y0) * z + 2), text, fill=tuple(int(v) for v in col), font=f)
    return out


def _swatch(cv, rgb):
    f = font(14)
    a = rgb.reshape(-1, 3)
    shares = {}
    for i in range(16):
        col = (cv.pal[i].astype(int) * 17)
        shares[i] = float(np.all(a == col, axis=1).mean())
    names = {v: k for k, v in cv.names.items()}
    tiles = []
    for i in range(16):
        t = Image.new('RGB', (118, 46), BG)
        d = ImageDraw.Draw(t)
        d.rectangle([0, 0, 30, 30], fill=tuple(int(v) * 17 for v in cv.pal[i]), outline=(90, 90, 110))
        d.text((36, 0), f'{i:>2} {cv.hex(i)}', fill=FG, font=f)
        d.text((36, 16), f'{shares[i] * 100:4.1f}%', fill=DIM, font=f)
        d.text((0, 32), names.get(i, '')[:16], fill=DIM, font=font(12))
        tiles.append(t)
    return _col([_row(tiles[:8], 6), _row(tiles[8:], 6)], 6)


def _text_block(lines, w=520):
    f = font(14)
    h = 18 * len(lines) + 8
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        col = (255, 150, 150) if ('LOW' in ln or 'HIGH' in ln or 'FAIL' in ln) else FG
        d.text((4, 4 + 18 * i), ln, fill=col, font=f)
    return img


def _ref_crops(cfg, z):
    out = []
    for r in cfg.get('refs', []):
        try:
            f = BASE.resolve(r['path'])
        except FileNotFoundError:
            continue
        im = Image.open(f).convert('RGB')
        if 'box' in r:
            im = im.crop(tuple(r['box']))
        out.append((r.get('label', Path(r['path']).stem), im))
    return out


def look(name, cv, steps, cfg, d):
    lk = cfg.get('look', {})
    z, dz = lk.get('zoom', 3), lk.get('detail_zoom', 4)
    rgb = cv.rgb()
    pic = Image.fromarray(rgb)
    rows = []
    top = [_label(_zoom(pic, z), f'{name}  {cv.w}x{cv.h}  at {z}x  ({len(steps)} passages)')]
    if cv.ud.rgba[..., 3].any() or cv.ud.labels:
        fb = lk.get('focus')
        top.append(_label(_under_view(cv, dz if fb else z, fb), f'with underdrawing{" (focus " + str(fb) + ")" if fb else ""}'))
    rows.append(_row(top))
    if cv.base is not None:
        # painting into a real picture: the same box before and after, at 1x and at the detail zoom
        bx = lk.get('focus') or [0, 0, cv.w, cv.h]
        before = Image.fromarray(cv.rgb(cv.base)).crop(tuple(bx))
        after = pic.crop(tuple(bx))
        rows.append(_row([_label(before, 'before 1x', color=DIM), _label(after, 'after 1x'),
                          _label(_zoom(before, dz), f'before {dz}x', color=DIM), _label(_zoom(after, dz), f'after {dz}x')]))
    refs = _ref_crops(cfg, 1)
    # at display size: what a visitor actually sees
    small = [_label(pic, 'ours 1x'), _label(_zoom(pic, 2), 'ours 2x')]
    for lab, im in refs[:3]:
        small.append(_label(_zoom(im, 2), f'{lab} 2x', color=DIM))
    rows.append(_row(small))
    # stepping back (stillwet's look modes): value only, and squinting (blurred), at 1x. Which region leads?
    gray = ImageOps.grayscale(pic).convert('RGB')
    squint = pic.resize((max(1, cv.w // 4), max(1, cv.h // 4)), Image.BILINEAR).resize((cv.w, cv.h), Image.BILINEAR)
    rows.append(_row([_label(gray, 'value 1x', color=DIM), _label(squint, 'squint 1x', color=DIM),
                      _label(ImageOps.grayscale(squint).convert('RGB'), 'value + squint 1x', color=DIM)]))
    # details at the same zoom as the references
    det = []
    for rn, box in (lk.get('regions') or {}).items():
        det.append(_label(_zoom(pic.crop(tuple(box)), dz), f'ours: {rn} {dz}x'))
    for lab, im in refs:
        im2 = im if im.width * dz <= 900 else im.crop((0, 0, 900 // dz, min(im.height, 600 // dz)))
        det.append(_label(_zoom(im2, dz), f'pro: {lab} {dz}x', color=DIM))
    if det:
        rows.append(_row(det))
    mb = lk.get('measure')
    m = MX.measure(rgb[mb[1]:mb[3], mb[0]:mb[2]] if mb else rgb)
    rng = MX.reference_ranges()
    lines = [f'measures vs pro PC-98 interiors{" (box " + str(mb) + ")" if mb else ""}:'] + MX.report(m, rng)
    lint = ROOT / 'filter' / 'pc98lint.py'
    if lint.exists():
        r = subprocess.run([sys.executable, str(lint), str(d / 'out' / f'{name}.png')], capture_output=True, text=True)
        lines += [''] + [ln.strip() for ln in r.stdout.splitlines()[1:4]]
    rows.append(_row([_swatch(cv, rgb), _text_block(lines)]))
    sheet = _col(rows)
    sheet.save(d / 'out' / 'look.png')
    return m, rng


def steps_sheet(steps, d, z=2):
    tiles = [_label(_zoom(Image.fromarray(rgb), z), stem) for stem, rgb in steps]
    per = 3
    rows = [_row(tiles[i:i + per]) for i in range(0, len(tiles), per)]
    _col(rows).save(d / 'out' / 'steps.png')


def cycle_gif(cv, d, z=3):
    if not cv.cycles:
        return None
    frames = []
    n = max(len(ix) for ix, _, _ in cv.cycles)
    base_pal = cv.pal.copy()
    for k in range(n):
        pal = base_pal.copy()
        for ix, fps, _ in cv.cycles:
            pal[ix] = np.roll(base_pal[ix], k, axis=0)
        frames.append(_zoom(Image.fromarray((pal[cv.idx].astype(np.uint16) * 17).astype(np.uint8)), z))
    fps = cv.cycles[0][1]
    out = d / 'out' / 'cycle.gif'
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)
    return out


# ----------------------------------------------------------------------------------- commands

def cmd_new(a):
    d = PIECES / a.piece
    if d.exists():
        raise SystemExit(f'{d} exists')
    w, h = (int(v) for v in a.size.lower().split('x'))
    ax, ay = (int(v) for v in a.at.split(','))
    (d / 'passages').mkdir(parents=True)
    (d / 'out').mkdir()
    (d / 'piece.toml').write_text(TEMPLATE_TOML.format(name=a.piece, w=w, h=h, ax=ax, ay=ay))
    (d / 'passages' / '00_palette.py').write_text(TEMPLATE_PASSAGE)
    (d / 'journal.md').write_text(f'# {a.piece}: journal\n\n')
    print(f'new piece at {d}. Write passages/NN_*.py, then: easel paint {a.piece}')


def cmd_paint(a):
    d, cfg = load(a.piece)
    cv, steps = run(a.piece, a.upto)
    out = d / 'out'
    out.mkdir(exist_ok=True)
    pic = Image.fromarray(cv.rgb())
    pic.save(out / f'{a.piece}.png')
    if cv.base is not None:
        # the layer: only what this piece changed, at its place on the base picture (palette changes are global:
        # piece.json carries the registers)
        lay = np.zeros((cv.h, cv.w, 4), np.uint8)
        ch = cv.idx != cv.base
        lay[ch, :3] = cv.rgb()[ch]
        lay[ch, 3] = 255
        Image.fromarray(lay, 'RGBA').save(out / f'{a.piece}-layer.png')
    _zoom(pic, 2).save(out / f'{a.piece}@2x.png')
    _zoom(pic, 3).save(out / f'{a.piece}@3x.png')
    np.save(out / 'index.npy', cv.idx)
    (out / 'piece.json').write_text(json.dumps({
        'size': [cv.w, cv.h], 'at': [cv.ox, cv.oy],
        'palette': [cv.hex(i) for i in range(16)], 'names': cv.names,
        'cycles': [{'indices': ix, 'fps': fps, 'name': n} for ix, fps, n in cv.cycles]}, indent=1))
    steps_sheet(steps, d)
    cycle_gif(cv, d)
    m, rng = look(a.piece, cv, steps, cfg, d)
    print(f'{len(steps)} passages -> {out}/{a.piece}.png, look.png, steps.png')
    for ln in MX.report(m, rng):
        print('  ' + ln)


def cmd_note(a):
    d = piece_dir(a.piece)
    stamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    n = len(passages(d))
    with open(d / 'journal.md', 'a') as f:
        f.write(f'- **{stamp}** (after {n} passages): {a.text}\n')
    print('noted')


def cmd_checkpoint(a):
    d = piece_dir(a.piece)
    src = d / 'out' / f'{a.piece}.png'
    if not src.exists():
        raise SystemExit('paint it first')
    cp = d / 'out' / 'checkpoints'
    cp.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime('%m%d-%H%M')
    dst = cp / f'{stamp}_{a.label or "cp"}.png'
    shutil.copy(src, dst)
    print(dst)


def cmd_preview(a):
    from pc98 import preview as PV
    d, cfg = load(a.piece)
    site = cfg.get('site')
    if not site:
        raise SystemExit('add a [site] table to piece.toml')
    pic = Image.open(d / 'out' / f'{a.piece}.png').convert('RGB')
    base = Image.open(ROOT / site['base']).convert('RGB') if site.get('base') else pic
    ax, ay = cfg['canvas'].get('at', [0, 0])
    comp = base.copy()
    comp.paste(pic, (ax, ay))
    s = site.get('scale', 1)
    tmp = ROOT / '.preview'
    tmp.mkdir(exist_ok=True)
    comp_path = tmp / f'{a.piece}_site.png'
    _zoom(comp, s).save(comp_path)
    overrides = {site['path']: str(comp_path)}
    for p in site.get('blank', []):           # site overlays to hide (e.g. the old twinkle strip)
        im = Image.open(SITE / p)
        blank = tmp / f'{a.piece}_blank_{Path(p).name}'
        Image.new('RGBA', im.size, (0, 0, 0, 0)).save(blank)
        overrides[p] = str(blank)
    paths = PV.preview(None, d / 'out' / 'preview', page=site.get('page', 'room.html'), overrides=overrides,
                       hide=site.get('hide'))
    print('\n'.join(paths))


def cmd_metrics(a):
    rng = MX.reference_ranges()
    for p in a.images:
        print(p)
        for ln in MX.report(MX.measure(np.asarray(Image.open(p).convert('RGB'))), rng):
            print('  ' + ln)


def cmd_vpcheck(a):
    """Measure every declared edge (cv.persp) on the finished picture; write the overlay sheet and the table."""
    d, cfg = load(a.piece)
    cv, _ = run(a.piece)
    if not cv.persp.vps:
        raise SystemExit('no vanishing points declared: cv.persp.vp("room", VP) in a passage, then edges')
    res = VPC.measure(cv, a.tol)
    lines = VPC.report(res, a.tol)
    out = d / 'out'
    out.mkdir(exist_ok=True)
    suffix = f'-{a.label}' if a.label else ''
    title = f'{a.piece} vp-check{" " + a.label if a.label else ""}: tolerance {a.tol:.1f}px'
    sheet = [VPC.overlay(cv, res, z=a.zoom, title=title, font=font(13))]
    if a.box:
        box = tuple(int(v) for v in a.box.split(','))
        sheet.append(VPC.overlay(cv, res, z=a.box_zoom, box=box, title=f'detail {box}', font=font(13)))
    sheet.append(_text_block(lines, w=max(i.width for i in sheet)))
    _col(sheet).save(out / f'vp-check{suffix}.png')
    (out / f'vp-check{suffix}.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print(f'-> {out}/vp-check{suffix}.png')
    if any(r['status'] == 'FAIL' for r in res):
        sys.exit(1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='easel', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('new'); s.add_argument('piece'); s.add_argument('--size', default='448x320'); s.add_argument('--at', default='0,0'); s.set_defaults(f=cmd_new)
    s = sub.add_parser('paint'); s.add_argument('piece'); s.add_argument('--upto', type=int); s.set_defaults(f=cmd_paint)
    s = sub.add_parser('note'); s.add_argument('piece'); s.add_argument('text'); s.set_defaults(f=cmd_note)
    s = sub.add_parser('checkpoint'); s.add_argument('piece'); s.add_argument('label', nargs='?'); s.set_defaults(f=cmd_checkpoint)
    s = sub.add_parser('preview'); s.add_argument('piece'); s.set_defaults(f=cmd_preview)
    s = sub.add_parser('metrics'); s.add_argument('images', nargs='+'); s.set_defaults(f=cmd_metrics)
    s = sub.add_parser('vp-check'); s.add_argument('piece'); s.add_argument('--tol', type=float, default=1.0)
    s.add_argument('--label'); s.add_argument('--zoom', type=int, default=3)
    s.add_argument('--box', help='x0,y0,x1,y1: also a zoomed detail of this box'); s.add_argument('--box-zoom', type=int, default=6)
    s.set_defaults(f=cmd_vpcheck)
    a = ap.parse_args(argv)
    a.f(a)
