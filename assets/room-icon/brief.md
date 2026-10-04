# room-icon

The sidebar nav icon for Panda's Room (`/room.html`, the "find me online" page: a night bedroom where each object is
one of Panda's accounts). It takes the empty slot beside the blog's newspaper, in the sidebar's third row.

## What it must sit next to

The site's computer, cd_audio, envelope_closed and globe_map icons, plus the newspaper from `assets/blog-icon`. These
are Windows 98 icons, or drawn the same way, recoloured into the frame's PC-98 palette. They share:
- **Size:** 48x48, filled nearly edge to edge.
- **Outline:** 1px; black on the shadow side, plum on the lit side.
- **Light:** from the top left, with white highlights, one mid tone, and a 50% checker between tones.
- **Colour:** periwinkle `#8899ff` as the body colour, with accents from pink, hot pink, tan and yellow.

See `assets/blog-icon/brief.md` for the measurements.

## Reading it

At 72px the icon has to say "visit my room" in a glance, and must not collide with its neighbours:
- the computer already means home (`/index.html`);
- the envelope already means contact.

## Candidates (`out/`, each `<name>.png` original + `<name>_recolor.png`)

1. **bed2** (chosen): a bed with Panda's plush sitting on the pillow.
   - The headboard is tan wood, the blanket pink with a hot-pink hem, and the mattress side periwinkle with a checker at the bottom.
   - It's the room itself, and the plush is Panda: it reads as "Panda's room" at once.
   - It doesn't read as "home", and pairs with the newspaper as the third row's two cosy things.
2. **house**: a little three-quarter-view house with a pink roof, lit windows and a chimney. The strongest silhouette, but a house in a nav bar reads as "home page", which the computer already is.
3. **door**: a door swung open, with warm light spilling across the floor and a glimpse of a night window inside. It reads as "enter", but the flat yellow block is the weakest of the four in the set.
4. **bed**: the first pass at the bed. The panda floated above the pillow, the blanket's side was a loud hot pink, and it filled only the lower half of the canvas.

## Review

- `out/sheet_recolor.png`, `out/sheet_original.png`: the candidates beside the site's four icons (1x, as shown at 72px, and 6x).
- `out/review/sidebars.png`: each candidate in the real sidebar of `contact.html`, beside the blog newspaper.
- `out/review/<name>/`: the per-candidate previews.

Installed in the site as `img/icons/room.png` and `img/icons/room_recolor.png`.
