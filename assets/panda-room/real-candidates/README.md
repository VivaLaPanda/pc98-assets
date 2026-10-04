# Option: a real PC-98 room as the base (scouting, 2026-10-03)

The user rejected the hand-drawn room ("If I saw this in a game I would assume it was a highschooler's low effort doujin
project"). This folder tests the alternative: start from a genuine PC-98 background, as every scene in the site's
`img/explore/places/` already is, and edit in only the missing objects.

**Images here are gitignored** (third-party game art and edits derived from it). Only the scripts and this note are
tracked. To rebuild: copy `img/explore/places/mahou_bedroom.png` from the site repo to `mahou_bedroom_src.png`,
re-run the edit (`pc98 gen panda-room real_edit ... --refs mahou_bedroom_src.png`), align it into
`edit1_aligned.png`, then run `composite_test.py`, `pc98 preview ... preview_night` and `make_review.py`.

## Method (feasibility test)
1. **Base:** `mahou_bedroom.png` (500×268, a resampled copy of a PC-98 room; big balcony window, bed, desk, bookshelf).
2. **Additions:** one Nano Banana Pro edit added a 90s PC + newspaper on the desk, a phone on the bed, a panda plush
   (replacing a frog plush), a butterfly on the glass and a small TV in the bookshelf ($0.30 for 2 variants).
3. **Composite:** the model re-renders every pixel, so only hand-boxed object regions are taken, and only pixels that
   really changed; everything is snapped to the room's own 16 inks (k-means, on the 4096-colour grid).
4. **Night:** the same 16 inks multiplied toward navy (hue relations kept: yellow stays dim gold), the screens kept lit;
   the balcony glass shows the real PC-98 skyline from `city_overlook.png`.

## Findings
- At 1× the added objects read as part of the original; at 3× the TV's paste seam shows and the PC is a touch smoother
  than the hand dithering around it. Fixable by hand-touching the edges.
- The night palette and real skyline work well and are period-authentic.
- **Aspect ratio is the main problem:** 500×268 (1.87:1) fills the 740×528 scene window (1.40:1) only by cropping ~25%
  of the width, losing the plush and the bookshelf/TV. Either pick a 1.6:1 room (`day_simple_bedroom.png`,
  `day_bedroom.png`) or extend this one with floor/ceiling.
- VNDB's PC-98 screenshots (643 native 640×400 captures scanned) almost always include characters, so they're poor
  backgrounds; MobyGames blocks scripted access. The site's own library is the best character-free source.
