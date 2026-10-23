# panel-icons

Scene icons for the home panel (~/code/home-panel): a round 240x240 touchscreen (Waveshare ESP32-S3-Touch-LCD-1.28,
1.28 in, 0.135 mm per pixel) that applies one home scene per tap. The panel shows one big icon, the scene
a tap will apply, at 2x (96 px on screen, ~13 mm), and the panel's art is all on a 2x grid like the site's frame.

Ids come from home-mcp's scenes.toml (`icon` field); the panel looks icons up by id, `unknown` is the fallback.

| id | scene | when | drawn as |
|---|---|---|---|
| candle | Awake: all lights warmest 30 %, bedroom 10 %, blinds stay down | morning, lights all off | a lit candle on a saucer |
| mug | Slow morning: a gentler Up and at 'em, "like Chill time" for 5 am to sunrise + 1 h (scene in home-mcp) | morning | a steaming mug of coffee, a small sun printed on it |
| sunrise | Up and at 'em: all lights 5500 K 100 %, blinds up | morning | the sun half risen behind Mount Fuji's summit |
| door | Heading out | morning, day | a front door open onto daylight |
| bowl | Dinnertime: full warm light, The Sun at min, music 20 % | evening | the katsudon donburi (recipes-icon's runner-up) |
| moon | Chill time: warm and dim the lamps that are on | evening, night | a crescent moon and stars |
| futon | Bedtime: lights off, blinds down, kotatsu off, music off | night | a futon: big pillow, the kotatsu's plaid quilt, zzz |
| wait | connecting | boot | the Windows hourglass |
| offline | no Wi-Fi / home-mcp down | | an unplugged plug |
| unknown | an icon id the firmware doesn't have | | a ? tile |

Same conventions as the nav icons (README, "Nav icons"): 48x48, SITE letters, light from the top left, plum lit-side
outline and black shadow-side outline, one mid tone and the 50 % checker, white highlights, one accent per icon.
They sit on the panel's window: white by morning/day, #222233 by evening/night, so they must read on both:
`<name>_dark.png` turns the outer outline's black plum (black shadow-side edges dissolve on #222233).
No mint fields (it's the night frame's stripe colour).

Status (2026-10-16; mug added 2026-10-23): futon, sunrise and mug drawn through the home-icon flow; the other seven are still the first drafts,
drawn from primitives. Blind-read by two judges (below), not blind-tested against the site's icons.
- Website session's review of the drafts: candle, hourglass, plug and bowl read; futon read as a slab/cake, sunrise as
  a sun over a box. Panda: no blinds for Up and at 'em, "sunrise is better".
- Still to weigh: Chill time as a dimmed lamp (the moon is fine on the dark window).

## The futon and the sunrise, redone

Flow (as assets/home-icon): `render.py` (lit 3D model, quantized to the set's ramps, plum overlap lines) ->
`polish.py grid/fal` (nano-banana-pro edit: the draft beside the kotatsu, computer, globe, cd and recipe book at 8x,
the render as second reference) -> `polish.py snap --bits` (48x48, `out/redraw/`) -> finished by hand in `draw.py`.
Sheets and raw redraws (they contain the Windows icons) stay in `.scratch/panel-icons/`.

Concepts weighed:
- futon (chosen, `fal_r1_futon_0`): futon on the floor seen from the foot corner; big white pillow, white turned-down
  band, periwinkle quilt with the kotatsu's pink plaid over a sleeper. The lower camera of the drafts read as a slab;
  a higher three-quarter view and an oversized pillow fixed it.
  - `fal_r1_futon_1`: flatter, more "on the floor", but the pillow is small; weaker at 96 px.
  - Not drawn: folded futon (reads as storage), a sleeping panda on the pillow (cuter, but a character in a set of
    objects; Panda's call).
- sunrise (chosen, `fal_r2_fuji2_0`): the sun half risen behind Fuji's flat summit, centred, rays above. The cone and
  snow cap make it a place; it fills the square.
  - hills (`fal_r1_hills_*`): the dip between two hills pinched the sun into a light bulb.
  - sun beside Fuji's peak (`fal_r1_fuji_*`): reads, but half the square is empty.
  - shallow saddle, dome: not redrawn. Too flat at 48 px; a lumpy periwinkle hill under a sun reads as the
    "partly cloudy" weather icon.
  - sun over the sea: the draft's problem (a flat sea is a box).

Hand finish (draw.py):
- both: interior black to plum (the snap doubles outlines in places); black kept on the silhouette only.
- futon: zzz redrawn to rise small to big from the pillow, plain periwinkle (a plum shadow muddles 3 px glyphs); right
  drape pulled off the grid edge so dark() can turn it plum.
- sunrise: the model's ragged rays redrawn mirror-symmetric in 2 px runs; long rays yellow with a peach shadow edge
  (plain yellow is faint on the white window), short rays peach; white lit edge down Fuji's left slope.

Blind read (two Sonnet judges, round-screen mocks at 2x, new and old mixed, no context):
- new futon: "bed with a quilted blanket, pillow, zzz", 80 and 85 %; others: sleeping bag, folded blanket.
- old futon: 55 %; cake, hotel desk bell, boat.
- new sunrise: "sun rising behind Mt. Fuji", 75 and 85 %, guessed as morning/waking up; both also named "volcano".
- old sunrise: 80 and 85 % "sun over water"; one judge guessed sunset.

Open questions for Panda:
- Fuji for Up and at 'em? It reads as morning, but it is a specific place; the non-Fuji versions read worse.
- "Volcano" is the second reading of the sunrise. A fix if it bothers: raise the sun 2-3 px so more disc shows.

Spend: $1.20 on fal (8 nano-banana-pro images, ledger $2.40 -> $3.60; filed under "(other)" since the outputs live in
`.scratch/`). home-icon's $2.40 is not in ledger.csv: it went to ~/scratch-art/house/fal_ledger.csv.

## The mug (Slow morning), 2026-10-23

Panda: "up and at em is a bit too intense for 5am->(sunrise +1hr) - would be good to have a more chill morning option,
that's more like the 'chill time' option we use in the evening". It shows next to the candle (Awake) and the Fuji
sunrise (Up and at 'em), mostly on the light window.

Same flow as the futon and sunrise: `render.py mug mugsun mugtea` -> `polish.py fal` (r1_mug, r1_mugsun) ->
`polish.py snap --bits` -> `draw.py mug()`.

Concepts weighed:
- mug with a small sun printed on it (chosen, `fal_r1_mugsun_0`): the object reads first; the print is the hint of
  early light. Squat and wide with a handle, so its silhouette differs from the candle's pillar and the Fuji landscape.
- mug with a pink heart (`fal_r1_mug_*`): the strongest read (90 %), as "chill, cosy break, also morning coffee"; the
  sun mug reads as "morning coffee". Panda's call: heart says chill, sun says morning. Swapping is a few lines in
  `mug()` (the same snap, a 9x8 heart in k/h instead of `sun_print`).
- mug with a tea bag's tag (render only): at 48 px the tag is a pink box and the string vanishes; not sent to fal.
- Not drawn: a yunomi (no handle: reads as a cup or a can), a teapot (says "tea", not a slow start), slippers, a cat
  stretching (a character among objects), breakfast (food, next to the Dinnertime bowl), the sun through a window (a
  sun motif, and close to the blinds Panda turned down).

Hand finish (draw.py):
- interior black to plum, as the others.
- steam redrawn as three 2 px S-curves, white with a periwinkle shadow edge: plain white (the bowl's) vanishes on the
  light window and a mauve edge was faint there; periwinkle matches the futon's zzz.
- sun print redrawn: a 9 px yellow disc, white glint top left, peach shadow edge, eight 2 px rays, all yellow (peach
  rays were lost in the body's plum checker on the dark window).
- the model's scattered coffee glints replaced by one, in the tan highlight at the back left (toward the light).

Blind read (Sonnet judges, round-screen mocks at 2x, mixed with the other icons, no context):
- judge 1, light window: "blue mug of coffee or tea with steam and a sun emblem", 85 %; guessed "morning coffee,
  waking up". Candle and Fuji beside it read as candle (90 %) and sunrise (85 %).
- judge 2, dark window, peach rays: "mug of hot coffee with a sun on it", 80 %; also "a mug with a lamp or light bulb
  or yellow dot"; named it the weakest (the sun a dot at 13 mm). Fixed by the yellow rays.
- judge 2, heart variant, light window: "mug of hot coffee or cocoa with a heart", 90 %; "chill, relax, cozy break".
- judge 3, dark window, after the fix: "steaming mug of coffee or tea with a sun on it", 90 %; guessed "morning
  coffee, or a relaxing chill moment".
- Side finding: judge 3 read the door (Heading out) at 55 % (window, cabinet, wardrobe, fridge).

Spend: $0.60 on fal (4 nano-banana-pro images, ledger $3.60 -> $4.20, under "(other)"). Sheets and raw redraws in
`.scratch/panel-icons/`.
