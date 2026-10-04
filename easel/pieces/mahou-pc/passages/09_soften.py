# 09 density: the room is a 640-wide PC-98 picture resampled to 500 (its calendar's date squares run 1,2,1,1,3,3,3
# pixels wide; its wall dither beats every ~9px). Freshly painted 1px lines and clean tiles are crisper than that,
# which is the tell at 3x. So the painted pixels go through the same journey: up to 640 by nearest neighbour, back to
# 500 by bilinear, each snapped to the nearest of the 16 inks. Lines come out of uneven width with off-ramp inks at
# their edges, and tiles beat like the room's own dithers. Only the desk corner: the tell is the new line art; the
# floor's cone and the stool's light are tile bands, which the resampling would only average away.
S = 640 / 500
grown = cv.idx != cv.base
for _ in range(1):                                       # and a pixel around, so new meets old the same way
    g = grown.copy()
    g[1:] |= grown[:-1]; g[:-1] |= grown[1:]; g[:, 1:] |= grown[:, :-1]; g[:, :-1] |= grown[:, 1:]
    grown = g
pal = cv.pal.astype(float) * 17
rgb = Image.fromarray((pal[cv.idx]).astype(np.uint8))
big = rgb.resize((round(cv.w * S), round(cv.h * S)), Image.NEAREST)
back = np.asarray(big.resize((cv.w, cv.h), Image.BILINEAR)).astype(float)
snap = ((back[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
grown &= cv.m_rect(330, 28, 440, 160)
cv.idx[grown] = snap[grown]
