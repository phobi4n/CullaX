#!/usr/bin/python3
"""Culla generates a desktop theme using colours
from the current wallpaper"""

import sys
import os
import subprocess
import time
import colorsys
import dbus
from PIL import Image
import cv2
import numpy as np
from skimage import io

if sys.version_info[1] < 6:
    print("Culla requires Python 3.6 or later.")
    sys.exit(1)


#Template for our Plasma theme
plasma_colors = """[Colors:Window]
ForegroundNormal=bbb
BackgroundNormal=aaa

[Colors:Selection]
BackgroundNormal=eee

[Colors:Button]
ForegroundNormal=bbb
BackgroundNormal=fff
DecorationFocus=eee
DecorationHover=ggg

[Colors:Compilmentary]
BackgroundNormal=4,4,222

[Colors:View]
BackgroundNormal=ccc
ForegroundNormal=bbb
DecorationHover=ddd"""


# ------ Image Functions ------------------------------------------------
#https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv/43111221
def get_dominant_color(image):
    img = io.imread(image)
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    return palette[np.argmax(counts)]

# ------ Culla Functions ------------------------------------------------
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

# Resize to 386x386 - massive speedup for large images
tmp_img = Image.open(wallpaper.rstrip())
tmp_img = tmp_img.resize((256, 256))
tmp_img.save(os.path.expanduser('~/.cullax.png'))
dom_overflow = get_dominant_color(os.path.expanduser('~/.cullax.png'))
print(dom_overflow)
h_base, l_base, s_base = colorsys.rgb_to_hls(dom_overflow[0]/255.0, dom_overflow[1]/255.0, dom_overflow[2]/255.0)
os.remove(os.path.expanduser('~/.cullax.png'))

#h_base, l_base, s_base = colorsys.rgb_to_hls(9/255.0, 15/255.0, 25/255.0)
print("HLS: {} {} {}".format(h_base, l_base, s_base))

l_midlight = l_base

if l_base < 0.4:
    l_midlight = (l_base + 0.5) / 2.0

if s_base < 0.011:
    s_midlight = 0.0
    s_highlight = 0.0
    h_midlight = 0.0
    h_highlight = 0.0
else:
    s_midlight = s_base
    s_highlight = 1.0
    h_midlight = h_base
    h_highlight = h_base 
    
#Panel Background
if l_base > 0.7:
    panel_background = color_triplet(h_base, 0.96, s_base)
    foreground = color_triplet(h_base, 0.25, 0.05)
    midlight_color = color_triplet(h_base, 0.7, 0.5)
    highlight_color = color_triplet(h_highlight, 0.3, s_highlight)
else:
    panel_background = color_triplet(h_base, 0.02, s_base)
    highlight_color = color_triplet(h_highlight, 0.75, s_highlight)
    midlight_color = color_triplet(h_base, l_midlight, s_midlight)
    foreground = color_triplet(h_base, 0.98, 0.95)

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
try:
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=Colors:Selection',
                    '--key=BackgroundNormal', midlight_color])
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=Colors:View',
                    '--key=DecorationFocus',
                    midlight_color])
    subprocess.run(['kwriteconfig5', '--file=kdeglobals',
                    '--group=WM',
                    '--key=activeBackground',
                    midlight_color])
except:
    fatal("Fatal. Unable to run kwriteconfig.")


#If Culla window dec is active, update it
#aur_theme = subprocess.run(['kreadconfig5', '--file=kwinrc',
                            #'--group=org.kde.kdecoration2', '--key=theme'], \
                            #stdout=subprocess.PIPE)

#if b'CullaX' in aur_theme.stdout:
    #aurorae(window_decoration_color)
