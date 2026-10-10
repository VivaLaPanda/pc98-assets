# home-icon

The sidebar's Home icon. Home is the living room (`/living-room.html`), a live copy of Panda's real house, so the icon
replaced round 3 of `assets/room-icon` (homefolder2, a folder with a house on it). The user, 2026-10-09: "I don't love
the folder/etc", and "try to avoid the home icon looking clip-art-ish. It should fit well w/ the other icons".

## What it sits with

The envelope, CD, newspaper and recipe book, which are real Windows 98 icons or drawn the same way, recoloured into the frame's palette. They share: everyday objects
with chunky three-quarter volume, every surface in a lit tone, a body tone and a 50% checker into shadow, white
highlights on edges facing the top left, a 1px outline (plum on the lit side, black on the shadow side), periwinkle
bodies with pink accents. The computer icon used to mean "home page"; it left the sidebar with the living room, so a
house no longer collides with anything.

## Concepts weighed

- **house**: the universal "home", but a pictogram among objects; drafts and their redraws read as clip art.
- **cozyhouse**: the house with the kotatsu glowing in its window; the window is a blob at 72px.
- **two-storey house** (drawn by the image model from an empty slot): real form, but mostly plum and brown at 48px.
- **front door** ajar onto warm light: clean, but says "enter" and sits outside the set's colours.
- **kotatsu** (chosen): the living room's own centrepiece and an object like its neighbours, with the mikan the user
  loved in the room. Periwinkle quilt, pink plaid, tan board. Small mikan, no bowl, so it doesn't read as food next to
  the recipe book.
- Also considered and not drawn: keys, slippers at the door, an apartment block (reads as the city, i.e. Explore),
  a lamp, a mug.

## How it was made

1. `draft.py`: rough blockouts in the palette (they read as clip art, as expected).
2. `render.py`: the kotatsu modelled and lit (quilt draped from the board and flaring into corner folds, the plaid in
   the cloth's own coordinates, three mikan), rendered at 8x and quantized to the set's tone ramps:
   `out/kotatsu3d_render.png`, `out/kotatsu3d_recolor.png`.
3. `polish.py grid`: the quantized render placed in a 3x2 sheet beside five real icons at 8x; the image model
   (nano-banana-pro edit, with the render as a second reference) redrew it in the set's hand. `polish.py snap` reads it
   back to 48x48 in the frame palette with the set's outline. The redraws stay in `.scratch/home-icon/` (they contain
   the Windows icons).
4. `finish.py`: the chosen redraw (`fal3_draft_0`) finished by hand. The board is cleared to tan wood with a lit lip,
   and the three mikan are redrawn as outlined fruit, since at 48px they had run into a peach board.
   It writes `out/home_recolor.png` and `out/home.png`.

Installed as the site's `img/icons/home_recolor.png` (and `home.png`), linked from `templates/t_lsidebar.html`.
Spend: $2.40 on fal (16 images).
