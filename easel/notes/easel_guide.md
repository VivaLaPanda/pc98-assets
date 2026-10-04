# The easel: a guide for the painter

The easel is a simulated PC-98 graphics screen and the tools a 1990s staff artist had on it (Z's STAFF Kid98,
マルチペイント). Nothing in it blends: every pixel is one of 16 registers, each a colour from the 4096-colour grid, and
intermediate tones come only from 8x8 tile patterns anchored to the screen, as with the GRCG. There are no image models
here. Read `technique.md` first; it is the brief this tool is built to enforce.

## A piece

```
easel/pieces/<name>/
  piece.toml        canvas size, where it sits on the screen (`at`), look-sheet settings, references, site preview
  passages/NN_*.py  the painting, run in order in one shared namespace, replayed from scratch on every paint
  journal.md        what you saw when you stepped back, and what you changed because of it
  out/              renders (see below)
```

A passage is one stage of the work, e.g. `03_lines.py` or `07_light.py`. Passages are the replayable log, like
stillwet's strokes: editing an early passage repaints everything after it. Constants defined in one passage
(vanishing point, boxes, silhouettes) are visible in later ones.

## Commands

```
uv run easel new <piece> --size 176x128 --at 0,160    # scaffold (at = its place on the full screen: tiles anchor there)
uv run easel paint <piece> [--upto N]                 # replay passages 00..N, write renders + look sheet, print measures
uv run easel note <piece> "what I saw, what I'll do"  # dated journal entry
uv run easel checkpoint <piece> [label]               # keep the current 1x render under out/checkpoints/
uv run easel preview <piece>                          # the piece in the real site page ([site] in piece.toml;
                                                      #   blank=[images] and hide=[css selectors] drop page
                                                      #   overlays drawn for older art)
uv run easel metrics <img...>                         # any image against the pro PC-98 ranges
```

`paint` writes `out/<piece>.png` (1x), `@2x`, `@3x`, `steps.png` (the picture after each passage), `piece.json`
(registers, names, cycles), `cycle.gif` if any registers cycle, and `look.png`, the sheet to step back with: the
picture and the underdrawing; before/after if it started from a real picture; yours at 1x/2x beside the references;
your regions beside reference crops at the same zoom; the palette with each register's share; measures against pro
PC-98 interiors and pc98lint. A piece started from a real picture also gets `out/<piece>-layer.png`: only the pixels
you changed, in place (RGBA).

## The namespace a passage sees

- `cv` the canvas, `ud` its underdrawing layer, `P` the tile library, `T(pattern, ground, ink)` a tile (ground None =
  ink only over what's there), `np`, `rng` (seeded), `bresenham`, `ellipse_points`, `quantize`, `resolve`, `Image`.
- **Registers:** `cv.pal_set(i, '#rgb', name)`, `cv.palette(...)`, `cv.cycle([i...], fps)`. Change a register any
  time: the whole picture follows (the period way to re-time a scene: night is a register change).
- **Pens:** `dot`, `dots`, `line`, `polyline`, `rect` (fill or outline), `ellipse`, `poly`, `fill(mask, c)`,
  `flood(x, y, c)`, `stamp(x, y, text, key)` (pixels by hand).
- **Tiles:** any `c` above may be a tile. `grad(mask, a, b, t)` steps between two registers in tile bands
  (none, 1/4, 1/2, 3/4, solid); `t` from `lin(p0, p1)`, `rad(c, r0, r1)` or any array.
- **Light on what's painted:** `relight(mask, level, ramp, tile_on=...)`: each ink steps up its own ramp (a dict
  ink -> next lighter ink); `level` 1.5 = one step plus a 1/2 tile of the next. `tile_on` limits the tiled partial
  step to a surface's base inks so a texture stays coherent in the glow. Line inks left out of the ramp stay dark.
  `relight_halves(mask, level, ramp)`: the same in half steps for a surface that is already dithered (a wall's
  two-ink texture, printed paper): a dither's dark ink lifts first (solid), then a checker one step up, and so on;
  flat ground takes a 1/2 checker on the odd half steps. Use it wherever partial tiles would interfere into dust.
