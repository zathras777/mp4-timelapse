mp4-timelapse
=============

A small python script to simplify creating timelapses from MP4 videos.

I wrote this to allow me to process a series of MP4 files from a GoPro
camera into a single timelapse sequence. The aim is to capture an image
from the videos at a given time interval and write them out as a continuous
sequence which is then transformed into a video.

It works and has been used a few times. I have a few ideas for improvements
but haven't found the time or need to implement them yet.

If you have improvements or find it useful, let me know!

Update 22 Oct 2014

When creating a timelapse, you can now just specify the first video file
in a sequence and the remaining videos will be found and included. This only
works if a single video file is specified and the other parts are in the
same directory.

