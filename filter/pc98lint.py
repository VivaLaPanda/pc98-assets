# pc98lint.py: check an image against the measurable PC-98 rules in PC98_STYLE_GUIDE.md
#   uv run --with pillow --with numpy python pc98lint.py img1.png [img2.png ...]
# Reports: colour count, 4096-grid compliance, black/white present, flat / checker / dot shares,
# mean contrast of dithered pairs (OKLab), and the share of 2-colour 4x4 blocks at each tile level.
import sys, collections
import numpy as np
from PIL import Image

def oklab(rgb):
    c = rgb / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(lin @ M1.T) @ M2.T

def lint(path):
    a = np.array(Image.open(path).convert('RGB')).astype(np.int64)
    h, w, _ = a.shape
    k = a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]
    cols = collections.Counter(k.ravel().tolist())
    on_grid = sum(1 for c in cols if all(((c >> s) & 255) % 17 == 0 for s in (16, 8, 0)))
    c = k[1:-1, 1:-1]; L = k[1:-1, :-2]; R = k[1:-1, 2:]; U = k[:-2, 1:-1]; D = k[2:, 1:-1]
    flat = ((c == L) & (c == R) & (c == U) & (c == D)).mean()
    checker = ((L == R) & (U == D) & (L == U) & (c != L)).mean()
    m = (L == R) & (U == D) & (L == U) & (c != L)
    pairs = np.stack([c[m], L[m]], -1)
    if len(pairs):
        rgb = np.stack([(pairs >> 16) & 255, (pairs >> 8) & 255, pairs & 255], -1).astype(float)
        lab = oklab(rgb)
        pair_de = np.linalg.norm(lab[:, 0] - lab[:, 1], axis=-1).mean()
    else:
        pair_de = 0
    lv = collections.Counter()
    for y in range(0, h - 3, 4):
        for x in range(0, w - 3, 4):
            blk = collections.Counter(k[y:y + 4, x:x + 4].ravel().tolist())
            if len(blk) == 1: lv['flat'] += 1
            elif len(blk) == 2: lv[f'{min(blk.values())}/16'] += 1
            else: lv['3+'] += 1
    tot = sum(lv.values())
    has_black = 0 in cols
    has_white = 0xffffff in cols
    print(f"{path}\n  {w}x{h}  colours={len(cols)} (rule <=16)  on4096grid={on_grid}/{len(cols)}  black={has_black} white={has_white}")
    print(f"  flat px={flat:.2f}  checker/dot px={checker:.3f}  mean dither-pair dE={pair_de:.3f} (refs ~0.10-0.20)")
    print('  4x4 blocks: ' + ' '.join(f"{kk}:{v * 100 / tot:.0f}%" for kk, v in sorted(lv.items())))

for p in sys.argv[1:]:
    lint(p)
