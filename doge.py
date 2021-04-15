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
def swap(frame, meme, meme_width, meme_height, position, frame_height, count):
    skip = (frame_height-meme_height) if position == 'bottom' else 0
    for i in range(meme_height):
        for j in range(meme_width):
            if not (meme[i][j][0])+(meme[i][j][1])+(meme[i][j][2]) == 255*3:
                frame[i+skip][j+count] = meme[i][j]
    return frame

gif_map = {
'cat' : {'path' : 'gifs/cat.gif', 'flip' : False, 'magnify' : 2.5,
            'move' : False, 'position' : "bottom", 'speed' : 0
},
'pikachu' : {'path' : 'gifs/pikachu.gif', 'flip' : False, 'magnify' : 1,
            'move' : True, 'position' : "top", 'speed' : 4
},
'dog' : {'path' : 'gifs/dog.gif', 'flip' : False, 'magnify' : 0.5,
            'move' : True, 'position' : "top", 'speed' : 4
},
'rainbow_cat' : {'path' : 'gifs/rainbow_cat.gif', 'flip' : True, 'magnify' : 1,
            'move' : True, 'position' : "top", 'speed' : 4
}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", choices=["cat", "pikachu","dog","rainbow_cat"], default="cat")
    parser.add_argument("--camera", type=int, default=0, help="ID of webcam device (default: 0)")
    parser.add_argument("--fps", action="store_true", help="output fps every second")
    parser.add_argument("--magnify", type=float, default=None, help="Set gif magnification factor")
    parser.add_argument("--effect", choices=["shake", "none"], default="none")
    parser.add_argument("--position", default=None, help="'top' or 'bottom'")
    parser.add_argument("--move", default=None, help="Move from right to left")
    parser.add_argument("--speed", default=None, help="gif moving speed")
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

    character = args.filter
    magnify = gif_map[character]['magnify'] if args.magnify ==None else args.magnify
    position = gif_map[character]['position'] if args.magnify ==None else args.magnify
    speed = gif_map[character]['speed'] if args.magnify ==None else args.magnify
    move = gif_map[character]['move'] if args.magnify ==None else args.magnify

    fps_out = 20

    with pyvirtualcam.Camera(width, height, fps_out, fmt=PixelFormat.BGR, print_fps=args.fps) as cam:
        print(f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

        # Shake two channels horizontally each frame.
        channels = [[0, 1], [0, 2], [1, 2]]
        gif = cv2.VideoCapture(gif_map[character]['path'])
        count=0
        while True:
            # Read frame from webcam.
            ret_cam, frame = vc.read()            
            ret_gif, meme = gif.read()
            count+=1
            if not ret_cam:
                raise RuntimeError('Error fetching frame')
            if not ret_gif:
                gif.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_gif, meme = gif.read()
            meme_shape = meme.shape
            meme_width = int(meme_shape[1]*magnify)
            meme_height = int(meme_shape[0]*magnify)
            meme = cv2.resize(meme,(meme_width, meme_height))
            if gif_map[character]['flip']:
                meme = cv2.flip(meme, 1)
            meme = np.array(meme, np.int16)
            move_speed = count*speed if move else 0

            frame = swap(frame, meme, meme_width, meme_height, position, height, move_speed)

            if args.effect == "shake":
                dx = 15 - cam.frames_sent % 5
                c1, c2 = channels[cam.frames_sent % 3]
                frame[:,:-dx,c1] = frame[:,dx:,c1]
                frame[:,dx:,c2] = frame[:,:-dx,c2]

            cam.send(frame)

            # Wait until it's time for the next frame.
            cam.sleep_until_next_frame()

if __name__ == '__main__':
    main()