- **Masks (selections):** `m_all`, `m_rect`, `m_poly`, `m_ellipse`, `m_where(*inks)`, `m_region(x, y)` (a flood
  of the seed's ink; `inks=(a, b)` floods across a dithered field of several inks; `within=` fences it),
  `m_line`, `m_edge(mask, 'top,left')`, `dist_from(mask)` (rings out from a shape, for halos).
- **Fences (mask colours):** `with cv.only_over(*inks):` / `never_over`, `protect`/`release`.
- **Selections:** `copy(x0, y0, x1, y1)` -> clip, `paste(clip, x, y, transparent)`, `clip.flip()`, `clip.rot()`,
  `replace(a, b, mask)`.
- **A real picture as the ground:** `idx, pal = quantize('explore/places/x.png')` (its 16 inks on the 4096 grid),
  `cv.start_from(idx, pal)`; set `cv.base = cv.idx.copy()` again after re-timing it, so the layer holds only painting.
- **Underdrawing:** `ud.line`, `ud.poly`, `ud.rect`, `ud.ellipse`, `ud.ray(vp, through)`, `ud.cross`, `ud.label`.

## The loop

1. `00` palette by role (or the real picture and its re-timing). 2. `01` underdrawing: eye level, vanishing point,
the box of everything, the light. 3. Lines back to front: each object clears its silhouette to a ground ink, then is
inked. 4. Flats front to back, fenced `only_over(ground)`: occlusion is free; assert no ground is left. 5. Form
shading, 6. light, 7. detail, 8. highlights, 9. palette tune. After every passage: `easel paint`, look at `@3x` and
`look.png`, and write what you saw with `easel note`. Judge at 1x and 2x as well as zoomed. The look sheet's
value / squint row (1x) answers "which region leads?": check it after any light or palette change.

## Gotchas learned on the pilots

- Partial tiles laid over an existing texture read as dust. Use `tile_on`, or light the texture in whole steps.
- Light lifts everything it touches: letter small print (newspapers, labels, key gaps) after the light, not before.
- A halo drawn as a circle reads as a blob; ring it out from the light-giving shape with `dist_from`.
- A real base may be a resampled copy: measure its own regions (`easel metrics`, or `look.measure`) and match their
  line and tile density, not only the pro ranges. Crisper-than-its-surroundings is a seam.
- Choose register merges only between inks at most one grid step apart in the scene's current timing.
- A mask from an object's bounding box draws a rectangle when you rim it (`m_edge`). Use the object's own extent
  (its inks inside its outline, or a polygon), and look at the rim at 6x.
- Text on lit paper: print one ink *under* the paper's local ink (not black), and only a few rows; a 10px sheet with
  print on half its rows reads as a dark striped object.

## Recipes from mahou-pc (copy them; the passages are the worked example)

`easel/pieces/mahou-pc/passages`: 00 room + re-timing + daylight removal, 01 camera and every object in 3D, 02 clear,
03 lines, 04 flats, 04b form, 05 screen detail, 06 keys, 07 traced light, 08 print + rims + contact shadows,
09 density match.

- **Find the room's camera before drawing (01).** One-point rooms: VP and eye level from receding edges. The focal
  distance `D` from something whose real proportions you know: a round seat's ellipse (height/width = sin of the
  angle below eye level) or a box's depth vs its height. Scale from a door (~200cm). Then `proj(X, Y, Z)` (cm) puts
  any point on the canvas, and new objects are built in their own frame and projected (`mon3`/`mon`, `on_desk`), not
  eyeballed. PC-98 rooms are wide-angle (mahou_bedroom: D ~200 for a 500px picture); a guess of D decides which side
  of a turned object you see.
- **Trace light, set strength per surface (07).** Inverse-project each lit surface onto its plane (`on_plane_y`),
  sum irradiance from a grid of points on the source (emission cos x incidence cos / r^2) with occluders as slabs and
  discs. The trace gives the shape (terminator = the source's plane, shadow lines, falloff). Strength is a painter's
  choice per surface (`steps(E, top, per_stop)`, quantised to the tile bands), because true falloff leaves anything
  a metre away invisible. If the strict trace puts light where it reads as another source (the day's sun), cheat the
  occluder, not the shape, and log it in the journal.
- **Bounce** onto walls: each lit pixel of the desk/paper as a Lambertian emitter, blocked by solid bodies; light
  it with `relight_halves` so the wall's own dither stays clean.
- **Re-timing a picture removes the old light too (00):** sun patches, sunlit views, white sun highlights on
  curtains, shadow stubs. Do it before `cv.base = cv.idx.copy()`: it is the scene's timing, not the painting.
- **A picture inserted into another** (a skyline in a window) gets inks by role (`CITY_INKS`: its lit windows to the
  glow ink, lamps to white), not by nearest colour, which dims every light.
- **Match a resampled base (09):** if the base was resampled (uneven widths of repeated marks, beating dithers), put
  the painted pixels through the same journey (nearest up to the original width, bilinear back, snap to the 16
  inks), only where the new line art is; leave lighting bands crisp.
