# virtual-camera-meme-filters
Overlay gifs of memes on your video calls (works with Zoom, Google Meet, Microsoft Teams)

[Demo]('demo.gif')

## Installation guide

```
pip install -r requirements.txt
```
[PyVirtualCam](https://github.com/letmaik/pyvirtualcam) needs [OBS](https://obsproject.com/) if you're using Mac or Windows, or install [v4l2loopback](v4l2loopback) for Linux for virtual camera output. 

## Usage

```
python run_cat.py --magnify 2.5 --position bottom --filter none
```

Open up Zoom or Google Meet and choose OBS/v4l2loopback Virtual Camera 

If you're using Google Chrome and OBS virtual camera option is not avilable then disable hardware acceleration in chrome settings and restart.


## Future updates
Will add more memes (doge coming up next!)