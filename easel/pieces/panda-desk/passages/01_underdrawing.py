# 01 underdrawing: eye level and vanishing point, then the box of every object. Nothing on the canvas yet.
# Eye level above the desk (we look down on the desk top, the monitor top and the keyboard); one VP off to the right,
# so objects left of it show their right-hand sides.
VP = (250, -24)

def toward(p, t):
    """The point a fraction t of the way from p to the vanishing point (for receding edges)."""
    return (round(p[0] + (VP[0] - p[0]) * t), round(p[1] + (VP[1] - p[1]) * t))

ud.label(120, 2, 'VP ->', col='#ff4')
# window bottom rail, sill top/front, desk back edge, desk front edge and its thickness
GLASS_B, RAIL_B, SILL_F, SILL_B = 25, 28, 33, 35
DESK_BACK, DESK_FRONT, DESK_EDGE = 60, 101, 106
DESK_R = 140                                   # the desk's right end (front corner)
for y, col in ((GLASS_B, '#8af'), (SILL_F, '#8af'), (DESK_BACK, '#f84'), (DESK_FRONT, '#f84'), (DESK_EDGE, '#f84')):
    ud.line((0, y), (175, y), col)
ud.ray(VP, (DESK_R, DESK_FRONT), '#8f8')
# tower: front face and the side receding to the VP
TW = dict(l=2, r=29, t=6, b=82)
TW_SIDE_T, TW_SIDE_B = toward((TW['r'], TW['t']), 0.06), toward((TW['r'], TW['b']), 0.06)
ud.rect(TW['l'], TW['t'], TW['r'], TW['b'], '#4af')
# CRT: bezel front, screen inset, the body behind it (smaller: a CRT tapers), the stand
BZ = dict(l=44, r=115, t=12, b=70)
SC = dict(l=51, r=108, t=18, b=58)
BZ_TR_BACK, BZ_BR_BACK = toward((BZ['r'], BZ['t']), 0.13), toward((BZ['r'], BZ['b']), 0.13)
BZ_TL_BACK = toward((BZ['l'], BZ['t']), 0.04)
ud.rect(BZ['l'], BZ['t'], BZ['r'], BZ['b'], '#4af'); ud.rect(SC['l'], SC['t'], SC['r'], SC['b'], '#4ff')
for p in ((BZ['r'], BZ['t']), (BZ['r'], BZ['b']), (BZ['l'], BZ['t'])):
    ud.ray(VP, p, '#8f8')
# keyboard, newspaper, chair back
KB = [(62, 77), (126, 77), (133, 91), (57, 91)]
NP = [(6, 87), (60, 82), (70, 98), (12, 104)]
CH = [(142, 64), (175, 58), (175, 127), (148, 127)]
for q, lab in ((KB, 'kbd'), (NP, 'paper'), (CH, 'chair')):
    ud.poly(q, '#a6f'); ud.label(q[0][0] + 2, q[0][1] + 2, lab, '#a6f')
