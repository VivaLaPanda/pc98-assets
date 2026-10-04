# pc98-assets

A workspace for making PC-98-style art for [vivalapanda.moe](https://vivalapanda.moe): nav icons, sprites for the
frame, scenes for the explore pages, and whatever comes next. Art is drawn in code at its true pixel size, checked in
the real page, and handed to the site by copying a PNG.

```
uv sync                                   # once: Python 3.12 + pillow, numpy, requests in .venv
uv run pc98 new reading-icon              # assets/reading-icon/{brief.md, draw.py, refs/, out/}
uv run pc98 gen reading-icon books "..." --refs assets/blog-icon/refs/style_win98_icons.png --n 2   # optional refs
uv run pc98 render reading-icon           # runs draw.py: out/<name>.png + <name>_recolor.png + review sheets
uv run pc98 compare out.png blog assets/reading-icon/out/*_recolor.png       # each candidate in the real sidebar
uv run easel new desk-corner --size 176x128 --at 0,160   # paint a scene or a piece of one on the PC-98 easel
uv run easel paint desk-corner            # replay its passages: renders, steps, look sheet with references + measures
```

**The easel** (`src/easel/`, `easel/`) is for scenes and anything that must pass for real PC-98 background art: a
simulated 16-register screen with GRCG-style 8x8 tiles and period tools only (no blending, no image models), painted
as replayable passages with a working journal. Start with `easel/notes/technique.md` (the craft, with checkable
rules), `easel/notes/research/pc98-craft.md` (sources and measurements) and `easel/notes/easel_guide.md` (the tool).

## Why a separate repo

Three homes were possible. This one won on what each would cost:

- **The site repo** is served whole: production is a `git pull` into the nginx webroot, so every reference, ledger,
  trace and screenshot committed there becomes public, and the repo should stay lean. Finished PNGs belong there;
  making them doesn't.
- **~/animations** has the plumbing (fal client, budget ledger, key file, headless Chrome), but it's a home for music
  videos with its own handbook, projects and conventions. Site assets there would be a second subject in someone else's
  house, and its git history would mix the two.
- **A new repo** is clean, and the one thing it would have to duplicate, fal access, doesn't need copying:
  `pc98/gen.py` imports `~/animations/toolkit/py/fal.py` at run time, so the key stays in
  `~/animations/secrets.txt` (read by that repo's `keys.py`; never printed, logged or copied), while spend goes to
  **this** repo's `ledger.csv` under **this** repo's budget. Nothing secret is here; the coupling is one path,
  overridable with `PC98_ANIMATIONS`.

So: a new repo at `~/git/pc98-assets` that reads the site checkout (`PC98_SITE`, default `~/git/vivalapanda.moe`)
and never writes to it.

## Setup

```
cd ~/git/pc98-assets && uv sync           # creates .venv from pyproject.toml / uv.lock
uv run pc98 --help
```
Needs Google Chrome (driven headless over the DevTools protocol for previews; `PC98_CHROME` to point elsewhere) and, for `gen` only, the animations
checkout with its `secrets.txt`. Add packages with `uv add <pkg>`; one-off tools with `uv run --with <pkg>`.

## What "PC-98" means here (it is not generic pixel art)

- **Palette discipline.** 16 colours per picture, chosen from the PC-98's 4096 (4 bits per channel: every channel a
  multiple of `0x11`). The frame, `img/background-frame.png`, uses exactly 13 such colours, and that palette *is* the
  site's look. `pc98 palette` reports any colour off the 12-bit grid; `palette.is_pc98()` enforces it on export.
- **Ordered dither, never error diffusion.** In-between tones are patterns: the 50% checkerboard above all, then 25% /
  75% staggered dots, and Bayer 4x4 for gradients in scenes. Pick the pattern per material.
- **Drawn at 640x400.** The frame is a 640x400 screen shown at 2x. Scenes are anime illustration at roughly that
  resolution, with dark lines along forms and hand-placed highlights. Generated images are references to trace and
  paint over, never the pixels that ship.
- **The nav icons are a special case:** they're Windows 98 icons (16-colour VGA) recoloured by hand into the frame's
  palette, so new icons are drawn in Windows 98's conventions and recoloured the same way (below).

### The site's palettes (`src/pc98/palette.py`)

| letter | colour | role in the frame and the icon recolours |
|---|---|---|
| `K` | `#000000` | outlines on the shadow side |
| `W` | `#ffffff` | highlights |
| `p` | `#8899ff` | periwinkle: the body colour of every recoloured icon; the paper of the envelope |
| `u` | `#664477` | plum: shadow, lit-side outlines, interior lines; the frame sprites' outline |
| `a` | `#bbaabb` | mauve grey: half-light |
| `b` | `#1133bb` | royal blue: the frame's window borders |
| `k` / `h` | `#ffaabb` / `#ff0066` | pink / hot pink accents |
| `y` `e` `n` `r` | `#ffee55` `#ffaa77` `#cc8844` `#994422` | yellow, peach, tan, rust |
| `m` | `#00eebb` | mint: the sidebar's own background, so only small accents inside icons |

Three of the 16 slots are free (`EXTRA` has a deep teal). `background-frame-dark.png` swaps the stripes to
`#00eebb` / `#222233` and hot pink to `#ff1144`.

## Asset types and their conventions

### Nav icons (`img/icons/<name>.png` and `<name>_recolor.png`)
Measured in Chrome: each icon is drawn **72 px wide** with smooth (bilinear) scaling (the site sets no
`image-rendering`), so a 48x48 icon shows at 1.5x (the 32x32 envelope at 2.25x). The original is an indexed PNG in
the VGA palette, colour 0 transparent; the `_recolor` is RGBA in the frame palette, and is what the sidebar shows.
Draw at **48x48, filled nearly edge to edge**, in Windows 98's rules:
- 1 px outline: dark/black on the shadow side (bottom, right), a mid tone on the lit side (grey, plum in the recolour);
  interior lines in the mid tone, not black;
- light from the top left; white highlights; one mid tone and the 50% checker between tones; no anti-aliasing;
- square to the frame or a slight three-quarter view. A pixel-exact `Grid.skew()` exists for tilted objects, but the
  tilted newspaper looked busier than any of the originals: prefer square.
- recolour: paper and bodies go periwinkle (`W`->`p`, `S`->`a`, `G`->`u`), as the user's own envelope recolour did;
  white survives only as highlights; one accent colour per icon (hot pink seal, pink feather...).
- text is grey type lines (words of varied length with 1 px gaps, an indent per paragraph), never squiggles: blind
  judges called squiggled handwriting "a typical AI approximation of writing".

### Frame sprites (the striped panels of `img/background-frame*.png`)
15-30 px objects at 640x400, freely rotated, 1 px **plum** outline all round (no black), white bodies turning mauve
through a checker, one accent colour, light from the top left. Draw them as Grids, paste with `pc98 compose`, preview
with `--override img/background-frame.png=...`.

### Scenes (`img/explore/places/`)
Originals are 416x224 to 640x400 and are drawn into the 740x528 window with `background-size: cover`. Most have <= 16
colours; scraped ones often aren't on the exact 12-bit grid (other 4-bit-to-8-bit mappings), so 12-bit is a rule for
new art and only a warning for old. Recipe: a generated reference -> `pc98 pc98ify` (16 colours, Bayer 4x4) -> load
the result as a Grid and repaint in code: lines along forms, flat areas where the dither is noise, patterns per
material, highlights by hand -> `pc98 preview --page explore/<page>.html --override img/explore/places/<x>.png=...`.
For a full scene, the paint-over in `assets/panda-room/` is the worked example: trace an image-model underlay off
gridded zooms (`pc98 zoom`), lay flat planes, light as hand-placed hard-stepped fields, cel shadows from offset masks.
Its `NOTES.md` lists the techniques that worked and the ones that didn't. That paint-over was rejected as amateur;
new scene work goes on the easel instead: `easel/pieces/mahou-pc/` paints a glowing PC into a real PC-98 room at
night (start from a real picture, re-time it with registers, light with `relight`), and `easel/pieces/panda-desk/`
starts a desk corner from a blank screen.

## Making an asset, end to end

1. **Brief.** `uv run pc98 new <name>`, then write `assets/<name>/brief.md`: where it lives on the site, what it sits
   next to, what it must say at its real size.
2. **Study.** `uv run pc98 palette 'img/icons/*_recolor.png'` (globs are relative to the site), `pc98 sheet` of the
   neighbours, `pc98 preview` of the page as it is.
3. **References (optional, cheap).** `uv run pc98 gen <name> <tag> "<prompt>" --refs <style image> --n 2`. Each call
   refuses past `--max` dollars (default $2) and the workspace budget (`PC98_FAL_BUDGET`, default $25); `pc98 ledger`
   shows spend per asset. Nano Banana Pro edit with the neighbours as a style reference gave good compositions.
   `uv run pc98 trace refs/gen/x.png` snaps a reference to its own pixel grid, quantizes it and writes an ASCII
   draft. Use it to see proportions; then draw.
4. **Draw** in `assets/<name>/draw.py` with `pc98.pixel`: `Grid`, masks (`rect`, `ellipse`, `poly`, `line`,
   `polyline`, `grow`, `shrink`), `fill`, `dither` (checker / q1 / q3 / h / v), `edge` (selective outlines), `patch`
   (ASCII pixels by hand), `recolor`, `skew`. Masks returned by the drawing let the recolour treat regions differently.
   `uv run pc98 render <name>` exports and writes `out/sheet_recolor.png` and `out/sheet_original.png`
   (1x, as shown at 72 px, 6x).
5. **Check in place.** `uv run pc98 compare out.png <slot> a_recolor.png b_recolor.png` puts each candidate into the
   page's own sidebar (whatever layout the site has that day) and lays the sidebars side by side; `--scale 1` is a
   normal screen, 2 a retina one. `uv run pc98 preview <dir> --swap <slot>=<png>` writes the whole frame at 1x and 2x.
   Look at 1x, at 72 px and at 14x with a grid (`out/*.txt` are the grids as ASCII).
6. **Blind test.** `uv run pc98 blind <dir> --real <site pngs> --new <your pngs>` builds lineups and pairs plus a key
   kept outside `<dir>`; run 3-6 separate judge agents on a different model with the prompts in `pc98/blind.py`,
   each reading only its own images. Fix what they name, not what they don't. Recognisable source art (the Windows 98
   originals) is a confound no drawing can beat.
