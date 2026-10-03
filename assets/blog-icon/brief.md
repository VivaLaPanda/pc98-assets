# blog-icon

The sidebar nav icon for the blog, "Panda's Manifestos" (a Substack newsletter, shown at `/blog/`).

## Where it lives

The left sidebar's grid of nav icons (`templates/t_lsidebar.html`, `.nav-row` in `css/style.css`): bottom-left
slot of a third row, under the envelope (contact) and beside an empty slot. The site's file name is
`img/icons/blog_recolor.png` (placeholder at the time of writing: Windows 98's satellite dish, not recoloured).

## What it must sit next to

`computer`, `cd_audio`, `envelope_closed`, `globe_map`: Windows 98 icons (48x48 except the 32x32 envelope), moved
into the frame's PC-98 palette by hand. What they share, measured from the files:
- **Size:** a 48x48 canvas filled almost edge to edge, shown 72 px wide (1.5x), smooth-scaled by Chrome.
- **Outline:** 1 px. Black on the shadow side (bottom, right), a mid tone on the lit side (grey in the originals, plum
  `#664477` in the recolours). Interior lines are the dark tone, not black.
- **Shading:** light from the top left; white highlights; one mid tone plus a 50% checkerboard between tones. No
  gradients, no anti-aliasing.
- **Palette (recolour):** periwinkle `#8899ff` is the body colour of every icon; plum `#664477` shadow; white
  highlights; accents from pink `#ffaabb`, hot pink `#ff0066`, yellow `#ffee55`, peach `#ffaa77`, tan `#cc8844`.
  Mint `#00eebb` is the sidebar itself, so it appears only as small accents.
- **View:** a slight three-quarter view for solid objects (computer, globe), flat for flat ones (envelope).

## Reading it

At 72 px, beside four objects that are each one silhouette: the blog icon has to be one recognisable thing too, read
in a glance. "Manifesto" suggests a proclamation; "newsletter" suggests print. Candidates: a newspaper, a scroll
(manifesto) with a seal, a quill and paper.

## Candidates (out/, each as `<name>.png` original + `<name>_recolor.png`)

1. **newspaper** (recommended): a front page over a second sheet, masthead with its title knocked out, headline,
   a portrait photo, columns, the bottom corner curling. Square to the frame like the envelope. Reads as "news" at a
   glance and sits with the envelope as a pair of paper things.
2. **scroll**: a manifesto, rolled top and bottom, a two-word title, two paragraphs, a signature, a hot-pink wax seal
   with notched ribbons. The most literal "Manifestos", and the most personality.
3. **quill**: a letter, a white-and-pink feather and a plum-glass ink bottle. Reads as "writing" more than "blog".

Review: `out/review/contact_sheet.png` (recolours beside the site's four, the live sidebar at 2x for each, and the
Windows 98 originals); `out/review/<name>/context.png` is the whole contact page with that candidate in place.
To install one: copy `out/<name>.png` and `out/<name>_recolor.png` to the site's `img/icons/` as `blog.png` and
`blog_recolor.png` (the sidebar uses `/img/icons/blog_recolor.png`).

## Blind test (Sonnet judges, each seeing only its own images; `pc98 blind`)

Four rounds, 16 judges. Pairs: one new icon against one real one, "which is AI-drawn?" (chance 50%).

| | caught in pairs | 7-icon lineups: mean "recent" probability, 9 judges |
|---|---|---|
| newspaper | 1 / 9 | 35% |
| scroll | 9 / 12 | 37% |
| quill | 9 / 12 | 45% (across its versions; 37% for the last) |
| the site's real four | | 39% (envelope 68%, CD 38%, globe 31%, computer 17%) |

In lineups, 9 of 10 judges (including one on the Windows 98 originals) named the *real* envelope as the likeliest
new icon; nothing new stands out among the set. Head to head, the newspaper is taken for the original 8 times in 9. The scroll and quill are caught for
being "more ornate / narrative" (ribbons, seal, quill and bottle) than Windows 98's single bold objects: a
design-level tell, not a pixel one. Rounds 1-2 also named fixable tells, and they were fixed: a saturated cobalt ink
bottle (now plum glass, black ink), squiggled handwriting ("a typical AI approximation of writing": now type
lines, the Windows 98 convention), evenly spaced bars (now words with gaps and indents), flat fills (stepped dither on
the rolls and page edges).

## Notes

- **Dropped:** a tilted newspaper (drawn flat, then `Grid.skew()`ed 1:4). Every edge and text line became a
  staircase and it looked busier than any of the originals.
- **Paper goes periwinkle** in the recolour, as the user's own envelope recolour did; tried white paper in context
  first: it read as a hole in the set.
- References: `refs/sheet.jpg` (6 Nano Banana Pro edits with `refs/style_win98_icons.png` as style, $0.90). Used
  for composition only; traces are in `refs/trace/` (gitignored). No generated pixels are in the icons.
