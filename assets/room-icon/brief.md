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

## Round 2 (2026-10-06): the user on bed2, "this icon kinda sucks"

Why bed2 failed beside the set: a flat side view among chunky three-quarter objects; the plush a flat black-and-white
sticker floating at the headboard; tan and rust wood, outside the set's periwinkle/plum/pink. Round 2 (`draw2.py`,
`out2/`) draws straight in the frame palette, so every shade is chosen: periwinkle bodies, plum shadow and lit-side
outline, black shadow-side outline, white highlights, mauve half-light, pink and hot pink. The plush's white fur takes a
**periwinkle** half-light (moonlight, and the set's body colour), which ties a white thing into the set instead of
leaving a hole.

1. **tuckedin** (recommended): Panda tucked into bed, seen from the foot (the RPG-inn view), periwinkle headboard
   and posts, mauve pillow so the white face reads, the sheet folded over its chin with two paws on it, a pink quilt
   with dotted hot-pink quilting falling into shadow on the right. Reads as "bedroom + Panda" at once and matches the
   set best: three-quarter volume, the computer's pink, nothing outside the palette.
2. **ajar**: the bedroom door swung inward, a warm peach room with a night window inside, Panda peeking around the
   door's edge with a paw on it. "Come in" plus Panda; narrower than its neighbours, so a touch lighter in the row.
3. **nightwindow**: the room's balcony window (navy sky, crescent moon, plum skyline with lit windows, pink curtains
   tied back) with the plush on the sill, rimmed in moonlit periwinkle. Echoes the page's main feature; the busiest of
   the four, and its navy is the darkest mass in the sidebar.
4. **moonpanda**: the plush's head against a crescent moon. The clearest silhouette, but it's a face among objects
   (reads as an avatar / "about me") and the heaviest white in the row. A pink nightcap was tried and dropped: with a
   white band and pom-pom it read as a Santa hat.

Phones never show this icon: below the mobile breakpoint the whole sidebar is hidden on every page, so 72 px
(48 at 1.5x, smooth-scaled) is the only size that matters.

Review: `out2/review/rows_72px.png` (each candidate in the sidebar's row at 72 px), `out2/review/sheet_all.png`
(1x, 72 px, 6x beside the set and the old bed2), `out2/review/sidebars.png` and `out2/review/sidebar/desktop_*.png`
(the real sidebar of contact.html at 2x, candidate swapped in by request interception; `sidebar_shots.js`).
To install one: copy `out2/<name>.png` and `out2/<name>_recolor.png` to the site's `img/icons/room.png` and
`img/icons/room_recolor.png`.

## Round 3 (2026-10-06): no bed

`tuckedin` went in (site db2c97a); the user: "I feel like the bed evokes sleepytime, not: - home - directory -
bedroom". So the icon has to say Panda's home, a directory (the page is a list of Panda's places online) and Panda's
own room. `draw3.py`, `out3/`, same palette rules as round 2. Ranked on home + directory + bedroom, then fit with the set:

1. **homefolder2** (recommended): a Windows 98 folder in the set's periwinkle, papers peeking out, a little house on
   the front with Panda's face in its lit window. Folder = directory, house = home, Panda = whose; and it's one of the
   desktop-icon family (My Computer, CD, envelope, globe) more than anything else here. Weakest on "bedroom".
2. **cutaway**: a dollhouse cut of a tiny room: a night window, a glowing CRT on a desk, Panda on a pink rug. It *is*
   the page (Panda's room), reads as a room rather than sleep, three-quarter like the computer and globe; the busiest
   of the five, and the CRT is faint at 72 px.
3. **door**: Panda's bedroom door, nearly closed, warm light round its edge, a pink panda nameplate, star / heart /
   crescent stickers. The classic "my room" door; fills the cell; flat like the envelope. No "directory".
4. **house**: a little house at night, a pink roof, a crescent moon, Panda's face in the big lit window. The strongest
   "home", but a house in the nav risks reading as the home page (the computer), and it's the loudest in the row.
5. **homefolder**: the same folder with a round pink badge of Panda's face. "Panda's folder", clean, but it says
   "directory" and "Panda" without "home" or "room"; homefolder2 does the same job better.

Redrawn after the first pass: the house's silhouette in the window was a black blob at 72 px (now Panda's face); the
cutaway's plush and CRT were lost (now bigger, a thick white cut edge, a glow round the CRT); the folders' back panel
was grey (now periwinkle with a plum dither); homefolder2's window was too small for anything (now a mini Panda).

Review: `out3/review/sheet_all.png` (1x, 72 px, 6x beside the set, round 2's ajar and the installed tuckedin),
`out3/review/rows_72px.png`, `out3/review/sidebars.png` and `out3/review/sidebar/desktop_*.png` (contact.html's real
sidebar at 2x; `sidebar_shots3.js`). Install: copy `out3/<name>.png` and `out3/<name>_recolor.png` to the site's
`img/icons/room.png` and `img/icons/room_recolor.png`.
