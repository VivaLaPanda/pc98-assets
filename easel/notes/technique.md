# Technique brief: painting like a PC-98 graphics artist

Distilled from `research/pc98-craft.md`. Every rule is something you can check in the look sheet. When a rule and
your taste disagree, follow the rule and look again.

## Order of work (each step is one or more passages; step back after every one)

1. **Palette by role** (passage 00). Plan all 16 before drawing: black; a 4-5 step dark ramp that carries the room;
   one light ramp per light source (3-4 steps, ending near white); a 2-3 step material ramp per major material;
   1-3 single accents. White only for light sources and speculars. Ramps are what get tiled together.
2. **Underdrawing** (`ud`): horizon, vanishing points, the box of every object, the light sources and where their
   light falls. Nothing goes on the canvas until the boxes agree with the vanishing points.
3. **Line art**: every silhouette as an unbroken 1px line, then the interior construction lines (seams, bevels,
   panel edges, key grid). Black on machines and in shadow; the darkest of the material's own ramp on lit materials.
4. **Flats**: fill each enclosed area with its base tone (flood or polygon). No shading yet.
5. **Form shading**: 2-3 tones per surface by plane (top/front/side differ), transitions as banded tiles between
   *neighbouring* ramp colours (1/4, 1/2, 3/4). Recesses: black 1/2 over the dark tone, then solid black.
6. **Light**: sources as hard-edged flats of the brightest colour. Glow as concentric tile bands on the surfaces
   around them (`grad` with `rad`, fenced with `only_over` so line art stays on top). Rim lights: 1px of a lighter
   colour along edges that face a light.
7. **Detail**: break every surface. Seams, screws, labels as 1-2px clusters, LEDs (1 colour pixel + 1 white),
   knobs, slots, cables, clutter. If a 16x16 patch of your picture is one flat colour and it isn't a light source or
   deep shadow, it needs detail.
8. **Highlights**: speculars (1-3px white clusters) on glass, metal, glossy plastic; bevel lights on top edges.
9. **Palette tune**: adjust registers, not pixels, until the whole reads. Then look at 1x and 2x, not just zoomed.

## Checkable rules

- **Line art density**: thinline 0.09-0.23 (the look sheet measures it). Below that, you haven't drawn enough lines.
- **Detail density**: edge 0.45-0.75. **Flat** below 0.46. **Checker** 0.07-0.32.
- **Night**: black 25-66% of the picture; light concentrated around its sources.
- **No anti-aliasing, no blending.** The medium enforces it; don't fake it with single "soft" pixels along lines.
- **Tiles step between ramp neighbours only** (black-navy, navy-dusk, cyan-pale). Never tile two colours that are far
  apart in value unless you mean texture (it reads as noise).
- **Tiles are screen-aligned.** Adjacent fills line up; don't shift a pattern's phase to make it "look random".
- **Perspective is constructed, not guessed**: every receding edge on the line to its vanishing point.
- **Small text and logos are abstract clusters**, not letters, unless big enough to be legible.
- **Silhouettes against light**: a dark object in front of a bright area keeps a crisp 1px dark outline; the bright
  area may catch a 1px rim on the object's lit side.
- **Every object has three values**: light plane, mid plane, shadow plane (plus line). Fewer reads as flat cut-paper.

## What made our first room look amateur (don't repeat)

Traced shapes from an image model, soft generic "lo-fi room" composition, flat fills with almost no line art
(thinline .02), few tiles, no micro-detail, cartoon proportions. The cure is the order above, done slowly.

## Painting into a real PC-98 picture (learned on mahou-pc)

- **Re-time with registers, not pixels.** Night is the same index map with new registers (toward navy, hue relations
  kept). If the new object needs inks the scene lacks (a screen's cyan, a white), merge register pairs that land one
  grid step apart in the new timing and reuse the freed registers.
- **Follow the picture's own light.** Planes facing the picture's light source are a step lighter (in mahou_bedroom:
  left-facing planes, from the window). A new object shaded against that reads as pasted in.
- **New light lifts old surfaces along their own ramps** (`relight`): wall to lit wall, wood to lit wood, never one
  "light colour" over everything. Strongest where a surface faces the source and is near it; concentric bands out;
  rims on edges that face it; nothing behind things.
- **Match the base's density.** A resampled base has softer lines and almost no exact checkers; paint at its density
  or the new object looks sharper than the room around it.
- **Find the camera first** (focal distance from a round object or a box's depth, scale from a door) and build new
  objects in it. A wide-angle room shows a turned object's sides differently from what the eye expects.
- **Re-timing removes the old timing's light**: sun patches, sunlit views behind glass, sun highlights. Leaving
  one is a daylight tell at night.
- **Light is traced, strength is chosen.** The shape of a glow (where it stops, what casts shadows) comes from the
  geometry; how strong each surface reads is set by hand. Floors and far surfaces: at most a 3/4 tile of the glow
  ink; solid glow ink only on the source and what touches it.
- **Halos over dithered or printed surfaces go in half steps** (solid, checker, solid), never quarter tiles.
- **Keep the hierarchy**: check value and squint at 1x after every light or palette change. Lights inside an
  inserted picture are given bright inks on purpose so the intended focal point keeps leading.
