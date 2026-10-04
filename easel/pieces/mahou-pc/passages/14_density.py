# 14 density: the new objects' contours take the room's 640->500 journey too (see 09), so where they meet the picture
# their lines run uneven like its own. Only a ring a pixel either side of the plush's and the TV's silhouettes: run
# over whole objects, the journey took the panda's catchlights and the phone's bezel, which are what read at 1x.
# The phone and the butterfly are too small to give anything up.
pal = cv.pal.astype(float) * 17
rgb = Image.fromarray((pal[cv.idx]).astype(np.uint8))
big = rgb.resize((round(cv.w * S), round(cv.h * S)), Image.NEAREST)
back = np.asarray(big.resize((cv.w, cv.h), Image.BILINEAR)).astype(float)
snap = ((back[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
RING = np.zeros_like(PLUSH)
for m in (PLUSH, TV_BODY):
    RING |= cv.m_edge(m, inside=True) | cv.m_edge(m, inside=False)
cv.idx[RING] = snap[RING]
