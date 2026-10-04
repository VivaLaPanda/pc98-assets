# panda-room

**What it is.** The site's "find me online" page (vivalapanda.moe), as a PC-98 adventure-game scene: Panda's cosy
bedroom at night with a big window onto a lit-up city. The visitor is Panda's guest; every lit object in the room is
one of the user's accounts. Hovering an object makes Panda comment on it in the existing dialog box; clicking gives a
short dialog and then a choice ("→ Visit GitHub / → Look at something else"). Unlike the explore map (illegible on
purpose), this page must be **legible**: what's clickable has to be obvious.

**Where it lives.** The 740×528 CSS px scene window of the site's 1280×800 frame (`#main-image`), with the dialog box
below and Panda's portrait on the right. Native art ≈ **448×320** (aspect 740:528 ≈ 1.40), shown at ≈1.65× like the
existing explore scenes (~448×272 native at ~1.7×).

**Themes the user likes:** cute anime girls, cities and urbanism, comfiness.

## Objects, ranked by how much the user uses each account

Prominence (size, position, light) follows this order.

| rank | account | object | prominence |
|---|---|---|---|
| 1 | Twitter | the big **window**, city lights beyond | centre, largest |
| 2 | Signal / Discord | **phone** on the bed, glowing screen | foreground |
| 3 | GitHub | **PC** with a lit monitor | large |
| 4 | Substack | **newspaper** (on the desk or bed) | medium |
| 5 | Reading list | **bookshelf**, lamp over it | medium, to the side |
| 6 | Bluesky | small **butterfly** ornament on the windowsill | small |
| 7 | Letterboxd | small **CRT TV** in a corner | small |
| 8 | anything else | tiny knick-knacks (radio/stereo, a plush, posters) | minimal or none |

## Hard requirements

- **Lighting is the affordance.** Every interactive object is a light source or lit thing (monitor glow, phone
  screen, city lights, lamp over the shelf, TV glow); the rest of the room sits in dithered navy/violet shadow.
- **No character in the scene.** Panda speaks through the dialog box and portrait; at most hints of her (a plush, a
  hoodie on a chair, slippers).
- **PC-98 rules** (`filter/PC98_STYLE_GUIDE.md`): ≤16 colours on the 12-bit grid; night field of navy/violet with warm
  point lights; ordered dither only; clean shapes; no garbled lettering (leave screens and signs textless or drawn).
- Style references: the site's `img/explore/places/bedroom.png` (cosy pink room), `city_overlook.png` (night skyline
  through a window, warm lamp), `night_musician_bedroom.png` (night desk lighting).

## Process

1. **Layouts (this round).** 3–4 genuinely different compositions from Nano Banana Pro with the site scenes as style
   references, each given a quick PC-98 pass (the cover filter's illustration preset) and annotated with the object
   map. The user picks one. Budget about $1, at most $2.
2. **Final art.** Repaint the chosen layout by hand in code: lines, flat shapes, per-material patterns; every object on
   its own layer/mask so it can brighten on hover; city lights palette-cycled to twinkle.
3. **Integrate.** Copy the scene and object masks into the site; the page's hotspot data points at them.

`research.md` holds the dialogue and affordance research (PC-98 adventure-game hotspot conventions, VN line style,
draft lines for every object).

## Candidates

Layout round, 2026-10-03: four Nano Banana Pro references ($0.60; prompts in `ledger.csv`), each cropped to 1.40 and
given a PC-98 pass by the site's own filter (`js/pc98.js`, illustration preset, 448×320, 16 colours) via
`layouts.py`. Sheets: `out/layouts_in_site.png` (each option in the real frame, in place of the contact page's scene)
and `out/layouts_contact_sheet.png` (reference | PC-98 pass with the object map by rank). Generated references are in
`refs/gen/` (gitignored).

- **A, window centred behind the bed (recommended).** Window centred and dominant, phone glowing mid-bed, PC and
  newspaper left, lamp-lit shelf and TV right, butterfly on the sill. Hierarchy reads in rank order, objects are well
  separated (clean hotspots), and the warm orange city against the cool navy room is very PC-98.
- **B, big window left, desk under it.** Biggest window, but the PC sits in front of it (Twitter and GitHub hotspots
  would overlap) and the bookshelf (rank 5) reads too large.
- **C, corner room, city panorama on two walls.** The most urbanist view, but the window breaks into small panes
  further back and the TV is cut off at the edge.
- **D, from the bed.** Cosy, but the big foreground phone competes with the window, and the bed is a large dead area.

## Notes

- The filter at 448×320 flattens small bright details: the phone's glow and the butterfly nearly vanish in the
  passes. The final repaint must keep both lit by hand.
- The neon signs in every reference carry pseudo-lettering, the fastest PC-98 tell (style guide rule 9): repaint them
  as abstract lit shapes.
- Final-art plan: repaint the chosen layout in code over the PC-98 pass (lines, flat shapes, per-material patterns),
  each object on its own mask so it can brighten on hover, city windows on palette-cycled indices to twinkle.
