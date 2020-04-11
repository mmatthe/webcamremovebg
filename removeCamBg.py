# see red_blue.py in the examples dir
import os
import pyfakewebcam
import numpy as np
import cv2
import argparse

W = 640  # Picture width
H = 480  # Picture height

def parseArgs():
    parser = argparse.ArgumentParser(description="Read a webcam image and replace all background with pixels from a custom image.")

    parser.add_argument('-b', '--background', help="Filename of the background image. By default, it's a noisy image", default=None)

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
    bgImg = loadBgImage(args.background)

    camera = pyfakewebcam.FakeWebcam('/dev/video20', 640, 480)


    cam = cv2.VideoCapture(0)

    # bgImg =

    # bgImg = cv2.cvtColor(bgImg, cv2.COLOR_RGB2BGR)

    face_cascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml'))

    i = 0

    while True:
        ret_val, img = cam.read()
        i = i + 1
        if i % 3 != 0:
            continue
        # img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) / 256.0
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
            # cv2.circle(fgMask, (x+w//2, y+h//2), int(h//2*1.2), 255, -1)
            cv2.ellipse(fgMask, (x+w//2, y+h//2), (int(w/1.5), int(h/1.2)), 0, 0, 360, 255, -1)

        # fgMask_bool = fgMask > 0
        fgMask_float = cv2.GaussianBlur(fgMask / 256., (51, 51), 0)
        # cv2.imshow("mask", fgMask_float)


        fgMask_float = np.dstack([fgMask_float]*3)
        # result = bgImg.copy()
        # # result[fgMask_bool] = img[fgMask_bool]
        result = (bgImg * (1-fgMask_float) + img * (fgMask_float)).astype(np.uint8)

        cv2.imshow("result", result)
        cv2.waitKey(1)

        camera.schedule_frame(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

if __name__ == '__main__':
    main()
