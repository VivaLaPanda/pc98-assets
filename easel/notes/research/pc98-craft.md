# How PC-98 graphics staff made backgrounds (research notes, Oct 2026)

Sources are cited inline. Where the web is thin, the strongest evidence is the site's own genuine PC-98 pictures
(`~/git/vivalapanda.moe/img/explore/places/`), measured and studied at 3-4x (see "Measured" below).

## The machine and the tools

- **16 colours on screen from 4096** (4 bits per channel), 640x400. Gradations can't be reproduced with 16
  colours, so tile patterns (タイルパターン) were used for pseudo intermediate colours.
  [pixiv 16色](https://dic.pixiv.net/a/16%E8%89%B2) (via search summary), [PC-98 Color Space Parser](https://madsonweb.itch.io/pc-98-color-space-parser)
- **The GRCG tile register** writes an 8-pixel pattern per bitplane in one go (TDW and RMW modes), so patterned
  fills were cheap and screen-aligned: a fill's pattern is anchored to screen pixels, not to the shape.
  [rec98, 2020-12-18](https://rec98.nmlgc.net/blog/2020-12-18); [PC-9801小手先技巧講座](https://mzisland.com/club/98koza/index.html)
  ("CPUがライトしたデータを無視して、予め設定しておいたタイルパターンを4画面同時に書き込む" — the preset tile pattern is
  written to all four planes at once).
- **Paint programs**: Z's STAFF Kid98 (Zeit) and マルチペイント were the standard PC-98 tools. They let you build
  intermediate colours (skin tones) and screentone-like patterns within 16 colours, had a loupe (3 zoom levels) for
  dot-by-dot work, and arc/circle tools. [ドット絵の時代２](https://ameblo.jp/mugenkai/entry-10678173861.html),
  [weblio: Zeit](https://www.weblio.jp/content/zeit)
- **Workflow**: pencil sketch on paper, tidied, scanned, then traced on a layer above (some artists traced with a
  mouse before owning a tablet). [search summary of an artist's account; see pixelglade below]
- **Tile painting is "Japan's own tradition"** carried from the 8-colour PC-88/X1/FM-7 era (640x200, where
  arranging red/green etc. at intervals made skin tones) into the PC-9801; Doukyuusei 2 is called the peak of
  tile-heavy PC-98 bishoujo CG. [サイボーグMSX](https://note.com/cyborgmsx/n/n4c34d79a575c)
- On 8-colour machines skin was pink/white checker; Snatcher's artist describes building colours by laying
  different colours in a 市松 (checkerboard) and enjoying the trial and error. [Togetter](https://togetter.com/li/2091849)
- **Overlapping patterns** can create new moiré patterns; artists used this deliberately. These images were made for
  a fixed display; scaling them changes them. [posfie](https://posfie.com/@highcampus/p/GlaFktV)
- **What distinguishes PC-98 (vs PC-88) art**: anime styling, thick outlines, saturated colours; backgrounds are lower
  contrast than characters; colours are shared between foreground and background; scenes are information-dense;
  small objects carry no readable labels. [Pixel Glade](https://pixelglade.net.au/blog/posts/2025-08-31-Whats-unique-about-PC98-art.html)

## Measured on the site's genuine PC-98 interiors (easel/metrics.py)

| | thinline | edge | checker | flat | black |
|---|---|---|---|---|---|
| night_musician_bedroom | .21 | .75 | .32 | .13 | .25 |
| commandcenter (night) | .13 | .57 | .08 | .22 | .44 |
| bedroom | .10 | .60 | .07 | .21 | .11 |
| day_bedroom | .15 | .46 | .22 | .46 | .10 |
| conbini | .10 | .70 | .24 | .20 | .12 |
| **our rejected room art** | **.02** | **.37** | **.05** | **.47** | .16 |

The rejected art had 4-8x too little line art, half the detail density, too little tile work and too much flat.

## Palettes of night scenes

- night_musician_bedroom (14): black 25%, slate #666677 19%, lavender #bbbbdd 18%, a peach/pink ramp
  (#aa7766 #eeaa99 #ffccbb #ffeedd), white 6%, single accents (#ee5555, #66aa77, #7766dd, #ffdd55).
- commandcenter (15): black 44%, a 5-step grey ramp (#333 #555 #777 #999 #bbcccc), tiny warm and green accents.
- city_overlook (16): black 66%, warm lamp ramp (#734242 #bd5221 #ef8c73 #ffad00 #ffbd9c #ffdebd), cool ramp
  (#106342 #52bd73 / #5263bd #adbdff), white for the lamp.
- night_home_front (13): black 60%, navy #223355 30%, warm window ramp (#aa5544 #dd7744 #ffcc66 #ffccbb).
Pattern: black dominates; one dark mid ramp carries the room; light lives in one warm ramp (and/or one cool);
single-pixel accents; white only at light sources and speculars.

## Seen at 3-4x (the craft)

- **Line art**: 1px, unbroken around every object; black on machines, the darkest colour of the material's own ramp
  on furniture (maroon on pink wood, dark grey-green on walls). Internal edges (panel seams, bevels, slots) are 1px
  lines too.
- **Bevels**: a 1px light line along the top/front edge of boxes and panels; a dark 1px line along the bottom.
- **Surfaces**: 2-3 flat tones per surface with banded tiles between neighbours of a ramp; recesses as black over a
  dark tone in 1/2 checker, then solid black at the deepest point.
- **Micro-detail**: LEDs (1 coloured pixel + 1 white), knobs (2-3px with a highlight dot), labels as 1-2px clusters,
  slots, grilles as line tiles, cables as curves with a 1px highlight.
- **Light**: the source is a hard-edged flat of the brightest colour; the glow is concentric bands of tiles
  (solid ring, 1/2, 1/4, 1/8) stepping outward over the surrounding surfaces; edges facing the light catch a 1px rim
  of light colour. Lit windows at night are flat warm blocks cut by dark silhouettes.
- **CRT screens**: bright face with a darker bevel strip just inside the bezel, glare as a stepped curved shape in one
  corner; on a dark screen, content is drawn as simple light line graphics.
