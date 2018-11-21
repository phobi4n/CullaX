#!/usr/bin/python3
"""Culla generates a desktop theme using colours
from the current wallpaper"""

import sys
import random
import os
import subprocess
import time
import colorsys
from collections import namedtuple
from math import sqrt
import dbus

if sys.version_info[1] < 6:
    print("Culla requires Python 3.6 or later.")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    sys.exit("Python Pillow is required.")

try:
    from colorthief import ColorThief
except:
    sys.exit("Python ColorThief is required.")


#Colours for our Plasma theme
plasma_colors = """[Colors:Window]
ForegroundNormal=bbb
BackgroundNormal=aaa

[Colors:Selection]
BackgroundNormal=eee

[Colors:Button]
ForegroundNormal=248,248,248
BackgroundNormal=fff
DecorationFocus=eee
DecorationHover=ggg

[Colors:Compilmentary]
BackgroundNormal=4,4,222

[Colors:View]
BackgroundNormal=ccc
ForegroundNormal=242,242,242
DecorationHover=ddd"""


#------ Culla Functions ------------------------------------------------
def color_triplet(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    if r > 1.0:
        r = 1.0
    r = int(r * 255)

    if g > 1.0:
        g = 1.0
    g = int(g * 255)

    if b > 1.0:
        r = 1.0
    b = int(b * 255)

    return ','.join([str(r), str(g), str(b)])


def aurorae(rgb):
    """Open decoration template, substitue our colour
    then write decoration.svg"""

    try:
        with open(os.path.expanduser \
            ('~/.local/share/aurorae/themes/CullaX/decoration-template.svg')) \
            as f:
            auroraetemplate = f.read()
    except IOError:
        fatal("Unable to find Aurorae template.")

    r, g, b = rgb.split(',')
    hex_colour = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
    auroraetemplate = auroraetemplate.replace('TEMPLAT', hex_colour)

    try:
        with open(os.path.expanduser \
            ('~/.local/share/aurorae/themes/CullaX/decoration.svg'), 'w') as f:
            f.write(auroraetemplate)
    except IOError:
        fatal("Fatal. Unable to write aurorae decoration.")


    session_bus = dbus.SessionBus()

    if [k for k in session_bus.list_names() if 'KWin' in k]:
        proxy = session_bus.get_object('org.kde.KWin', '/KWin')
        subprocess.run(['kbuildsycoca5'], stderr=subprocess.DEVNULL)
        subprocess.run(['kwriteconfig5', '--file=kwinrc',
                        '--group=org.kde.kdecoration2',
                        '--key=theme', '__aurorae__svg__CullaX'])
        proxy.reconfigure()
    else:
        fatal('Unable to find KWin. Is it running?')

def fatal(message):
    """Something's wrong."""
    print(message)
    sys.exit(1)

#---------------- CullaX ------------------------------------------------
#Raise flag when finding correct session in plasmarc
flag = False
#Holder for current activity ID
activity = ""

try:
    with open(os.path.expanduser( \
        '~/.config/plasma-org.kde.plasma.desktop-appletsrc')) as f:
        plasmaconfig = f.readlines()
except:
    fatal('Fatal. Unable to find plasma config.')


try:
    with open(os.path.expanduser('~/.config/kactivitymanagerdrc')) as f:
        activityrc = f.readlines()
except:
    print('Unable to find kactivity manager rc.')
    activityrc = None
    flag = True   #There is only default activity

#Retrieve current activity
if activityrc is not None:
    a = [a for a in activityrc if 'current' in a]
    a = a[0].split('=')
    activity = a[1].rstrip()

#Flag if wallpaper is found
found = False

#Find current activity then grab next Image= key
for line in plasmaconfig:
    if activity in line:
        flag = True
    if 'Image=' in line and flag:
        found = True
        break

if not found:
    print("I didn't find your wallpaper. Have you set one yet?")
    sys.exit(1)

tmp, wallpaper = line.split('//')
wallpaper = wallpaper.strip()

if not os.path.isfile(wallpaper):
    sys.exit("I think the wallpaper is {0} but I can't find it. Exiting."
          .format(wallpaper))

# Resize to 512x512 - massive speedup for large images
tmp_img = Image.open(wallpaper.rstrip())
tmp_img = tmp_img.resize((512, 512))
tmp_img.save(os.path.expanduser('~/.cullax.png'))
thief = ColorThief(os.path.expanduser('~/.cullax.png'))
colorslist = thief.get_palette(color_count=2)
os.remove(os.path.expanduser('~/.cullax.png'))

image_darkest = 766
image_lightest = 0
r_dark = 0.0
g_dark = 0.0
b_dark = 0.0
#r_light = 0.0
#g_light = 0.0
#b_light = 0.0

for i in colorslist:
    #print ('r {}, g {}, b {}'.format(i[0], i[1], i[2]))
    local_sum = i[0] + i[1] + i[2]
    
    if local_sum < image_darkest:
        image_darkest = local_sum
        r_dark = float(i[0])
        g_dark = float(i[1])
        b_dark = float(i[2])
    
    #if local_sum > image_lightest:
        #image_lightest = local_sum
        #r_light = float(i[0])
        #g_light = float(i[1])
        #b_light = float(i[2])


#Convert to HLS for colour ops
h_base, l_base, s_base = colorsys.rgb_to_hls(r_dark/255, g_dark/255, b_dark/255)

midlight_color = color_triplet(h_base, 0.45, 0.35)
highlight_color = color_triplet(h_base, 0.7, 1.0)

#Default text colour
foreground = color_triplet(h_base, 0.96, 0.95)


#Lightness threshold for dark text
#if l_base > 0.62:
    #foreground = "16,16,16"
    ##offset = 0 - offset
    #light1 = 0.0
    #light2 = 0.0
    #minimised_task = "248,248,248"

#Panel Background
panel_background = (','.join([str(int(r_dark)), str(int(g_dark)), str(int(b_dark))]))

#Check for monochrome
if s_base < 0.09:
    s_frame = 0.0
    s_button = 0.0
    s_selection = 0.0
    s_base = 0.0
    s_offset = 0.0

#Hues with set parameters
s_frame = s_base
s_button = s_base
s_selection = s_base

if s_base < 0.88 and s_base > 0.09:
    s_frame = s_base + 0.12
    s_button = s_base + 0.12
    s_selection = s_base + 0.12

l_frame = 0.45
l_button = 0.4
l_selection = 0.45
#s_selection = 0.45

#Frame and button hover
#frame = color_triplet(h_base, l_frame, s_frame)

#Plasma selection and button background
#highlight_color = color_triplet(h_base, l_button, s_button)

#Color Scheme Window Decoration and Selection
#window_decoration_color = color_triplet(h_base, l_selection, s_selection)
#window_decoration_color = (','.join([str(int(r_light)), str(int(g_light)), str(int(b_light))]))
#window_decoration_color = theme_highlight

#Color Scheme Focus
focus_offset = 0.06

#Focus
focus_decoration_color = color_triplet(h_base, l_selection + focus_offset,
                                       s_selection - focus_offset)

plasma_colors = plasma_colors.replace('aaa', panel_background)
plasma_colors = plasma_colors.replace('bbb', foreground)
plasma_colors = plasma_colors.replace('ccc', panel_background)
plasma_colors = plasma_colors.replace('ddd', midlight_color)
plasma_colors = plasma_colors.replace('eee', highlight_color)
plasma_colors = plasma_colors.replace('fff', midlight_color)
plasma_colors = plasma_colors.replace('ggg', highlight_color)

try:
    with open(os.path.expanduser( \
        '~/.local/share/plasma/desktoptheme/CullaX/colors'), 'w') as f:
        f.write(plasma_colors)
except:
    fatal("Unable to open Culla Plasma colors. Is it installed?")

try:
    subprocess.run(['kwriteconfig5', '--file=plasmarc',
                    '--group=Theme', '--key=name', 'Default'])

    #Do this too quickly and Plasma won't change
    time.sleep(0.5)

    subprocess.run(['kwriteconfig5', '--file=plasmarc',
                    '--group=Theme', '--key=name', 'CullaX'])
except IOError as e:
    print(e)
    fatal("Fatal. Unable to run kwriteconfig.")

try:
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=Colors:Selection',
                    '--key=BackgroundNormal', midlight_color])
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=Colors:View',
                    '--key=DecorationFocus',
                    focus_decoration_color])
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=WM',
                    '--key=activeBackground',
                    midlight_color])
except:
    fatal("Fatal. Unable to run kwriteconfig.")


#If Culla window dec is active, update it
aur_theme = subprocess.run(['kreadconfig5', '--file=kwinrc',
                            '--group=org.kde.kdecoration2', '--key=theme'], \
                            stdout=subprocess.PIPE)

if b'CullaX' in aur_theme.stdout:
    aurorae(window_decoration_color)
