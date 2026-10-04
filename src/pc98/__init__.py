"""pc98: a workspace for making PC-98-style art for vivalapanda.moe. Run `uv run pc98 --help`."""
import argparse
import runpy
import sys
from pathlib import Path


def _asset(name):
    from .config import ASSETS
    d = ASSETS / name
    if not d.exists():
        sys.exit(f'no asset {name!r} in {ASSETS} (pc98 new {name})')
    return d


def cmd_new(a):
    from .config import ASSETS, ROOT
    d = ASSETS / a.name
    if d.exists():
        sys.exit(f'{d} exists')
    tpl = (ROOT / 'templates' / 'draw.py').read_text().replace('NAME', a.name)
    (d / 'refs').mkdir(parents=True)
    (d / 'out').mkdir()
    (d / 'draw.py').write_text(tpl)
    (d / 'brief.md').write_text(f'# {a.name}\n\nWhat it is for, where it lives on the site, what it must sit next to.\n\n'
                                '## Candidates\n\n## Notes\n')
    print(f'made {d}: edit brief.md, then draw.py')


def cmd_palette(a):
    from . import palette as P
    from .config import SITE
    paths = []
    for p in a.images:
        q = Path(p)
        paths += [str(x) for x in (sorted(SITE.glob(p)) if not q.exists() else [q])]
    if not paths:
        sys.exit('no images matched (paths, or globs relative to the site checkout)')
    c = P.extract(paths)
    print(f'{len(paths)} images, {len(c)} colours')
    for rgb, n in c.most_common(a.top):
        tag = '' if P.snap12(rgb) == rgb else f'  (12-bit: {P.hexs(P.snap12(rgb))})'
        print(f'  {P.hexs(rgb)}  {n:7d}{tag}')
    if a.swatch:
        leg = P.legend_from_counts(c, a.top)
        P.swatch(leg, a.swatch, counts=c)
        print('wrote', a.swatch)
    if a.json:
        import json
        leg = P.legend_from_counts(c, a.top)
        Path(a.json).write_text(json.dumps({k: list(v) for k, v in leg.items()}, indent=1))
        print('wrote', a.json)


def cmd_gen(a):
    from .gen import generate
    from .sheet import image_sheet
    d = _asset(a.asset)
    outs = [d / 'refs' / 'gen' / f'{a.tag}_{i}.png' for i in range(a.n)]
    refs = [r for r in a.refs.split(',') if r]
    generate(outs, a.prompt, endpoint=a.endpoint, refs=refs, aspect=a.aspect, cost=a.cost, max_spend=a.max)
    have = sorted(str(p) for p in (d / 'refs' / 'gen').glob('*.png'))
    if have:
        print('sheet:', image_sheet(have, d / 'refs' / 'sheet.jpg', w=256, cols=6))


def cmd_ledger(a):
    from .gen import ledger
    ledger()


def cmd_trace(a):
    from .trace import trace
    from .sheet import icon_sheet
    g, info = trace(a.image, size=a.size, legend=a.palette, dither=a.dither, mode=a.mode, pad=a.pad)
    out = Path(a.out or Path(a.image).with_suffix('.trace.txt'))
    g.dump(out)
    png = out.with_suffix('.png')
    g.save(png, a.palette)
    print(info)
    print('wrote', out, png, icon_sheet([('trace', png)], out.with_suffix('.sheet.png')))


def cmd_render(a):
    d = _asset(a.asset)
    sys.argv = [str(d / 'draw.py')] + a.rest
    runpy.run_path(str(d / 'draw.py'), run_name='__main__')


def cmd_sheet(a):
    from .sheet import icon_sheet
    items = []
    for p in a.icons:
        from .config import SITE
        q = Path(p)
        if not q.exists():
            for cand in (SITE / f'img/icons/{p}_recolor.png', SITE / f'img/icons/{p}.png'):
                if cand.exists():
                    q = cand
                    break
        items.append((q.stem.replace('_recolor', ''), q))
    print('wrote', icon_sheet(items, a.out, title=a.title))


