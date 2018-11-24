#!/usr/bin/python3

import sys
import colorsys

hex_color = sys.argv[1].strip('#')
split_color = ['0x{}'.format(hex_color[i:i+2]) for i in (0,2,4)]
float_color = [format(int(i, 16) / 0xff, '.3f') for i in split_color]
float_color = [float(i) for i in float_color]
hsv_color = [colorsys.rgb_to_hsv(float_color[0], float_color[1], float_color[2])]
hsv_color = [format(float(i), '.3f') for i in hsv_color[0]]
print (hsv_color)
