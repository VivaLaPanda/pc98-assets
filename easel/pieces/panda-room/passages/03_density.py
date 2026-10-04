# 03 density: the strips' new lines and tiles take the room's 640->500 journey (see mahou-pc 09), so the moulding, the
# seams, the AC's lip, the leg, the cap and the plinth run as uneven as the picture they continue. Not the cone's
# bands (the journey only averages tile bands away) and not the old rows.
S = M['S']
pal = cv.pal.astype(float) * 17
rgb = Image.fromarray((pal[cv.idx]).astype(np.uint8))
big = rgb.resize((round(cv.w * S), round(cv.h * S)), Image.NEAREST)
back = np.asarray(big.resize((cv.w, cv.h), Image.BILINEAR)).astype(float)
snap = ((back[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
STRIPS = ~OLD & ~(NEW & FAN & cv.m_where(GLOW))
cv.idx[STRIPS] = snap[STRIPS]
