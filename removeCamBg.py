# see red_blue.py in the examples dir
import os
import pyfakewebcam
import numpy as np
import cv2
import argparse
import time
import logging

W = 640  # Picture width
H = 480  # Picture height

logging.basicConfig(level=logging.INFO)

def parseArgs():
    parser = argparse.ArgumentParser(description="Read a webcam image and replace all background with pixels from a custom image.")

    parser.add_argument('-b', '--background', help="Filename of the background image. By default, it's a noisy image", default=None)
    parser.add_argument('-u', '--mask-update', help="Update the face mask every u frames", default=3, type=int)
    parser.add_argument('-d', '--mask-decay', help="Upon losing the face, how fast shall the face fade away. Between 0 and 1. 0 Means to delete mask immediately, 1 means keep mask forever.", default=0.1, type=float)
    parser.add_argument('-m', '--mask-max', help="Maximum blending factor of the detected face, between 0 and 1. 1 means the face is not transparent at all. 0 means face it not visible at all", type=float, default=1)
    parser.add_argument('-c', '--camera-id', help="Id of the video capturing device to open. Will use 0 by default, that will open the default backend camera.", default=0, type=int)
    parser.add_argument('-s', '--scale-mask', help="Scale the area of the detected face by this factor", default=1, type=float)
    parser.add_argument("--debug", help="If set, show the resulting image in a debug window", action='store_true', default=False)

    return parser.parse_args()

    return None

def createNoisyBg(W, H):
    X = np.random.rand(H, W) * 256
    return np.dstack([X]*3)


def loadBgImage(bgFile):
    if bgFile is not None:
        bg = cv2.imread(bgFile, cv2.IMREAD_COLOR)
    else:
        bg = createNoisyBg(W, H)
    return cv2.resize(bg, (W, H))


def main():
    args = parseArgs()
    print (args)
    bgImg = loadBgImage(args.background)

    camera = pyfakewebcam.FakeWebcam('/dev/video20', W, H)

    cam = cv2.VideoCapture(args.camera_id)

    face_cascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml'))


    nr = 0
    fgMask_float = 0
    framesInLastSec = 0
    start = time.time()
    while True:
        ret_val, img = cam.read()
        if nr % args.mask_update == 0:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.5, 4)
            img2 = img / 256.0

            fgMask  = np.zeros((480, 640), dtype=np.uint8)
            wMax = 0
            biggest = None
            for dim in faces:
                if dim[2] > wMax:
                    wMax = dim[2]
                    biggest = dim
            if biggest is not None:
                (x, y, w, h) = biggest
                cv2.ellipse(fgMask, (x+w//2, y+h//2), (int(w//1.5*args.scale_mask), int(h/1.2*args.scale_mask)), 0, 0, 360, 255, -1)
                fgMask_float = cv2.GaussianBlur(fgMask / 256., (51, 51), 0) * args.mask_max
                fgMask_float = np.dstack([fgMask_float]*3)
            else:
                fgMask_float *= args.mask_decay

        result = (bgImg * (1-fgMask_float) + img * (fgMask_float)).astype(np.uint8)

        if args.debug:
            cv2.imshow("input", img)
            cv2.imshow("result", result)
            cv2.waitKey(1)

        nr = nr + 1
        framesInLastSec = framesInLastSec + 1
        if time.time() - start > 1:
            logging.info(f"Processed {framesInLastSec} frames in 1 second")
            framesInLastSec = 0
            start = time.time()

        camera.schedule_frame(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

if __name__ == '__main__':
    main()
