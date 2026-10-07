# 09 the letter (email): an envelope standing on the back of the desk, leaned against the wall beside the monitor,
# its flap toward us, sealed with a heart. The room's paper ink with a black edge so it parts from the lit wall
# behind; its right edge takes the CRT's light, its left throws a 1px shadow on the wall.
LT_X, LT_Y = 349, 161
LT_ART = '''
KKKKKKKKKKKKKKKKKKK
KVPPPPPPPPPPPPPPPVK
KPVPPPPPPPPPPPPPVPK
KPPVPPPPPPPPPPPVPPK
KPPPVPPPPPPPPPVPPPK
KPPPPVPPRPRPPVPPPPK
KPPPPPVHRRRRVPPPPPK
KPPPPPPVRRRVPPPPPPK
KPPPPPPPVRVPPPPPPPK
KPPPPPPPPVPPPPPPPPK
KPPPPPPPPPPPPPPPPPK
KKKKKKKKKKKKKKKKKKK
'''
cv.line(LT_X - 1, LT_Y + 1, LT_X - 1, LT_Y + 11, DARK)
cv.stamp(LT_X, LT_Y, LT_ART, {'K': BLACK, 'P': PAPER, 'V': WALL, 'R': RED, 'H': DESK_SHADE})
for _y in range(LT_Y + 2, LT_Y + 11):                               # the CRT's side
    if cv.idx[_y, LT_X + 17] == PAPER:
        cv.dot(LT_X + 17, _y, GLOW)
cv.dots([(LT_X + 15, LT_Y + 9), (LT_X + 14, LT_Y + 10)], GLOW)
LETTER = cv.m_rect(LT_X, LT_Y, LT_X + 18, LT_Y + 11)
cv.masks['letter'] = LETTER

# vp-check: an envelope standing against the back wall is frontal: level and plumb
cv.persp.edge('letter', (LT_X + 1, LT_Y), (LT_X + 17, LT_Y), 'h')
cv.persp.edge('letter', (LT_X, LT_Y + 1), (LT_X, LT_Y + 10), 'v')
cv.persp.edge('letter', (LT_X + 18, LT_Y + 1), (LT_X + 18, LT_Y + 10), 'v')
cv.persp.edge('letter', (LT_X + 1, LT_Y + 11), (LT_X + 17, LT_Y + 11), 'h')