**Scenes go on the easel** instead of `draw.py`: `uv run easel new <piece> --size WxH --at X,Y`, then passages in the
order of `easel/notes/technique.md` (palette, underdrawing, lines, flats, form, light, detail, highlights, tune),
`uv run easel paint <piece>` and a look at `out/look.png` after each, `uv run easel note <piece> "..."` for what you
saw, `uv run easel preview <piece>` in the real page, `uv run easel checkpoint <piece>` for keepers.

7. **Hand over.** Copy the chosen `out/<name>.png` and `out/<name>_recolor.png` into the site's `img/icons/` under
   the name the site uses. Never commit to the site from here; the user integrates.

## Commands

| command | does |
|---|---|
| `pc98 new NAME` | scaffold `assets/NAME/` from `templates/draw.py` |
| `pc98 palette IMG...` | colours used (paths or site-relative globs), 12-bit check, `--swatch`, `--json` legend |
| `pc98 gen ASSET TAG PROMPT` | fal references (default Nano Banana Pro edit, $0.15), into `refs/gen/`, plus `refs/sheet.jpg` |
| `pc98 ledger` | fal spend per asset and total |
| `pc98 trace IMG` | reference -> pixel-grid draft (snap to its own grid or box-fit), ASCII + PNG + sheet |
| `pc98 render ASSET` | run `assets/ASSET/draw.py` |
| `pc98 sheet OUT ICON...` | contact sheet: 1x, as shown (72 px smooth), 6x |
| `pc98 compare OUT SLOT PNG...` | candidates in the real sidebar, side by side |
| `pc98 preview DIR [ICONS...]` | the page in headless Chrome at 1x and 2x, `--swap`, `--override`, `--page`, `--pad` |
| `pc98 pc98ify IMG OUT` | scene first pass: `--size WxH`, 16 colours on the 12-bit grid (`--keep`, `--palette`), Bayer dither |
| `pc98 compose BASE OUT --put PNG@X,Y` | paste sprites into a site image at exact pixels |
| `pc98 zoom IMG OUT X0 Y0 X1 Y1` | gridded zoom in native coordinates for tracing; `-z`, `--beside` a second image |
| `pc98 blind DIR --real ... --new ...` | blind-test images and key |
| `easel new PIECE --size WxH --at X,Y` | start an easel piece (`easel/pieces/PIECE/`) |
| `easel paint PIECE [--upto N]` | replay its passages; 1x/2x/3x, steps, look sheet, layer (if on a real base), measures |
| `easel note PIECE "TEXT"` | dated journal entry |
| `easel checkpoint PIECE [LABEL]` | keep the current render |
| `easel preview PIECE` | composite into the site page (`[site]` in piece.toml) and screenshot it |
| `easel metrics IMG...` | thinline / edge / checker / flat / black against pro PC-98 interiors |

