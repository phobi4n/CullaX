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
DecorationFocus=ggg

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

#---------------- Culla ------------------------------------------------
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
colorslist = thief.get_palette(color_count=3)
os.remove(os.path.expanduser('~/.cullax.png'))

local_lowest = 766
r_base = 0.0
g_base = 0.0
b_base = 0.0

for i in colorslist:
    print ('r {}, g {}, b {}'.format(i[0], i[1], i[2]))
    local_sum = i[0] + i[1] + i[2]
    
    if local_sum < local_lowest:
        local_lowest = local_sum
        r_base = float(i[0])
        g_base = float(i[1])
        b_base = float(i[2])

print(r_base, g_base, b_base)
#sys.exit()
#Choose darkest returned colour
#image_value = 1.0


#for x in colorslist:
    #r, g, b = tuple(int(x[i:i+2], 16) for i in (1, 3, 5))
    #h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    #if v <= image_value:   #Choose darkest
        #r_base = r
        #g_base = g
        #b_base = b
        #image_value = v


#Convert to HLS for colour ops
h_base, l_base, s_base = colorsys.rgb_to_hls(r_base/255, g_base/255, b_base/255)


print("BASE HSL  ", h_base, s_base, l_base)

l_base = 0.3
s_base = 0.6

#Boundary check
if s_base > 0.99:
    s_base = 0.99

#Dialog background adjustment amounts
l_offset = 0.09
s_offset = 0.09

#Default text colour
foreground = "255,255,255"

#Minimised taskbar
minimised_task = "36,36,36"

#Lightness threshold for dark text
if l_base > 0.62:
    foreground = "16,16,16"
    #offset = 0 - offset
    light1 = 0.0
    light2 = 0.0
    minimised_task = "248,248,248"

#Panel Background
panel_background = (','.join([str(int(r_base)), str(int(g_base)), str(int(b_base))]))
print(panel_background)
#panel_background = (color_triplet(h_base, l_base, s_base))

print(color_triplet(h_base,l_base,s_base))
#Check for monochrome
if s_base < 0.09:
    s_frame = 0.0
    s_button = 0.0
    s_selection = 0.0
    s_base = 0.0
    s_offset = 0.0

#Hues relative to base
#l_dialog = l_base + l_offset
#s_dialog = s_base - s_offset

#Alternate shade for dialog backgrounds
#dialog_background = color_triplet(h_base, l_dialog, s_dialog)

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
frame = color_triplet(h_base, l_frame, s_frame)

#Plasma selection and button background
highlight_color = color_triplet(h_base, l_button, s_button)

#Color Scheme Window Decoration and Selection
window_decoration_color = color_triplet(h_base, l_selection, s_selection)

#Color Scheme Focus
focus_offset = 0.06

#Focus
focus_decoration_color = color_triplet(h_base, l_selection + focus_offset,
                                       s_selection - focus_offset)

plasma_colors = plasma_colors.replace('aaa', panel_background)
plasma_colors = plasma_colors.replace('bbb', foreground)
plasma_colors = plasma_colors.replace('ccc', panel_background)
plasma_colors = plasma_colors.replace('ddd', frame)
plasma_colors = plasma_colors.replace('eee', highlight_color)
plasma_colors = plasma_colors.replace('fff', highlight_color)
plasma_colors = plasma_colors.replace('ggg', minimised_task)

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
                    '--key=BackgroundNormal', window_decoration_color])
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=Colors:View',
                    '--key=DecorationFocus',
                    focus_decoration_color])
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=WM',
                    '--key=activeBackground',
                    window_decoration_color])
except:
    fatal("Fatal. Unable to run kwriteconfig.")


#If Culla window dec is active, update it
aur_theme = subprocess.run(['kreadconfig5', '--file=kwinrc',
                            '--group=org.kde.kdecoration2', '--key=theme'], \
                            stdout=subprocess.PIPE)

if b'CullaX' in aur_theme.stdout:
    aurorae(window_decoration_color)
