# 02 re-ink into the house's materials. Both rooms share one set of 16 registers (the bedroom's: its day inks, its
# night as Panda's Room has it), so the living room is painted in them: olive walls in the bedroom's own checker, its
# salmon moulding, its desk's honey wood for the floor and the furniture, its pale-blue curtains. Fermion's inks are
# mapped region by region (a cream on a wall is wall; the same cream on a door's glass is glass), so every dither and
# ramp the artist drew survives, only its colours change.
F = {h: i for i, h in enumerate(pal16)}               # Fermion's inks by colour
HOUSE = ['#fff', '#fca', '#cde', '#cff', '#bcd', '#e92', '#aa9', '#897', '#c77', '#743', '#46d', '#557', '#c14',
         '#344', '#fff', '#111']
HOUSE_NAMES = dict(paper=0, desk=1, curtain=2, screen=3, glow=4, bedspread=5, wall=6, wall_shade=7, desk_shade=8,
                   wood=9, floor=10, slate=11, red=12, dark=13, white=14, black=15)
src = cv.idx.copy()                                   # Fermion indices
new = np.full(src.shape, 255, np.uint8)               # house indices; 255 = not yet decided
H = HOUSE_NAMES


def remap(mask, table, default=None):
    """Within mask, Fermion ink (by hex) -> house ink (by name). Inks not in the table keep `default` (a name) or
    stay undecided."""
    for hx, name in table.items():
        sel = mask & (src == F[hx]) & (new == 255)
        new[sel] = H[name]
    if default is not None:
        sel = mask & (new == 255)
        new[sel] = H[default]


objects = np.zeros(src.shape, bool)
for m in OBJ.values():
    objects |= m

WALL_T = {'#fec': 'wall', '#eda': 'wall', '#db9': 'wall_shade', '#b98': 'wall_shade', '#a86': 'wall_shade',
          '#dcd': 'wall', '#fff': 'wall'}
remap(REGION['back'] & ~objects, WALL_T)
remap(REGION['left'] & ~objects, {'#fec': 'wall', '#eda': 'wall', '#db9': 'wall_shade', '#b98': 'wall_shade'})
remap(REGION['right_upper'] & ~objects, {'#a86': 'wall_shade', '#b98': 'wall', '#db9': 'wall', '#865': 'wood',
                                         '#655': 'wood', '#444': 'dark', '#787': 'wall_shade'})
# the ceiling: olive a step under the walls, its fret band and the coffer's lit edges in the bedroom's salmon
CEIL_T = {'#9a8': 'wall', '#787': 'wall_shade', '#bba': 'desk', '#dcd': 'desk', '#eda': 'desk', '#db9': 'desk_shade',
          '#fec': 'paper', '#fff': 'paper', '#a86': 'desk_shade', '#b98': 'desk', '#865': 'wood', '#655': 'wood',
          '#444': 'dark', '#333': 'dark', '#222': 'black', '#000': 'black'}
remap(REGION['ceil'] & ~OBJ['ac'], CEIL_T)
# woodwork (doors, sideboard, the vent's cabinet, the TV's stand): the bedroom desk's ramp
WOOD_T = {'#655': 'wood', '#865': 'wood', '#a86': 'desk_shade', '#b98': 'desk_shade', '#db9': 'desk', '#eda': 'desk',
          '#fec': 'paper', '#fff': 'paper', '#444': 'dark', '#333': 'dark', '#222': 'black', '#000': 'black',
          '#787': 'slate', '#9a8': 'wall', '#bba': 'curtain', '#dcd': 'curtain'}
for k in ('glass_door', 'left_door', 'sideboard', 'vent'):
    remap(OBJ[k], WOOD_T)
# the clock and the light switch: their own pixels in wood and paper, the wall around them as wall
CLOCK_FACE = cv.m_ellipse(220, 108, 15, 16)
remap(OBJ['clock'] & CLOCK_FACE, WOOD_T)
remap(OBJ['clock'] & ~CLOCK_FACE, WALL_T)
SWITCH_PLATE = cv.m_rect(135, 151, 139, 161)
remap(OBJ['switch'] & SWITCH_PLATE, {'#fff': 'paper', '#fec': 'paper', '#eda': 'desk', '#db9': 'desk_shade'})
remap(OBJ['switch'] & ~SWITCH_PLATE, WALL_T)
# the TV: dark plastic; its screen is repainted later
remap(OBJ['tv'], {'#000': 'black', '#222': 'black', '#333': 'dark', '#444': 'dark', '#655': 'wood', '#865': 'wood',
                  '#787': 'slate', '#9a8': 'slate', '#bba': 'glow', '#dcd': 'glow', '#fff': 'paper', '#fec': 'paper',
                  '#eda': 'desk', '#db9': 'desk', '#a86': 'desk_shade', '#b98': 'desk_shade'})
# the AC: white plastic, cool shadows
remap(OBJ['ac'], {'#dcd': 'paper', '#fff': 'paper', '#bba': 'curtain', '#9a8': 'glow', '#787': 'slate', '#655': 'dark',
                  '#865': 'slate', '#b98': 'curtain', '#a86': 'slate', '#444': 'dark', '#333': 'dark', '#fec': 'paper',
                  '#eda': 'paper', '#db9': 'curtain', '#222': 'black', '#000': 'black'})
# everything else for now: a neutral pass so the picture is in house inks (the foreground is cleared in 03)
REST_T = {'#fff': 'paper', '#fec': 'paper', '#eda': 'desk', '#dcd': 'curtain', '#db9': 'desk', '#bba': 'curtain',
          '#b98': 'desk_shade', '#9a8': 'wall', '#a86': 'desk_shade', '#787': 'wall_shade', '#865': 'wood',
          '#655': 'wood', '#444': 'dark', '#333': 'dark', '#222': 'black', '#000': 'black'}
remap(np.ones(src.shape, bool), REST_T)
assert (new != 255).all()
cv.start_from(new, HOUSE, dict(HOUSE_NAMES))
globals().update({k.upper(): v for k, v in HOUSE_NAMES.items()})
