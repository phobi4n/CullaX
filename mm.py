#!/usr/bin/python3

import colorsys


def closer(tmp, last, next):
    print(type(last))
    if tmp - last[0] > next[0] - tmp:
        return next
    else:
        return last


ct = []
q = colorsys.rgb_to_hsv(0.1, 0.9, 0.1)
l = [q[0], q[1], q[2], 'green']
ct.append(l)
q = colorsys.rgb_to_hsv(0.9, 0.1, 0.1)
l = [q[0], q[1], q[2], 'red']
ct.append(l)
q = colorsys.rgb_to_hsv(0.1, 0.1, 0.9)
l = [q[0], q[1], q[2], 'blue']
ct.append(l)
q = colorsys.rgb_to_hsv(0.1, 0.8, 0.9)
l = [q[0], q[1], q[2], 'cyan']
ct.append(l)

ct.sort()
print(ct)

t = 0.64
last = []
next = []
for i in ct:
    if t > i[0]:
        last = i
    else:
        next = i

print(last[0])
print(next[0])

print (closer(t, last, next))