## Layout

```
src/pc98/      the library and CLI: palette, pixel (Grid), trace, gen, preview, sheet, icon, scene, blind
src/easel/     the PC-98 easel: canvas (registers, tiles, pens, masks, fences, relight), patterns, metrics, base
easel/notes/   technique.md (the brief), easel_guide.md (the tool), research/ (sources, measurements)
easel/pieces/  one folder per painting: piece.toml, passages/, journal.md, out/
templates/     draw.py for new assets
assets/NAME/   brief.md, draw.py (the source of truth), refs/ (gen/ and trace/ are gitignored), out/ (finals, sheets,
               review/ with in-context screenshots)
ledger.csv     fal spend (no secrets)
```
Gitignored: `.venv/`, `.preview/` and `.scratch/` (temporary pages and files), `assets/*/refs/gen/`,
`assets/*/refs/trace/`, `assets/*/out/scratch/`, easel look sheets and previews (they embed third-party crops), and
`easel/pieces/mahou-pc/out/` (paints into a third-party room).

## The cover filter and style guide

`filter/` holds the PC-98 style guide (start there before drawing anything), a lint for its measurable rules, and the
harness behind the site's in-browser cover filter `js/pc98.js`. See `filter/README.md`.

## Assets so far

- `assets/blog-icon/`: the blog's nav icon, three candidates (newspaper recommended, scroll, quill), with blind-test
  results. See its `brief.md` and `out/review/contact_sheet.png`.