def cmd_preview(a):
    from .preview import preview
    swaps = dict(s.split('=', 1) for s in a.swap)
    if not a.icons and not swaps:
        print('(no icons or --swap given: showing the page as it is)')
    ov = dict(s.split('=', 1) for s in a.override)
    for p in preview(a.icons or None, a.out, page=a.page, dialog=a.dialog, swaps=swaps, pad=a.pad, overrides=ov):
        print('wrote', p)


def cmd_compare(a):
    from .preview import compare
    ov = dict(s.split('=', 1) for s in a.override)
    print('wrote', compare(a.slot, a.candidates, a.out, page=a.page, scale=a.scale, overrides=ov))


def cmd_pc98ify(a):
    from .scene import pc98ify
    size = tuple(int(v) for v in a.size.lower().split('x')) if a.size else None
    keep = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in a.keep.split(',')] if a.keep else None
    g, used, ok, probs = pc98ify(a.image, a.out, size=size, colors=a.colors, palette=a.palette,
                                 dither=None if a.dither == 'none' else a.dither, spread=a.spread, keep=keep, mode=a.fit)
    print(f'wrote {a.out} ({g.w}x{g.h}, {len(used)} colours), its .json legend and @2x preview')
    print('PC-98 palette: ok' if ok else f'PC-98 palette: {probs}')


def cmd_compose(a):
    from .scene import compose
    puts = []
    for p in a.put:
        path, xy = p.rsplit('@', 1)
        x, y = xy.split(',')
        puts.append((path, x, y))
    print('wrote', compose(a.base, a.out, puts))


def cmd_zoom(a):
    from .sheet import zoom_grid
    print('wrote', zoom_grid(a.image, a.out, tuple(a.box), a.z, a.beside))


def cmd_blind(a):
    from .blind import make, JUDGE_LINEUP, JUDGE_PAIRS
    kp = make(a.out, a.real, a.new, seed=a.seed, lineups=a.lineups, judges=a.judges)
    print(f'wrote trials to {a.out}/ and the key to {kp} (keep judges out of it)')
    print('judge prompts: pc98.blind.JUDGE_LINEUP / JUDGE_PAIRS (see the module docstring)')


