# The PC-98 cover filter: style guide, lint and test harness

These are the research and tooling behind `js/pc98.js` in the site repo
(`VivaLaPanda/vivalapanda.moe`), which turns blog cover images into PC-98-style art in the browser. The filter
itself lives there. This folder holds what it took to build it.

| file | what it is |
|---|---|
| `PC98_STYLE_GUIDE.md` | What makes art read as PC-98: palette, shapes, dithering, line art and resolution, measured from the site's ~100 genuine images, plus what gave fakes away in blind tests. **Read this before making any PC-98 asset.** |
| `pc98lint.py` | Measures an image against the guide's countable rules (colours on the 12-bit grid, flat-pixel share, dither patterns, ramp pairs). `uv run python filter/pc98lint.py IMG...` |
| `run.js`, `pngio.js` | Node harness: renders a test set through `pc98.js` (from `../vivalapanda.moe/js/pc98.js`, or set `PC98=`). Output matches the browser byte for byte. `node filter/run.js OUTDIR '{"width":240}'` |
| `results/` | Original / filtered / real PC-98 art side by side, and the blog page with the filter on (Oct 3, 2026). |

The test images aren't included: the blog covers come from the Substack feed (`<enclosure url>` of each item in
https://vlpanda.substack.com/feed) and some are third-party photos. Put them in `filter/covers/` to run the harness.

**How it was judged.** Fresh model judges each saw only their own pair: real PC-98 art beside filter output, at the
same scale, sides randomised. Photos were caught almost every time (34 of 36), on blobby regions following photo
texture, garbled signs and photographic lighting. Flat illustrations passed. Redrawing a photo with an image model
first, then running the illustration preset, did much better (7 of 8) but needs a human check every time. The guide
recommends that route for hero and explore art, and the plain filter for thumbnails.
