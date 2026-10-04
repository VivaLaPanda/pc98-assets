# 01 underdrawing: the room's own perspective, then the box of every new object. Nothing on the canvas yet.
# One-point room: the desk's receding left edge (345,137)->(378,157) and the floor lines meet at VP, eye level y 80.
VP = (250, 80)

def toward(p, f):
    """The point a fraction f of the way from p to the vanishing point (what recedes into the room)."""
    return (round(p[0] + (VP[0] - p[0]) * f), round(p[1] + (VP[1] - p[1]) * f))

def back(p, y):
    """Slide p back along its line to VP until it reaches height y (on a horizontal plane below eye level)."""
    f = (p[1] - y) / (p[1] - VP[1])
    return (round(p[0] + (VP[0] - p[0]) * f), y)

DESK_BACK_Y, DESK_FRONT_Y = 137, 157            # desk top meets the wall / its front edge
ud.ray(VP, (378, 157), '#8f8'); ud.ray(VP, (432, 157), '#8f8')
ud.line((330, DESK_BACK_Y), (440, DESK_BACK_Y), '#f84'); ud.line((370, DESK_FRONT_Y), (440, DESK_FRONT_Y), '#f84')
ud.label(252, 82, 'VP', col='#ff4')

# the PC-98 style desktop case on the desk's back right, the CRT standing on it
CASE = dict(l=388, r=431, t=132, b=143)          # front face
CASE_BL, CASE_TL = back((CASE['l'], CASE['b']), DESK_BACK_Y), None
f_case = (CASE['b'] - DESK_BACK_Y) / (CASE['b'] - VP[1])
CASE_TL = toward((CASE['l'], CASE['t']), f_case)
CASE_TR = toward((CASE['r'], CASE['t']), f_case)
ud.rect(CASE['l'], CASE['t'], CASE['r'], CASE['b'], '#4af')
ud.poly([(CASE['l'], CASE['t']), CASE_TL, CASE_TR, (CASE['r'], CASE['t'])], '#4af')
ud.poly([(CASE['l'], CASE['t']), CASE_TL, CASE_BL, (CASE['l'], CASE['b'])], '#4af')

BZ = dict(l=391, r=428, t=97, b=129)             # CRT bezel (front)
GL = dict(l=397, r=422, t=102, b=119)            # the glass
RC = dict(l=395, r=424, t=100, b=121)             # the recess the glass sits in
f_crt = 0.12                                     # the tube housing's depth, back to the wall, tapering
CRT_TLB = toward((BZ['l'] + 3, BZ['t'] + 2), f_crt)
CRT_BLB = toward((BZ['l'] + 3, BZ['b'] - 6), f_crt)
CRT_TRB = toward((BZ['r'] - 4, BZ['t'] + 2), f_crt)
ud.rect(BZ['l'], BZ['t'], BZ['r'], BZ['b'], '#4af'); ud.rect(GL['l'], GL['t'], GL['r'], GL['b'], '#4ff')
for p in ((BZ['l'], BZ['t']), (BZ['l'], BZ['b']), (BZ['r'], BZ['t'])):
    ud.ray(VP, p, '#8f8')

# keyboard on the desk in front of the case: front edge, back edge slid toward VP
KB_F = (391, 429, 153)                           # x0, x1, y of the front edge
KB_BL, KB_BR = back((KB_F[0], KB_F[2]), 146), back((KB_F[1], KB_F[2]), 146)
KB = [KB_BL, KB_BR, (KB_F[1], KB_F[2]), (KB_F[0], KB_F[2])]
# newspaper on the desk's left, folded, a little askew to the desk's axes
NP = [(350, 139), (374, 137), (389, 151), (373, 154)]
for q, lab in ((KB, 'kbd'), (NP, 'paper')):
    ud.poly(q, '#a6f'); ud.label(q[0][0], q[0][1] - 8, lab, '#a6f')
# the light: the glass is the source; it throws forward and down onto the desk, keyboard, paper and stool
LIGHT = ((GL['l'] + GL['r']) / 2, (GL['t'] + GL['b']) / 2)
ud.cross(*map(int, LIGHT), '#ff4')
