#!/bin/sh

INFO="\e[0;32m"
WARN="\e[0;33m"
FAIL="\e[0;31m"
MESS="\e[1;34m"
ENDC="\e[0m"

DESKTOPTHEME="${HOME}/.local/share/plasma/desktoptheme"
PIXMAPS="${HOME}/.local/share/pixmaps"
APPLICATIONS="${HOME}/.local/share/applications"
PROGS="${HOME}/.local/bin"
AURORAE="${HOME}/.local/share/aurorae/themes"


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

if [ ! -d $DESKTOPTHEME ]; then
    echo -e "${WARN}Creating Plasma desktoptheme directory ${ENDC}"
    mkdir -pv $DESKTOPTHEME
fi

echo -e "${INFO}Installing Plasma theme ${ENDC}"
cp -r desktoptheme/CullaX/ $DESKTOPTHEME

if [ ! -d $PIXMAPS ]; then
    echo -e "${WARN}Creating local pixmaps directory ${ENDC}"
    mkdir -pv $PIXMAPS
fi

echo -e "${INFO}Installing icon ${ENDC}"
cp cullax.png $PIXMAPS

if [ ! -d $APPLICATIONS ]; then
    echo -e "${WARN}Creating local applications directory ${ENDC}"
    mkdir -pv $APPLICATIONS
fi

echo -e "${INFO}Installing menu entry ${ENDC}"
cp  cullax.desktop $APPLICATIONS

if [ ! -d $PROGS ]; then
    echo -e "${WARN}Creating local bin directory ${ENDC}"
    mkdir -pv $PROGS
fi

echo -e "${INFO}Installing CullaX script ${ENDC}"
cp CullaX.py "${PROGS}/CullaX"

if [ ! -d $AURORAE ]; then
    echo -e "${WARN}Creating Aurorae theme directory ${ENDC}"
    mkdir -pv $AURORAE
fi

echo -e "${INFO}Installing Aurorae theme ${ENDC}"
cp -r themes/CullaX $AURORAE

echo
echo -e "${MESS}Look for CullaX under Applications->Settings. You will need to select the CullaX window decoration manually. ${ENDC}"
