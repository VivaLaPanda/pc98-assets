"""Blind tests: can a judge who doesn't know which is which tell new art from the site's real art?

`pc98 blind OUT --real a.png b.png ... --new c.png d.png ...` writes, into OUT (give the judges only this folder):
- lineup_<i>.png: every icon, shuffled and numbered, at 4x and at the size the site shows it;
- pair_<a>_<j>.png: one new icon against one real one, sides shuffled, each judge seeing each new icon once;
and writes the answer key next to OUT (OUT.key.json), where a judge told to read only OUT won't look.

Run judges as separate agents (a model other than the one that drew the art, e.g. Sonnet), each told to read only
its own images and nothing else, with JUDGE_LINEUP / JUDGE_PAIRS below. Score against the key. Chance is 50% for
pairs; for lineups, compare each new icon's probability with the real ones'.
Caveat: famous source art (the Windows 98 icons) can be recognised from memory, which no drawing can beat.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

from .config import SIDEBAR_BG, ICON_SHOWN_PX, font

JUDGE_LINEUP = """You are a judge in a blind visual-authenticity test. Use the Read tool to view exactly one image: {path}.
Do not read, list or search any other file or directory, and do not run shell commands or web searches.
The image shows {n} small pixel-art icons, numbered, each enlarged 4x (top) and at the size shown on a website
(bottom). They are the navigation icons of a retro 1990s-style (Windows 98 / NEC PC-98 aesthetic) personal website.
Some are original assets that have been on the site for years; some were drawn recently to match them. The number
of recent ones could be anything from 0 to {n}. Look closely at outlines, dithering, shading and light direction,
palette, proportions, detail and pixel-level regularity. Reply with: each icon's probability (0-100%) of being
recent with one line of cues; your final list of recent ones; your confidence and the strongest tell."""

JUDGE_PAIRS = """You are a judge in a blind visual-authenticity test. Use the Read tool to view exactly these images and
nothing else: {paths}. Do not read, list or search any other file or directory, and do not run shell commands or
web searches. Each image shows two pixel-art icons, A and B, enlarged 4x (top) and at the size shown on a website
(bottom), from a retro 1990s-style (Windows 98 / NEC PC-98 aesthetic) personal website. In each pair exactly one is
an original asset that has been on the site for years and the other was drawn recently by an AI to match. For each
image: which (A or B) is the AI-drawn one, your confidence (50-100%), and the cues. Then the strongest tell overall."""


def _tiles(path, bg):
    im = Image.open(path).convert('RGBA')
    big = Image.new('RGBA', (im.width * 4, im.height * 4), bg + (255,))
    big.alpha_composite(im.resize(big.size, Image.NEAREST))
    w = ICON_SHOWN_PX
    h = round(im.height * w / im.width)
    sm = Image.new('RGBA', (w, h), bg + (255,))
    sm.alpha_composite(im.resize((w, h), Image.BILINEAR))
    return big.convert('RGB'), sm.convert('RGB')


def _strip(paths, labels, out, bg):
    cell = max(220, max(Image.open(p).width * 4 for p in paths) + 20)
    W, H = cell * len(paths), 40 + cell + 120
    o = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(o)
    for i, (p, lab) in enumerate(zip(paths, labels)):
        big, sm = _tiles(p, bg)
        x = i * cell
        d.text((x + cell // 2 - 6, 8), lab, fill=(0, 0, 0), font=font(24))
        o.paste(big, (x + (cell - big.width) // 2, 40 + (cell - big.height) // 2))
        o.paste(sm, (x + (cell - sm.width) // 2, 40 + cell + (100 - sm.height) // 2))
        d.line([(x, 0), (x, H)], fill=(0, 0, 0))
    o.save(out)


def make(out, real, new, seed=0, lineups=3, judges=3, bg=SIDEBAR_BG):
    """real, new: lists of image paths. Returns the key path."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    name = lambda p: Path(p).stem    # noqa: E731
    key = {}
    for t in range(lineups):
        items = [(name(p), p) for p in list(real) + list(new)]
        rng.shuffle(items)
        labs = [str(i + 1) for i in range(len(items))]
        _strip([p for _, p in items], labs, out / f'lineup_{t}.png', bg)
        key[f'lineup_{t}'] = {l: n for l, (n, _) in zip(labs, items)}
    for a in range(judges):
        rr = list(real)
        rng.shuffle(rr)
        for j, m in enumerate(new):
            pair = [(name(m), m), (name(rr[j % len(rr)]), rr[j % len(rr)])]
            rng.shuffle(pair)
            _strip([p for _, p in pair], ['A', 'B'], out / f'pair_{a}_{j}.png', bg)
            key[f'pair_{a}_{j}'] = {'A': pair[0][0], 'B': pair[1][0]}
    key['_new'] = [name(p) for p in new]
    kp = out.parent / f'{out.name}.key.json'
    kp.write_text(json.dumps(key, indent=1))
    return kp
