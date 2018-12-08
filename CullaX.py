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
BackgroundNormal=224,4,4
ForegroundNormal=224,4,22

[Colors:View]
BackgroundNormal=hhh
ForegroundNormal=bbb
DecorationHover=ddd"""


# https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv/43111221
def get_dominant_color(image):
    img = io.imread(image)[:, :, :3]
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    return palette[np.argmax(counts)]

def get_average(image):
    """ Get the average of all pixels munged together"""
    img = io.imread(image)[:, :, :3]
    return img.mean(axis=0).mean(axis=0)

def notify_user():
    """ Simple notification to show something's happening """
    icon_path = os.path.expanduser('~/.local/share/pixmaps/cullax.png')
    icon = '--icon={}'.format(icon_path)

    try:
        subprocess.run(['notify-send',
                        icon,
                        '--expire-time=3000',
                        'CullaX - Reticulating Splines'])
    except:
        pass

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

def aurorae(active):
    """Open decoration template, substitue our colour
    then write decoration.svg"""
    try:
        with open(os.path.expanduser(
                  '~/.local/share/aurorae/themes/CullaX/decoration-template.svg')) as f:
            auroraetemplate = f.read()
    except IOError:
        sys.exit("Unable to find Aurorae template.")

    r, g, b = active.split(',')
    hex_colour = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
    auroraetemplate = auroraetemplate.replace('TEMPLAT', hex_colour)
    #auroraetemplate = auroraetemplate.replace('TEMPLA2', '#f7f7f7')
    

    try:
        with open(os.path.expanduser(
                '~/.local/share/aurorae/themes/CullaX/decoration.svg'), 'w') as f:
            f.write(auroraetemplate)
    except IOError:
        sys.exit("Fatal. Unable to write aurorae decoration.")

    session_bus = dbus.SessionBus()

    if [k for k in session_bus.list_names() if 'KWin' in k]:
        proxy = session_bus.get_object('org.kde.KWin', '/KWin')
        subprocess.run(['kbuildsycoca5'], stderr=subprocess.DEVNULL)
        subprocess.run(['kwriteconfig5', '--file=kwinrc',
                        '--group=org.kde.kdecoration2',
                        '--key=theme', '__aurorae__svg__CullaX'])
        proxy.reconfigure()
    else:
        sys.exit('Unable to find KWin. Is it running?')


# ----  CullaX  ----

# Try sending a notification to show we're working
notify_user()

# Raise flag when finding correct session in plasmarc
flag = False
# Holder for current activity ID
activity = ""

try:
    with open(os.path.expanduser(
            '~/.config/plasma-org.kde.plasma.desktop-appletsrc')) as f:
        plasmaconfig = f.readlines()
except:
    sys.exit('Unable to find plasma config.')


try:
    with open(os.path.expanduser('~/.config/kactivitymanagerdrc')) as f:
        activityrc = f.readlines()
except:
    print('Unable to find kactivity manager rc. Presuming only default activity.')
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
    sys.exit("I didn't find your wallpaper. Have you set one yet?")

tmp, wallpaper = line.split('//')
wallpaper = wallpaper.strip()

if not os.path.exists(wallpaper):
    sys.exit("I think the wallpaper is {0} but I can't find it. Exiting."
             .format(wallpaper))

# Resize to 256x256 - massive speedup
tmp_img = Image.open(wallpaper.rstrip())
tmp_img = tmp_img.resize((256, 256))
tmp_img_path = os.path.expanduser('.cullax.png')
tmp_img.save(tmp_img_path)

# Get dominant and average colors
dominant_color = get_dominant_color(tmp_img_path)
avg_color = get_average(tmp_img_path)
h_base, l_base, s_base = colorsys.rgb_to_hls(dominant_color[0]/255.0,
                                             dominant_color[1]/255.0,
                                             dominant_color[2]/255.0)
h_avg, l_avg, s_avg = colorsys.rgb_to_hls(avg_color[0]/255.0,
                                          avg_color[1]/255.0,
                                          avg_color[2]/255.0)

#Cleanup temp image
os.remove(tmp_img_path)

print("HLS Dominant: {} {} {}".format(h_base, l_base, s_base))
print("HLS Average:  {} {} {}".format(h_avg, l_avg, s_avg))

l_midlight = 0.4

if s_base < 0.011:
    s_midlight = 0.0
    s_highlight = 0.0
    h_midlight = 0.0
    h_highlight = 0.0
else:
    s_midlight = s_base

    if s_base < 0.4 and s_base > 0.08:
        s_highlight = 0.5
    elif s_base < 0.08:
        s_highlight = 0.1
    else:
        s_highlight = 1.0

    h_midlight = h_base
    h_highlight = h_base

if l_avg > 0.69:
    panel_background = color_triplet(h_base, 0.96, s_base)
    foreground = color_triplet(h_base, 0.25, 0.05)
    midlight_color = color_triplet(h_base, 0.8, 0.5)
    highlight_color = color_triplet(h_highlight, 0.6, 0.5)
    clock_hands_color = color_triplet(h_base, 0.64, 0.05)
    focus_decoration_color = highlight_color
else:
    panel_background = color_triplet(h_base, 0.07, s_base)
    highlight_color = color_triplet(h_highlight, 0.65, s_highlight)
    midlight_color = color_triplet(h_base, 0.5, s_midlight)
    foreground = color_triplet(h_base, 0.98, 0.95)
    clock_hands_color = color_triplet(h_base, 0.95, 0.7)
    focus_decoration_color = color_triplet(h_base, 0.3, 0.8)

plasma_colors = plasma_colors.replace('aaa', panel_background)
plasma_colors = plasma_colors.replace('bbb', foreground)
plasma_colors = plasma_colors.replace('ccc', panel_background)
plasma_colors = plasma_colors.replace('ddd', midlight_color)
plasma_colors = plasma_colors.replace('eee', highlight_color)
plasma_colors = plasma_colors.replace('fff', midlight_color)
plasma_colors = plasma_colors.replace('ggg', highlight_color)
plasma_colors = plasma_colors.replace('hhh', clock_hands_color)


try:
    with open(os.path.expanduser(
            '~/.local/share/plasma/desktoptheme/CullaX/colors'), 'w') as f:
        f.write(plasma_colors)
except:
    sys.exit("Unable to open Culla Plasma colors. Is it installed?")

try:
    subprocess.run(['kwriteconfig5', '--file=plasmarc',
                    '--group=Theme', '--key=name', 'Default'])

    #Do this too quickly and Plasma won't change
    time.sleep(0.5)

    subprocess.run(['kwriteconfig5', '--file=plasmarc',
                    '--group=Theme', '--key=name', 'CullaX'])
except IOError as e:
    sys.exit(e)



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
except IOError as e:
    sys.exit(e)


# If Culla window dec is active, update it
aur_theme = subprocess.run(['kreadconfig5', '--file=kwinrc',
                            '--group=org.kde.kdecoration2', '--key=theme'], \
                            stdout=subprocess.PIPE)

if b'CullaX' in aur_theme.stdout:
    aurorae(focus_decoration_color)
