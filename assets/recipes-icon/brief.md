# recipes-icon

The sidebar nav icon for the recipes page (`/recipes.html`, "Panda's Recipe Book": buttermilk pancakes and katsudon).

## Where it lives

The user reshuffled the sidebar (2026-10-06): three rows of two at 72 px, the computer (index) icon dropped:
globe | envelope / CD | newspaper / **recipes** | home folder. So the icon sits bottom-left, beside the home folder
(`assets/room-icon/out3/homefolder2`, which the user called "epic"), under the CD. A four-row sidebar at 60 px was
planned first and dropped before anything shipped; everything here is judged at 72 px.

## Style

As `assets/room-icon` rounds 2-3 (`draw2.py`, `draw3.py`): drawn straight in the frame palette, periwinkle bodies,
plum shadow and lit-side outline, black shadow-side outline, white highlights, mauve half-light, light from the top
left, one mid tone plus the 50% checker, three-quarter volume. Food brings the palette's warm end (yellow, peach, tan,
rust), which the globe's stand already uses.

## Candidates (`out/<name>_recolor.png`, plus `<name>.png` for the img/icons pair convention), ranked

1. **book** (recommended): Panda's Recipe Book, a pink hardback with a hot-pink spine banded in yellow, a label with
   its title as type, a steaming donburi on the cover, white page edges, a yellow ribbon. It says what the page is
   ("Recipe Book") rather than one dish, and it's a paper object like its neighbours, the newspaper and the folder.
   Its pink balances the sidebar's periwinkle. The bowl on the cover is small: at 72 px it reads as "a hot dish", not
   as katsudon.
2. **pancakes**: a stack of four on a plate, a pat of butter, syrup running down in drips. The most legible food of the
   three, and a strong silhouette. But it says "pancakes / breakfast" rather than "recipes", and its peach-and-rust mass
   is the warmest, heaviest thing in the sidebar.
3. **donburi**: a periwinkle bowl with a pink band, katsu slices in egg on rice, chopsticks resting on the back rim,
   steam. Reads as "a bowl of food" and nicely Japanese, but more ramen than katsudon at 72 px, and it's the widest,
   flattest silhouette in the set.

Fixed along the way: the chopsticks first crossed the bowl as a thick striped band (twice: diagonal, then a gentle
slope that hid the food); they now rest on the back rim, 1 px lacquer with a lit edge and a shadow. The syrup drips
had plum bars beside them (they read as stripes); they're rust with a peach lit edge and a bead at the bottom. The
book's donburi was enlarged and its katsu redrawn as slices with a lit crust.

## Review

- `out/review/sheet_all.png`: the candidates beside the sidebar's five other icons, at 1x, 72 px and 6x.
- `out/review/rows_72px.png`: each candidate at the end of the sidebar's icons at 72 px.
- `out/review/sidebars.png`, `out/review/sidebar/desktop_<name>.png`: contact.html's real sidebar at 2x in the new
  layout, the candidate swapped in for `/img/icons/recipes_recolor.png` (`sidebar_shots.js`).

To install one: copy `out/<name>.png` and `out/<name>_recolor.png` to the site's `img/icons/recipes.png` and
`img/icons/recipes_recolor.png`.
