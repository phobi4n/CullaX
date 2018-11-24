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
colorslist = thief.get_palette(color_count=3)
os.remove(os.path.expanduser('~/.cullax.png'))

# Get darkest from palette list
image_darkest = 766

for i in colorslist:
    local_sum = i[0] + i[1] + i[2]
    
    if local_sum < image_darkest:
        image_darkest = local_sum
        r_dark = float(i[0])
        g_dark = float(i[1])
        b_dark = float(i[2])
    
#Convert to HLS for colour ops
h_base, l_base, s_base = colorsys.rgb_to_hls(r_dark/255, g_dark/255, b_dark/255)

if s_base < 0.011:
    s_midlight = 0.0
    s_highlight = 0.0
    h_midlight = 0.0
    h_highlight = 0.0
else:
    s_midlight = s_base / 1.5
    s_highlight = s_base + ( (1.0 - s_base) / 1.5)
    h_midlight = h_base - 0.03
    
    if h_midlight < 0.0:
        h_midlight += 1.0
    
    h_highlight = h_base - 0.03
    
    if h_highlight < 0.0:
        h_highlight += 1.0
    

midlight_color = color_triplet(h_midlight, 0.45, s_midlight)
highlight_color = color_triplet(h_highlight, 0.8, s_highlight)



#Default text colour
foreground = color_triplet(h_base, 0.98, 0.95)

#Panel Background
#panel_background = (','.join([str(int(r_dark)), str(int(g_dark)), str(int(b_dark))]))
panel_background = color_triplet(h_base, 0.2, s_base)

plasma_colors = plasma_colors.replace('aaa', panel_background)
plasma_colors = plasma_colors.replace('bbb', foreground)
plasma_colors = plasma_colors.replace('ccc', panel_background)
plasma_colors = plasma_colors.replace('ddd', midlight_color)
plasma_colors = plasma_colors.replace('eee', highlight_color)
plasma_colors = plasma_colors.replace('fff', midlight_color)
plasma_colors = plasma_colors.replace('ggg', highlight_color)
focus_decoration_color = "255,0,0"


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



# ---- Set Global Colours ----
#try:
    #subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    #'--group=Colors:Selection',
                    #'--key=BackgroundNormal', midlight_color])
    #subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    #'--group=Colors:View',
                    #'--key=DecorationFocus',
                    #focus_decoration_color])
    #subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    #'--group=WM',
                    #'--key=activeBackground',
                    #midlight_color])
#except:
    #fatal("Fatal. Unable to run kwriteconfig.")


#If Culla window dec is active, update it
aur_theme = subprocess.run(['kreadconfig5', '--file=kwinrc',
                            '--group=org.kde.kdecoration2', '--key=theme'], \
                            stdout=subprocess.PIPE)

if b'CullaX' in aur_theme.stdout:
    aurorae(window_decoration_color)
