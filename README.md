# WebCam Remove Background

A Python script to remove background of a webcam image and stream the result into a virtual video device. The background removal is based on face detection with OpenCV within each image.

## Requirements
- Tested with Python 3.7
- Requires [V4L2-Loopback](https://github.com/umlaeute/v4l2loopback).
  In Ubuntu this is available as the package `v4l2loopback-utils` and its dependencies. **HOWEVER** under Ubuntu 18.04 with recent Kernel, the module has a [bug](https://github.com/umlaeute/v4l2loopback/issues/172) (see [here](https://github.com/jremmons/pyfakewebcam/issues/5#issuecomment-612167782) also). Hence, it is advised to install `v4l2loopback` from github source.

## Usage
1. create a virtual video device
    ```bash
	$ sudo modprobe v4l2loopback devices=1 video_nr=20 card_label='v4l2loopback' exclusive_caps=1
	```
2. Make sure you the video device `/dev/video20` has been created.
3. Run `python removeCamBg.py`

## Command line arguments
See `python removeCamBg.py --help`.

```
usage: removeCamBg.py [-h] [-b BACKGROUND] [-u MASK_UPDATE] [-d MASK_DECAY]
                      [-m MASK_MAX] [-c CAMERA_ID] [--debug]

Read a webcam image and replace all background with pixels from a custom
image.

optional arguments:
  -h, --help            show this help message and exit
  -b BACKGROUND, --background BACKGROUND
                        Filename of the background image. By default, it's a
                        noisy image
  -u MASK_UPDATE, --mask-update MASK_UPDATE
                        Update the face mask every u frames
  -d MASK_DECAY, --mask-decay MASK_DECAY
                        Upon losing the face, how fast shall the face fade
                        away. Between 0 and 1. 0 Means to delete mask
                        immediately, 1 means keep mask forever.
  -m MASK_MAX, --mask-max MASK_MAX
                        Maximum blending factor of the detected face, between
                        0 and 1. 1 means the face is not transparent at all. 0
                        means face it not visible at all
  -c CAMERA_ID, --camera-id CAMERA_ID
                        Id of the video capturing device to open. Will use 0
                        by default, that will open the default backend camera.
  --debug               If set, show the resulting image in a debug window
```

## Example Result
Holding a newspaper in front of the camera yields these results.

Input image:

![](doc/before.png)

Output image with some blending.

![](doc/after.png)
