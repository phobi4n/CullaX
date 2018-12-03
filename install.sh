#!/bin/sh

INFO="\e[0;32m"
WARN="\e[0;33m"
FAIL="\e[0;31m"
ENDC="\e[0m"


python3 -c "import cv2" 2>/dev/null

if [ $? == "1" ]; then
    echo -e "${FAIL}CullaX requires opencv-python${ENDC}"
    exit 1
fi

python3 -c "from PIL import Image" 2>/dev/null

if [ $? == "1" ]; then
    echo -e "${FAIL}CullaX requires Python Pillow${ENDC}"
    exit 1
fi

python3 -c "from skimage import io" 2>/dev/null

if [ $? == "1" ]; then
    echo -e "${FAIL}CullaX requires Python scikit-image${ENDC}"
    exit 1
fi

DESKTOPTHEME="${HOME}/.local/share/plasma/desktoptheme"

if [ ! -d $DESKTOPTHEME ]; then
    echo -e "${WARN}Creating Plasma desktoptheme directory ${ENDC}"
    mkdir -pv $DESKTOPTHEME
fi

echo -e "${INFO}Installing Plasma theme ${ENDC}"
cp -r desktoptheme/CullaX/ $DESKTOPTHEME

PIXMAPS="${HOME}/.local/share/pixmaps"

if [ ! -d $PIXMAPS ]; then
    echo -e "${WARN}Creating local pixmaps directory ${ENDC}"
    mkdir -pv $PIXMAPS
fi

echo -e "${INFO}Installing icon ${ENDC}"
cp cullax.png $PIXMAPS

APPLICATIONS="${HOME}/.local/share/applications"

if [ ! -d $APPLICATIONS ]; then
    echo -e "${WARN}Creating local applications directory ${ENDC}"
    mkdir -pv $APPLICATIONS
fi

echo -e "${INFO}Installing menu entry ${ENDC}"
cp  cullax.desktop $APPLICATIONS


PROGS="${HOME}/.local/bin"

if [ ! -d $PROGS ]; then
    echo -e "${WARN}Creating local bin directory ${ENDC}"
    mkdir -pv $PROGS
fi

echo -e "${INFO}Installing CullaX script ${ENDC}"
cp CullaX.py "${PROGS}/CullaX"
