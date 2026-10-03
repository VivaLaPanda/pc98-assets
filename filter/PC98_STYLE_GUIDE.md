# PC-98 style guide (for vivalapanda.moe art and assets)

Written Oct 3, 2026, while building `js/pc98.js`. It draws on three sources:
- measurements of the ~100 genuine 16-colour PC-98 pictures in the site's `img/` (scripts below);
- close reading of them at 4–6x zoom;
- what blinded reviewers said gave fakes away.

Every rule is meant to be checkable. `pc98lint.py` (next to this file) measures the countable ones.

## 1. The machine (why it looks the way it does)

- **640×400, 16 colours on screen, from 4096** (4 bits per channel, so every channel value is a multiple of 0x11:
  00, 11, 22 … ff). The analog 16-colour mode was standard from the mid-80s (PC-9801VM/VX era), and earlier machines
  had 8 fixed digital colours. Some games kept that 8-colour digital look on purpose, with pure blue, cyan, red,
  yellow, green, magenta, white and black (`night_storefront.png` is one).
- **Planar VRAM and the GRCG.** The graphics hardware has a *tile register*: an 8-pixel pattern per bitplane, written
  in one go. Patterned fills ("tile patterns", タイルパターン) were therefore cheap and idiomatic, and the paint tools
  of the day offered them as fill styles. That is why PC-98 dithers are a few *regular* patterns and never
  error-diffusion noise. (rec98.nmlgc.net, 2020-12-18, documents the GRCG tile register.)
- **High resolution, no pixel doubling.** Compared with PC-88 or DOS 320×200, PC-98 art is "crisper" and "creamier".
  At 640×400 a 1px line is a fine pen line, and a checkerboard blends into a third colour on a CRT. The art is drawn
  for the 4:3 monitor, but on the web we show it with square pixels at 1 CSS px per art px (2×2 device px on retina).
  Chunky 2x pixels read as "PC-88 or DOS", not PC-98.
- Visual-novel scenes usually sit in a **window of about 448×272 or 512×288** inside a frame. Full 640×400 is
  for event CGs.

## 2. Measured from the references (16-colour images in `img/explore`, `img/*.png`)

| property | typical value | example |
|---|---|---|
| colours per image | 8–16, almost always exactly 16 for scenes | `day_city_street.png` 16 |
| on the 4096 grid | 100% of colours in every true PC-98 rip (off-grid files are later re-encodes) | |
| black (000) present | in nearly every image: it is the ink | train_platform 18% of pixels |
| white (fff) present | in most day scenes; often absent at night | |
| pixels in flat 4-neighbourhoods | 25–45% | fish 44%, ghetto 45% |
| pixels inside a checker or dot pattern | 8–30% (one outlier at 60%) | day_diner 30%, garage 60% |
| 2-colour 4×4 blocks by minority share | 8/16 (checker) and 4/16 (dot grid) dominate, then 2/16 and 6/16 | |
| dithered pair contrast | mean OKLab ΔE 0.10–0.20: dither joins **neighbours on a ramp** | 776677/888899, ffbbaa/ffddcc |

Palettes are built from short ramps, with a few accents:
- **Skin ramp**: ffddcc / ffbbaa / ee8877, highlights ffffff.
- **Cool neutrals tinted lavender or blue**, never pure grey: 776677, 888899, 555577, 333344, 444455, bbbbcc.
- **Shadows lean navy and violet**: 112277, 222244, 330088, 333377.
- **Warm light**: ffcc99, ffddbb, ffcc77.
- **2–4 saturated accents** for signs, neon and clothing: dd0044, ff7799, 1144bb, 00aaff, ffdd00, ee0000.

Two-hue dithers that make a third, "virtual" colour are common: blue/salmon gives lavender (garage), and blue-grey with
peach gives lilac (day_apartments).

## 3. Rules

**Palette**
1. At most 16 colours per image, all on the 4-bit-per-channel grid.
2. Include true black. Include true white if anything is lit.
3. Build ramps (2–4 steps per material). Shift hue along a ramp: darker steps lean cooler and more violet, lighter
   steps warmer and more peach. Use no neutral greys.
4. Keep 2–4 saturated accents for what the eye should find first.
5. Night scenes: navy and violet field, warm point lights, black silhouettes. Day scenes: high key, with lavender
   greys, cream and white.

**Shapes and lines**
6. Draw shapes first. Every object is a closed, simple shape with a clean border: straight runs on architecture,
   smooth curves on organic things. No ragged posterisation edges.
7. Line art is 1px, dark, and continuous. It sits on object contours, not on shading steps (no ink between two skin
   tones). It is usually black on characters, and a dark ramp colour or black on backgrounds. Keep lines
   pixel-perfect: no doubled L-corners on diagonals.
8. Repeated structure stays regular: window grids, railings, tiles and stair edges.
9. Lettering is either drawn legibly or left out. Garbled text is the fastest tell.

**Fills and dithering**
10. Most shapes are flat. Small shapes (under ~60 px at thumbnail scale) are *always* flat.
11. Dither only where a tone changes across a shape (sky, wall falloff, skin turning away from light) or to make a
    deliberate texture or virtual colour over a whole surface (glass, mesh, fabric).
