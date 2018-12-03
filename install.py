#!/usr/bin/env python3

import sys

# Required for pathlib if nothing else
if sys.version_info[1] < 6:
    sys.exit("CullaX requires Python 3.6 or later.")


try:
    import cv2
except:
    sys.exit("CullaX requires opencv-python")

try:
    from PIL import Image
except:
    sys.exit("CullaX requires Pillow")

try:
    from skimage import io
except:
    sys.exit("CullaX requires scikit-image")


