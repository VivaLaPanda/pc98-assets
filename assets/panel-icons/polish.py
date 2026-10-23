"""panel-icons, steps 2 and 3 (the home-icon flow): an image model redraws each render's draft beside the site's real
icons, then the redraw comes back to a 48x48 icon in the frame palette. Run:
    uv run python assets/panel-icons/polish.py grid <draft>                     # the 3x2 sheet the model edits
    uv run python assets/panel-icons/polish.py fal <draft> <tag> --n 2 --max 0.30   # nano-banana-pro edit, via pc98.gen
    uv run python assets/panel-icons/polish.py snap <fal.png> <name> --bits     # its draft cell -> out/redraw/<name>
(needs PC98_ANIMATIONS=~/code/animations on rodney for the fal step.)

The sheet is five real recoloured icons (the kotatsu, computer, globe, cd and recipe book) and the draft
(out/render/<draft>.png), each at 8x on the sidebar's mint, so the model sees the set's pixel grid, outlines, checker
shading and palette and copies them; the lit render is the second reference. Sheets and redraws contain the Windows
icons, so they stay in .scratch/panel-icons/ (the repo is public); spend goes to ledger.csv through pc98.gen. The
snap reads each 8x8 cell of the draft's slot (the median of its middle), maps it to the nearest frame colour, clears
the mint, and redraws the set's outline (plum on the lit top/left, black on the bottom/right) round the main body; with
--bits, detached pieces (zzz, rays) stay, in the model's colours. draw.py finishes the chosen snaps by hand.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from pc98 import palette as P
from pc98.config import ROOT, SITE
from pc98.gen import generate
from pc98.pixel import Grid

HERE = Path(__file__).parent
SCR = ROOT / '.scratch' / 'panel-icons'
REDRAW = HERE / 'out' / 'redraw'
REFS = ['home', 'computer', 'globe_map', 'cd_audio', 'recipes']
CELL, S = 384, 8
MINT = (0x00, 0xEE, 0xBB)
LEG = P.get('site+')

SHEET = ('The first image is a sheet of 48x48-pixel desktop icons shown at 8x (every icon pixel is an 8x8 block): '
         'Windows 98 icons recoloured into one PC-98 palette. ')
GRID = ('the same 8x8-block pixel grid (no smaller detail, no anti-aliasing, no gradients, no blur), only these '
        'colours: {colours}; ')
LINE = ('a 1-pixel outline, black on the bottom and right, plum on the top and left, and plum lines where one part '
        'overlaps another. Not clip art, not cartoonish. Keep it the same size and place on the flat mint background '
        'and leave the other five icons exactly as they are. Output only the edited first image.')
PROMPTS = {
    'futon': SHEET + (
        'Its bottom-right icon is a rough quantized draft of a new icon, a Japanese futon laid out on the floor for '
        'the night; the second image is the 3D render it came from (a thin white mattress, a plump white pillow at '
        'the head, a thick puffy quilt with a pink plaid over a sleeper\'s body, draping to the floor in soft folds). '
        'Redraw ONLY the bottom-right icon of the first image as a finished icon of exactly that futon, as the same '
        'artist who drew the kotatsu, the computer and the globe would: '
        + GRID.format(colours='periwinkle #8899ff, plum #664477, mauve grey #bbaabb, pink #ffaabb, white, black') +
        'the quilt periwinkle with the kotatsu\'s pink plaid following its folds, thick and soft with rounded puffy '
        'edges and a gentle rise over the sleeper, lit on the left with white highlights and falling into plum '
        'shadow on the right through 50% checkerboard dithering; the quilt\'s top edge turned down to show a white '
        'band; a big soft white pillow with mauve shading, clearly separate from the quilt; three small "Z" letters '
        'rising from the pillow toward the top right, in periwinkle with a plum edge. It must read at a glance as a '
        'bed made for sleeping, not a cake, a box or a rug. ' + LINE),
    'hills': SHEET + (
        'Its bottom-right icon is a rough quantized draft of a new icon, the sun rising over hills; the second image '
        'is the 3D render it came from (a big yellow sun half hidden behind two rounded periwinkle hills, its rays '
        'fanned above). Redraw ONLY the bottom-right icon of the first image as a finished icon of exactly that '
        'sunrise, as the same artist who drew the globe, the kotatsu and the computer would: '
        + GRID.format(colours='yellow #ffee55, peach #ffaa77, hot pink #ff0066, rust #994422, periwinkle #8899ff, '
                              'plum #664477, mauve grey #bbaabb, white, black') +
        'the sun a big yellow disc with a white highlight at the top left and peach shading at the lower right '
        'through a 50% checkerboard, its rays short chunky wedges, yellow and peach in turn; the hills soft and '
        'rounded, periwinkle, lit on their left slopes with white highlights and falling into plum shadow on the '
        'right through 50% checkerboard dithering, the near hill in front of the far one. It must read at a glance '
        'as the sun coming up over a landscape, not a sun over a box. ' + LINE),
    'fuji': SHEET + (
        'Its bottom-right icon is a rough quantized draft of a new icon, the sun rising beside Mount Fuji; the second '
        'image is the 3D render it came from (a snow-capped cone with a flat top and two low foothills, a yellow sun '
        'half hidden behind its right shoulder, rays fanned above). Redraw ONLY the bottom-right icon of the first '
        'image as a finished icon of exactly that scene, as the same artist who drew the globe, the kotatsu and the '
        'computer would: '
        + GRID.format(colours='yellow #ffee55, peach #ffaa77, hot pink #ff0066, rust #994422, periwinkle #8899ff, '
                              'plum #664477, mauve grey #bbaabb, white, black') +
        'the sun a yellow disc with a white highlight at the top left and peach shading at the lower right through a '
        '50% checkerboard, its rays short chunky wedges, yellow and peach in turn; the mountain periwinkle with a '
        'jagged white snow cap, lit on its left slope and falling into plum shadow on the right through 50% '
        'checkerboard dithering. It must read at a glance as a sunrise, not a sun over a box. ' + LINE),
    'fuji2': SHEET + (
        'Its bottom-right icon is a rough quantized draft of a new icon, the sun rising behind the summit of Mount '
        'Fuji; the second image is the 3D render it came from (a snow-capped cone with a flat top, a big yellow sun '
        'half risen behind it, its rays fanned above). Redraw ONLY the bottom-right icon of the first image as a '
        'finished icon of exactly that scene, as the same artist who drew the globe, the kotatsu and the computer '
        'would: '
        + GRID.format(colours='yellow #ffee55, peach #ffaa77, rust #994422, periwinkle #8899ff, plum #664477, '
                              'mauve grey #bbaabb, white, black') +
        'the sun a big round yellow disc, clearly wider than the summit, with a white highlight at the top left and '
        'peach shading at the lower right through a 50% checkerboard, its rays short chunky wedges standing clear of '
        'the disc, yellow and peach in turn; the mountain periwinkle with gently concave slopes, a flat top and a '
        'white snow cap whose lower edge runs down the slopes in jagged streaks, lit on its left slope and falling '
        'into plum shadow on the right through 50% checkerboard dithering, a plum line where the summit crosses the '
        'sun. It must read at a glance as a calm sunrise, not an eruption and not a sun over a box. ' + LINE),
}
MUG = SHEET + (
    'Its bottom-right icon is a rough quantized draft of a new icon, a cosy mug of morning coffee, steaming; the '
    'second image is the 3D render it came from (a chunky periwinkle mug seen a little from above, a rounded white '
    'lip and white inside, dark coffee, a loop handle on the right, {print} on its front, three wisps of steam '
    'rising). Redraw ONLY the bottom-right icon of the first image as a finished icon of exactly that mug, as the '
    'same artist who drew the kotatsu, the computer and the cd would: '
    + GRID.format(colours='periwinkle #8899ff, plum #664477, mauve grey #bbaabb, white, black, rust #994422, tan '
                          '#cc8844, {colours}') +
    'the mug periwinkle and round, lit on the left with a white highlight strip down its left side and falling into '
    'plum shadow on the right through 50% checkerboard dithering; the lip a white ring, the coffee a rust-brown oval '
    'with a tan highlight and one small white glint; the handle a thick round loop with a clear hole; {print2}; three '
    'wavy wisps of steam rising from the coffee, white with a mauve grey edge on their right so they also show on '
    'a white background. It must read at a glance as a warm drink to sip slowly, not a pot, a bucket or a bowl. '
    + LINE)
PROMPTS['mug'] = MUG.format(print='a pink heart', colours='pink #ffaabb, hot pink #ff0066',
                            print2='a small pink heart printed on the front, its right half hot pink')
PROMPTS['mugsun'] = MUG.format(print='a small yellow sun', colours='yellow #ffee55, peach #ffaa77',
                               print2='a small yellow sun with short rays printed on the front, peach on its right')


def cell(im: Image.Image) -> Image.Image:
    """An icon on a mint 384px cell, 8x nearest, centred."""
    c = Image.new('RGB', (CELL, CELL), MINT)
    big = im.convert('RGBA').resize((im.width * S, im.height * S), Image.NEAREST)
    c.paste(big, ((CELL - big.width) // 2, (CELL - big.height) // 2), big)
    return c


def grid(draft: str) -> tuple:
    """The sheet (five real icons, the draft bottom right) and the render reference, in .scratch."""
    ims = [Image.open(SITE / f'img/icons/{n}_recolor.png') for n in REFS]
    ims.append(Image.open(HERE / 'out' / 'render' / f'{draft}.png'))
    sheet = Image.new('RGB', (CELL * 3, CELL * 2), MINT)
    for i, im in enumerate(ims):
        sheet.paste(cell(im), ((i % 3) * CELL, (i // 3) * CELL))
    SCR.mkdir(parents=True, exist_ok=True)
    out = SCR / f'grid_{draft}.png'
    sheet.save(out)
    ref = SCR / f'{draft}_render_ref.png'
    Image.open(HERE / 'out' / 'render' / f'{draft}_render.png').convert('RGB').resize((768, 768), Image.LANCZOS).save(ref)
    return out, ref


def fal(draft: str, tag: str, n: int, max_spend: float) -> list:
    sheet, ref = grid(draft)
    outs = [SCR / f'fal_{tag}_{i}.png' for i in range(n)]
    return generate(outs, PROMPTS[draft], refs=[sheet, ref], aspect='3:2', max_spend=max_spend)


def largest(m: np.ndarray) -> np.ndarray:
    """The largest 4-connected part of a mask."""
    lab = np.zeros(m.shape, int)
    best, best_n, k = 0, 0, 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        k += 1
        st, n = [(y0, x0)], 0
        lab[y0, x0] = k
        while st:
            y, x = st.pop()
            n += 1
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = k
                    st.append((yy, xx))
        if n > best_n:
            best, best_n = k, n
    return lab == best


def sample(im: np.ndarray, x0: float, y0: float, px: float) -> np.ndarray:
    """48x48 frame letters: each cell's middle, its median colour, the nearest frame colour ('.' for the mint)."""
    keys = [k for k in LEG if k != '.']
    pal = np.array([LEG[k][:3] for k in keys], float)
    g = np.full((48, 48), '.', dtype='<U1')
    H, W = im.shape[:2]
    for j in range(48):
        for i in range(48):
            ya, yb = int(y0 + (j + 0.3) * px), int(y0 + (j + 0.7) * px) + 1
            xa, xb = int(x0 + (i + 0.3) * px), int(x0 + (i + 0.7) * px) + 1
            if ya < 0 or xa < 0 or yb > H or xb > W:
                continue
            c = np.median(im[ya:yb, xa:xb].reshape(-1, 3), 0)
            k = keys[int(np.argmin(((pal - c) ** 2).sum(1)))]
            g[j, i] = '.' if k == 'm' else k
    return g


