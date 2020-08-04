#!/usr/bin/env python
"""
Face detector to create .square files
from rectangle images with a face.
It tries to detect the eyes or face
and crop the biggest possible image
around the face.

Also it tries to strip meta data
from jpg files with jpegoptim.

Maybe you can try pngquant for png!

python face_detect.py klitzing.jpg
"""

import cv2
import os
import subprocess
import sys


def get_line(middle, size, max):
    half = size / 2
    start = middle - half
    end = middle + half
    diffStart = 0
    diffEnd = 0
    if start < 0:
        diffStart = start * -1
        start = 0
    if end > max:
        diffEnd = end - max
        end = max

    if diffStart > 0 and diffEnd > 0:
        print('internal error')
        sys.exit(-1)

    return (start - diffEnd, end + diffStart)


def draw_image(faces, file, image):
    height, width, channels = image.shape
    size = min(width, height)

    for (x, y, w, h) in faces:
        x1 = x + (w/2)
        y1 = y + (h/2)

        (l, r) = get_line(x1, size, width)
        (o, u) = get_line(y1, size, height)

        destfile = file + '.square'
        options = '%dx%d+%d+%d' % (size, size, l, o)
        subprocess.call(['convert', file, '-crop', options, destfile])
        subprocess.call(['jpegoptim', '-q', '-s', destfile])
        print(' found: %s' % file)


def detect_faces(path, imagePath):
    faceCascade = cv2.CascadeClassifier(path)
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(15, 15),
                                         flags=cv2.CASCADE_SCALE_IMAGE)

    facesCount = len(faces)
    if facesCount == 0:
        print(' not found: %s' % imagePath)
        return False

    if facesCount > 1:
        print(' multiple found: %s %d' % (imagePath, facesCount))
        return False

    draw_image(faces, imagePath, image)
    return True


def start(args):
    image = args[1]

    if not os.path.exists(image):
        print('file not found %s' % image)
        sys.exit(0)

    if not os.path.isfile(image):
        sys.exit(0)

    print('try: %s' % image)

    if len(args) > 2:
        cascPath = [args[2]]
    else:
        cascPath = []
        path = '/usr/share/opencv4/haarcascades/'
        cascPath.append(path + 'haarcascade_eye.xml')
        # cascPath.append(path + 'haarcascade_mcs_eyepair_big.xml')
        cascPath.append(path + 'haarcascade_frontalface_alt.xml')

    for casc in cascPath:
        print('   try casc: %s' % casc)
        if detect_faces(casc, image):
            print('')
            sys.exit(0)


start(sys.argv)
