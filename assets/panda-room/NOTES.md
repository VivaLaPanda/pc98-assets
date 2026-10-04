# Panda's Room: how the final art was made

Layout B ("big window left, desk under it"), repainted by hand in code at native 448x320 (16 inks on the 12-bit grid).
Source: `paint.py` (the painting, one function per passage) and `export.py` (finals, hover states, hotspots, twinkle,
review sheets). This file records which techniques worked, so the next scene can start from them.

## The pipeline that worked

1. **An underlay to trace, not to convert.** Nano Banana Pro edit, with three *real* PC-98 scenes from the site as the
   style references and layout B only as a heavily blurred guide (`refs/B_layout_blur.png`). Result:
   `refs/gen/B_pc98_0.png`, cropped to the window's 740:528 and scaled to `refs/underlay.png`. It gives anime-style
   forms, perspective and light placement to trace. Its pixels never reach the scene.
2. **Trace off gridded zooms.** `uv run pc98 zoom refs/underlay.png out.png X0 Y0 X1 Y1 -z 6` labels native
   coordinates (lines every 8 px, numbers every 16). Read the vertices off and type them in as polygons and polylines.
   `--beside out/final/room.png` puts the painting next to it at the same zoom.
3. **Paint a passage at a time and step back after each.** Look at it beside the underlay at 3-6x, then at 1x in the
   real site frame (`pc98 preview --override`). `paint.py <passage>` writes the side-by-side progress sheet.
4. **Audit everything when one thing is wrong.** The first finished version had a skull-like panda. A full
   region-by-region audit against the underlay then found ten more problems: the hoodie, the bed, the walls, the TV,
   the lamp, the plant, the desk and newspaper, the neon halos, the poster and the slippers. Fix them in order of how
   much each one hurts the picture.

## Techniques that worked

- **Flat planes.** One ink per wall or plane, with a single checker band only where the light changes. This did more
  than anything else to move the picture from "modern pixel art" to PC-98. Lint moved from flat 0.41 to 0.52 and
  checker/dot from 0.155 to 0.072; the real `city_overlook` scores 0.59 and 0.113.
- **Light as hand-placed fields cut into hard steps.** Use a `radial()` or linear field and lay it as a flat core, one
  checker ring, then the flat outside. For example, the lamp band across the bed, the phone's pool and the desk pool
  under the monitor. Choosing where the light goes is the painter's decision. Sampling it from the reference isn't.
- **Cel shadows from offsets.** `shape & ~sh(shape, -dx, -dy)` is the rim facing away from the light (the hard
  shadow). `shape & ~sh(shape, dx, dy)` is the lit rim. `sh(obj, 0, k) & ~obj & surface` is a cast shadow (under the
  pillow, the hood, the newspaper, the plush's chin). Each is crisp, follows the form and needs no dither.
- **Black on black.** Black objects against a dark ground get painted navy (`N`) with a lit top (`v`), like the panda's
  ears against the black shelf. Pure `K` on `K` disappears.
- **The chibi plush recipe**, which fixed the panda:
  - a wide squircle head (wider than tall);
  - bean-shaped eye patches tilted down and out;
  - 2x2 catchlights high on the inside plus a 1 px low glint;
  - a small inverted-triangle nose and a ω mouth;
  - checker blush in `h`;
  - a black shoulder band with the arms at the sides, and soles with felt pads;
  - hard cel shading only, never dither on the fur.
- **Flat things lying in perspective** are drawn in their own coordinates with `on_quad(A, B, D)`, which gives (u, v)
  for every pixel of a parallelogram. The newspaper's masthead band, photo, columns and fold then lie on the desk.
- **Soft furniture as two planes.** The bed's top and the face where the blanket hangs are separate polygons, with a
  lit line along the rounded edge between them. One plane graded top to bottom read as a slab.
- **Folds.** Use irregular lengths and spacing. Draw a dark fold line with a 1-3 px shadow on the side away from the
  light, and a short lit ridge only where the fold starts. Evenly spaced folds read as corduroy or radiator fins.
- **Neon.** Signs are crisp boards with abstract content (bars, a two-tone diagonal split, a filled disc), and the glow
  is one solid ring a step darker. Avoid anything glyph-like: an O ring or a slash reads as a letter.
- **The city.** Lit windows sit on each tower's regular grid. Whether a window is lit is weighted by how bright the
  underlay is there. Towers come in three depths (far haze, tall towers, near blocks), with beacons on the crowns.
- **Screens.** The CRT is flat cyan with a darker rim where the glass curves away and two hard glare stripes. The
  switched-off TV holds a faint reflection of the window. Radial dithers on screens read as bullseyes.
- **The lamp.** A grey cone with a tilted-ellipse mouth (yellow with a white core), a gooseneck drawn as a
  black/violet/black triple line, a T-clamp on the board, and a hot spot plus banded warm pools on the back panels.
- **Fronds.** Tilted ellipses fanned from the pot, with the upper face of each one lit and the window-side edges in
  green.
- **Prominence is light.** The rank order of the accounts maps onto brightness. Big surfaces that aren't links (the
  bed) are dropped a value step, so that small lit objects (the phone) pop.