def snap(src: Path, name: str, fit: bool = False, keep_bits: bool = False) -> Path:
    """fit: size the object to the icon (its widest side to 46px, standing on the bottom row) rather than keep the
    slot's own scale. keep_bits: keep detached pieces (zzz, rays) instead of only the largest part."""
    im = np.asarray(Image.open(src).convert('RGB')).astype(float)
    H, W = im.shape[:2]
    cw, ch = W / 3, H / 2                                  # the draft's slot: bottom right
    x0, y0, px = 2 * cw, ch, cw / 48
    g = sample(im, x0, y0, px)
    if fit:
        body = largest(g != '.') if not keep_bits else g != '.'
        ys, xs = np.nonzero(body)
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        f = 46 / max(bw, bh)
        npx = px / f
        x0 = x0 + xs.min() * px - (48 - bw * f) / 2 * npx
        y0 = y0 + (ys.max() + 1) * px - 47 * npx
        g = sample(im, x0, y0, npx)
    body = largest(g != '.')
    if not keep_bits:
        g[~body] = '.'
    solid = body                                           # bits (zzz, rays) keep the model's colours, unoutlined
    pad = np.pad(solid, 1)
    up, down = pad[:-2, 1:-1], pad[2:, 1:-1]
    left, right = pad[1:-1, :-2], pad[1:-1, 2:]
    edge = solid & ~(up & left & down & right)
    g[edge & (~down | ~right)] = 'K'
    g[edge & down & right & (~up | ~left)] = 'u'
    out = Grid(48, 48)
    out.a = g
    REDRAW.mkdir(parents=True, exist_ok=True)
    out.dump(REDRAW / f'{name}.txt')
    return out.save(REDRAW / f'{name}.png', 'site+')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['grid', 'fal', 'snap'])
    ap.add_argument('args', nargs='+')
    ap.add_argument('--n', type=int, default=2)
    ap.add_argument('--max', type=float, default=0.30, help='refuse if this call would cost more ($)')
    ap.add_argument('--fit', action='store_true')
    ap.add_argument('--bits', action='store_true', help='keep detached pieces (zzz, rays)')
    a = ap.parse_args()
    if a.cmd == 'grid':
        print(*grid(a.args[0]))
    elif a.cmd == 'fal':
        print(*fal(a.args[0], a.args[1], a.n, a.max))
    else:
        print(snap(Path(a.args[0]), a.args[1], fit=a.fit, keep_bits=a.bits))