12. Use only the tile patterns: 1/8 sparse dots, 1/4 dot grid, 1/2 checkerboard, 3/4, 7/8 (the Bayer 4×4 matrix cut
    at 2, 4, 8, 12 and 14 of 16). They nest, so a gradient reads as flat → dots → checker → dots → flat, in clean bands.
    Never use error diffusion (Floyd–Steinberg) noise.
13. Dither between neighbours on a ramp (ΔE ≈ 0.1–0.2). High-contrast pairs, like black and white checker, are
    textures, not tones.
14. One surface gets one pattern field. Patterns must not change every few pixels (the "confetti" tell).
15. Skies are banded gradients: horizontal bands, or concentric rings around a light source.

**Composition and subject** (what a filter cannot fix)
16. Simplify. Leave out clutter, noise and depth-of-field blur. Pick a focal point.
17. Light has a source, and shadows are shapes.

## 4. What gave fakes away (blinded reviewers, rounds 1–3 and final)

In the final round, Sonnet judges saw genuine PC-98 crops next to filter output on the same kind of subject. In
forced-choice they picked the genuine one in 34 of 36 pairs, at about 90% confidence. Their tells, roughly in order:
1. Region shapes that follow photo texture: amoeba-like blobs with ragged edges (foliage, crowds, aerials).
2. Garbled lettering, and broken window grids, rails and straight lines.
3. Missing or fragmentary line art.
4. Dither used everywhere, or as confetti, rather than on purpose.
5. Photographic lighting and colour: vignettes, muddy close mid-tones.
6. Subject matter: modern cars, aerial suburbs, Western shopfronts.

They called these convincing: the 16-colour palette, the ordered-dither texture itself, night scenes with navy fields
and warm lights, and flat illustration input. The default illustration cover was rated 80–85% "genuine" on its own.

## 5. How `pc98.js` implements this

| rule | implementation |
|---|---|
| 1–2 | Weighted k-means in OKLab on the filled image, black fixed, white added when the 99.7th-percentile L > 0.86. Each ink is gamut-mapped (chroma pulled in at constant hue) and snapped to the best of its 8 surrounding grid points by OKLab distance. |
| 3–5 | The colour grade before anything else: levels, a key (midtone gamma toward median L 0.64, bounded so night stays night), saturation ×1.7, and a soft highlight knee. Then a scene tint that adds navy/violet to shadows, lavender to mids and peach to highlights, scaled down for already-colourful pixels and for skin. The palette inks get a chroma boost (k-means averages grey them out). k-means weights favour chroma and skin, so accents and faces get inks. |
| 6, 16 | Edge-aware flattening (domain-transform recursive filter), then Felzenszwalb–Huttenlocher graph segmentation. Small low-contrast crumbs merge and small high-contrast bits survive. Then a 7-of-8 border tidy (keeps 1px poles) and a 5×5 majority round-off on big shapes. |
| 10–11, 14–15 | Each shape gets a smooth fill: flat when small, a ridge-regularised plane when medium, a quadratic when big. Neighbouring shapes whose fills meet without a visible step merge, so a sky becomes one shape. Each pixel then picks a flat ink or a two-ink pattern for its fill colour, so patterns run as regular bands across a shape. |
| 12–13 | Patterns are Bayer-4×4 cuts {2, 4, 8, 12, 14}/16 between two inks, mixed in linear light. A pattern costs a share of the pair's own contrast plus a floor, and pairs with ΔE > 0.22 cost extra. The 5 nearest inks are considered. Shapes under `ditherMinArea` are flat. |
| 7 | 1px line on the darker side of every shape border whose fill contrast passes a threshold. There is no line between two skin-like tones unless the jump is large. Lines get a pixel-perfect pass. The ink is the nearest palette colour to a darkened version of that side, and must be darker than it. |
| 9, 16–17 | Not solvable per pixel. See section 6. |

## 6. Limits, and the next tool

A per-pixel or per-region filter keeps a photo's structure: its clutter, its lettering and its lens. That is what the
judges caught. The experiment in `redraw/` takes a different route. An image model first redraws the photo as a
90s anime background (clean lines, flat cels, legible signs), at about $0.15 per image, and `pc98.js` then converts it
with the illustration preset. That fixes tells 1–3, but it has to be checked by eye: the generator removed the child
from the truck photo. For assets that matter (hero images, explore scenes), do the PC-98 pass on art that already has
drawn structure, whether hand-made, traced or redrawn, rather than on photographs.

## 7. Tools

- `pc98lint.py img.png …`: colour count, grid compliance, black and white present, flat and dither shares, dither-pair
  contrast, and 4×4 block pattern histogram. Run it on references and on your output and compare.
- `compare.html`: originals, filter output, and real PC-98 crops side by side, at blog scale.
- `run.js` with `pngio.js`: a Node runner that uses the same `pc98.js` code, for offline pre-rendering, byte-identical to
  the browser.
- `blind_final.py`: builds blinded A/B pairs and singles, with the answer keys kept outside the judges' folder.
