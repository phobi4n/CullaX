#!/usr/bin/env python3

HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

import sys

# Required for pathlib if nothing else
if sys.version_info[1] < 6:
    sys.exit(FAIL + "CullaX requires Python 3.6 or later." + ENDC)

try:
    import cv2
except:
    sys.exit(FAIL + "CullaX requires opencv-python" + ENDC)

try:
    from PIL import Image
except:
    sys.exit(FAIL + "CullaX requires Pillow" + ENDC)

try:
    from skimage import io
except:
    sys.exit(FAIL + "CullaX requires scikit-image" + ENDC)


import os
from distutils.dir_util import copy_tree

dest = os.path.expanduser('~/.local/share/plasma/desktoptheme')

if os.path.exists(dest):
    print(GREEN + "Using Plasma theme directory at {}".format(dest)
          + ENDC)
else:
    print(WARNING + "Creating Plasma theme directory at {}".format(dest)
          + ENDC)
    try:
        os.makedirs(dest)
    except:
        sys.exit(FAIL + "Unable to create Plasma theme directory" + ENDC)
        
source = './desktoptheme/CullaX'
dest += "/CullaX"

if not os.path.exists(source):
    sys.exit(FAIL + "Cannot find CullaX source files." + ENDC)

copy_tree(source, dest, verbose=1)
