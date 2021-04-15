import argparse
import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import numpy as np
from numba import jit

PREF_WIDTH = 1280
PREF_HEIGHT = 720
PREF_FPS_IN = 30

# Swaps only the non transparent part of the gif
@jit(nopython=True)
def swap(frame, cat, cat_width, cat_height, position, frame_height):
    skip = (frame_height-cat_height) if position == 'bottom' else 0
    for i in range(cat_height):
        for j in range(cat_width):
            if not (cat[i][j][0])+(cat[i][j][1])+(cat[i][j][2]) == 255*3:
                frame[i+skip][j] = cat[i][j]
    return frame

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0, help="ID of webcam device (default: 0)")
    parser.add_argument("--fps", action="store_true", help="output fps every second")
    parser.add_argument("--magnify", type=float, default=2, help="Set gif magnification factor")
    parser.add_argument("--filter", choices=["shake", "none"], default="none")
    parser.add_argument("--position", default="bottom", help="'top' or 'bottom'")
    args = parser.parse_args()

    # Set up webcam capture.
    vc = cv2.VideoCapture(args.camera)

    if not vc.isOpened():
        raise RuntimeError('Could not open video source')

    
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, PREF_WIDTH)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, PREF_HEIGHT)
    vc.set(cv2.CAP_PROP_FPS, PREF_FPS_IN)

    # Query final capture device values (may be different from preferred settings).
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_in = vc.get(cv2.CAP_PROP_FPS)
    print(f'Webcam capture started ({width}x{height} @ {fps_in}fps)')
    magnify = args.magnify
    position = args.position

    fps_out = 20

    with pyvirtualcam.Camera(width, height, fps_out, fmt=PixelFormat.BGR, print_fps=args.fps) as cam:
        print(f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

        # Shake two channels horizontally each frame.
        channels = [[0, 1], [0, 2], [1, 2]]
        gif = cv2.VideoCapture('filters/cat.gif')
        while True:
            # Read frame from webcam.
            ret_cam, frame = vc.read()            
            ret_gif, cat = gif.read()
            if not ret_cam:
                raise RuntimeError('Error fetching frame')
            if not ret_gif:
                gif.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_gif, cat = gif.read()
            cat_shape = cat.shape
            cat_width = int(cat_shape[1]*magnify)
            cat_height = int(cat_shape[0]*magnify)
            cat = cv2.resize(cat,(cat_width, cat_height))
            cat = np.array(cat, np.int16)

            frame = swap(frame, cat, cat_width, cat_height, position, height)

            if args.filter == "shake":
                dx = 15 - cam.frames_sent % 5
                c1, c2 = channels[cam.frames_sent % 3]
                frame[:,:-dx,c1] = frame[:,dx:,c1]
                frame[:,dx:,c2] = frame[:,:-dx,c2]

            cam.send(frame)

            # Wait until it's time for the next frame.
            cam.sleep_until_next_frame()

if __name__ == '__main__':
    main()
