# panel-icons

Scene icons for the home panel (~/code/home-panel): a round 240x240 touchscreen (Waveshare ESP32-S3-Touch-LCD-1.28,
1.28 in, 0.135 mm per pixel) that applies one home scene per tap. The panel shows one big icon, the scene
a tap will apply, at 2x (96 px on screen, ~13 mm), and the panel's art is all on a 2x grid like the site's frame.

Ids come from home-mcp's scenes.toml (`icon` field); the panel looks icons up by id, `unknown` is the fallback.

| id | scene | when | drawn as |
|---|---|---|---|
| candle | Awake: all lights warmest 30 %, bedroom 10 %, blinds stay down | morning, lights all off | a lit candle on a saucer |
| sunrise | Up and at 'em: all lights 5500 K 100 %, blinds up | morning | the sun over the horizon |
| door | Heading out | morning, day | a front door open onto daylight |
| bowl | Dinnertime: full warm light, The Sun at min, music 20 % | evening | the katsudon donburi (recipes-icon's runner-up) |
| moon | Chill time: warm and dim the lamps that are on | evening, night | a crescent moon and stars |
| futon | Bedtime: lights off, blinds down, kotatsu off, music off | night | a futon with a pillow, zzz |
| wait | connecting | boot | the Windows hourglass |
| offline | no Wi-Fi / home-mcp down | | an unplugged plug |
| unknown | an icon id the firmware doesn't have | | a ? tile |

Same conventions as the nav icons (README, "Nav icons"): 48x48, SITE letters, light from the top left, plum lit-side
outline and black shadow-side outline, one mid tone and the 50 % checker, white highlights, one accent per icon.
They sit on the panel's window: white by morning/day, #222233 by evening/night, so they must read on both:
`<name>_dark.png` turns the outer outline's black plum (black shadow-side edges dissolve on #222233).
No mint fields (it's the night frame's stripe colour).

Status (2026-10-16): drafts for the first mockup, drawn from primitives; not blind-tested.
- Reviewed by the website session: candle, hourglass, plug and bowl read; futon reads as a slab/cake, sunrise as a sun
  over a box. Redo those through the home-icon flow (render -> quantize -> polish beside real icons -> snap + finish).
- Concepts to weigh: "Up and at 'em" as blinds rolling up onto morning light (what the scene does) instead of a
  sunrise symbol; Chill time as a dimmed lamp (the moon is fine on the dark window).