def main() -> None:
    ap = argparse.ArgumentParser(prog='pc98', description='PC-98 art workspace for vivalapanda.moe (see README.md)')
    sub = ap.add_subparsers(required=True)

    s = sub.add_parser('new', help='scaffold assets/<name>/ (brief.md, draw.py, refs/, out/)')
    s.add_argument('name'); s.set_defaults(f=cmd_new)

    s = sub.add_parser('palette', help='colours used by site images (paths, or globs relative to the site)')
    s.add_argument('images', nargs='+'); s.add_argument('--top', type=int, default=24)
    s.add_argument('--swatch'); s.add_argument('--json'); s.set_defaults(f=cmd_palette)

    s = sub.add_parser('gen', help='generate reference images with fal (budgeted, logged to ledger.csv)')
    s.add_argument('asset'); s.add_argument('tag', help='file prefix, e.g. scroll -> refs/gen/scroll_0.png')
    s.add_argument('prompt'); s.add_argument('--refs', default='', help='comma-separated reference images')
    s.add_argument('--n', type=int, default=2); s.add_argument('--endpoint', default='fal-ai/nano-banana-pro/edit')
    s.add_argument('--aspect', default='1:1'); s.add_argument('--cost', type=float)
    s.add_argument('--max', type=float, default=2.0, help='refuse if this call would cost more ($, default 2)')
    s.set_defaults(f=cmd_gen)

    s = sub.add_parser('ledger', help='fal spend per asset'); s.set_defaults(f=cmd_ledger)

    s = sub.add_parser('trace', help='reference image -> pixel grid draft (ASCII + PNG)')
    s.add_argument('image'); s.add_argument('--size', type=int, default=48)
    s.add_argument('--palette', default='vga'); s.add_argument('--dither', choices=['checker', 'bayer2', 'bayer4'])
    s.add_argument('--mode', default='auto', choices=['auto', 'snap', 'fit']); s.add_argument('--pad', type=int, default=1)
    s.add_argument('--out'); s.set_defaults(f=cmd_trace)

    s = sub.add_parser('render', help='run assets/<name>/draw.py (extra args are passed through)')
    s.add_argument('asset'); s.add_argument('rest', nargs=argparse.REMAINDER); s.set_defaults(f=cmd_render)

    s = sub.add_parser('sheet', help='contact sheet of icons: 1x, as shown, enlarged')
    s.add_argument('out'); s.add_argument('icons', nargs='+', help='PNG paths or site icon names (computer, ...)')
    s.add_argument('--title'); s.set_defaults(f=cmd_sheet)

    s = sub.add_parser('preview', help='screenshot the real site page with candidate icons in its sidebar')
    s.add_argument('out', help='output folder')
    s.add_argument('icons', nargs='*', help='explicit layout, two per row: site icon names, PNG paths, - for empty')
    s.add_argument('--swap', action='append', default=[], metavar='SITEICON=PNG',
                   help="replace one icon in the page's own sidebar, e.g. blog=assets/x/out/y_recolor.png")
    s.add_argument('--page', default='contact.html'); s.add_argument('--dialog')
    s.add_argument('--pad', type=int, help='vertical padding of nav buttons, px (layout experiments)')
    s.add_argument('--override', action='append', default=[], metavar='SITEPATH=FILE',
                   help='serve FILE in place of any site file, e.g. img/background-frame.png=out/frame.png')
    s.set_defaults(f=cmd_preview)

    s = sub.add_parser('compare', help='candidates swapped one at a time into a sidebar slot, side by side')
    s.add_argument('out', help='output PNG'); s.add_argument('slot', help="the site icon to replace, e.g. blog")
    s.add_argument('candidates', nargs='+', help="PNG paths ('-' = the site as it is)")
    s.add_argument('--page', default='contact.html'); s.add_argument('--scale', type=int, default=2)
    s.add_argument('--override', action='append', default=[], metavar='SITEPATH=FILE')
    s.set_defaults(f=cmd_compare)

    s = sub.add_parser('pc98ify', help='scene first pass: reference -> 16 colours (12-bit), ordered dither, true size')
    s.add_argument('image'); s.add_argument('out')
    s.add_argument('--size', help='WxH, e.g. 480x340 (default: keep)'); s.add_argument('--fit', default='cover',
                                                                                   choices=['cover', 'contain', 'stretch'])
    s.add_argument('--colors', type=int, default=16)
    s.add_argument('--palette', help="fixed palette instead of picking one: site, site+, vga or a legend .json")
    s.add_argument('--keep', help='colours the picked palette must include, e.g. #000000,#ffffff')
    s.add_argument('--dither', default='bayer4', choices=['bayer4', 'bayer2', 'checker', 'none'])
    s.add_argument('--spread', type=float, help='dither strength (default: from the palette)')
    s.set_defaults(f=cmd_pc98ify)

    s = sub.add_parser('compose', help='paste sprites into a site image at exact pixels (e.g. the frame)')
    s.add_argument('base'); s.add_argument('out')
    s.add_argument('--put', action='append', default=[], metavar='PNG@X,Y'); s.set_defaults(f=cmd_compose)

    s = sub.add_parser('zoom', help='gridded zoom of a region in native coordinates, for tracing (--beside: a 2nd image)')
    s.add_argument('image'); s.add_argument('out'); s.add_argument('box', nargs=4, type=int, metavar=('X0', 'Y0', 'X1', 'Y1'))
    s.add_argument('-z', type=int, default=4); s.add_argument('--beside'); s.set_defaults(f=cmd_zoom)

    s = sub.add_parser('blind', help='blind-test images (lineups, pairs) of new art against real art, plus a key')
    s.add_argument('out'); s.add_argument('--real', nargs='+', required=True); s.add_argument('--new', nargs='+', required=True)
    s.add_argument('--seed', type=int, default=0); s.add_argument('--lineups', type=int, default=3)
    s.add_argument('--judges', type=int, default=3); s.set_defaults(f=cmd_blind)

    a = ap.parse_args()
    a.f(a)