- **Interactivity:**
  - masks are exclusive, assigned front to back, and clipped where something painted later sits in front (the bed
    over the TV cabinet and the shelf's foot, the chair over the desk);
  - the hover state is one step brighter along each ink's own ramp, plus a 1 px warm rim outside;
  - the city twinkle is a strip of RGBA overlay frames in which only the changing pixels are opaque (palette cycling
    without an indexed canvas).

## What didn't work

- **Pure geometry in code** (the first attempt, `room.py`, since removed): stiff, not anime, under-greebled.
- **Filter-only conversion** (`pc98ify` of a reference): small lit details vanish (phone, butterfly) and fake
  lettering survives.
- **Giving the generator the lo-fi pixel-art layout as image 1:** it copies the modern pixel-art look. Use real PC-98
  scenes as the style and the layout only blurred.
- **Grading big surfaces by the underlay's luminance** (`cel()`): blotchy camouflage on the blanket, mottled walls. It
  now survives only on the mug.
- **Dot dither over whole walls** reads as a screen door, the modern fake-PC-98 tell. **Dithered halos around neon**
  read as postage-stamp edges.
- **Thin highlight lines as folds** read as cracks or planks. **Evenly spaced folds** read as corduroy.
- **Panda v1:**
  - a tall oval head with big round patches and centred glints read as a skull;
  - Bayer shading on the fur read as noise;
  - the paws inside the belly read as holes.
- **The hoodie:** a face opening read as a head; a slab with a pocket shape read as a shield. Tracing the underlay's
  bunched hood, hanging sleeve and ribbed hem fixed it.
- **Greebles too small to draw legibly at native size** (16 px slippers read as bowling balls, then ghosts) were cut. A
  wrong greeble is worse than none.
- **Accidental objects:**
  - a wood knot on the shelf's side panel read as a door handle;
  - the plant drawn as green lines read as wire, and with short leaves as a cactus.

## Files

- `out/final/room.png`: the scene, indexed, 16 colours, 448x320; the page shows it at 740x528 (x1.6518).
- `out/final/masks/<obj>.png`, `out/final/lit/<obj>.png`: the exclusive masks and the hover overlays, full canvas.
- `out/final/hotspots.json`: rank, account, bbox and polygons per object, plus the z order.
- `out/final/twinkle.png`, `out/final/twinkle.json`: the city-light overlay frames and how to step through them.
- `out/final/review/`:
  - `site/context.png`: the scene in the real frame;
  - `lit_states.png`;
  - `zoom_vs_real.png`: 3x beside real PC-98 crops;
  - `lint.txt`.
- `out/final/progress/`: passage sheets (painting | underlay).

Spend for the final art: $0.60 (four Nano Banana Pro edits; two anime redraws, two PC-98 redraws); see `ledger.csv`.
