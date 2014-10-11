#!/usr/bin/env python

# --------------------------------------------------------------------------
# "THE TEA-WARE LICENSE":
# This code was written by David Reid <zathrasorama@gmail.com>
# As long as you retain this notice you can do whatever you want with this
# stuff. If we meet some day, and you think this stuff is worth it, you can
# buy me a cup of tea in return.
# --------------------------------------------------------------------------

from __future__ import print_function

import os
import sys
import subprocess
import argparse
from tempfile import mkdtemp

# In an attempt to make this compatible with Python 2.x and 3.x,
# handle change in iteritems() between versions rather than importing
# six.
if sys.version_info >= (3, 0):
    def do_iter(x):
        return x.items()
else:
    def do_iter(x):
        return x.iteritems()


class TimelapseConversion(object):
    FFMPEG = "/usr/local/bin/ffmpeg"
    def __init__(self, interval = 2):
        self.interval = interval
        self.tmpdir = mkdtemp()
        self.seq = 0
        self.size = '1280x960'

        self.options = {
            'f': 'image2',
            'vf': 'fps=fps=1/%d' % interval,
            's': self.size}

    def set_size(self, sz):
        if not 'x' in sz:
            print("Malformed size detected. Format as <width>x<height>. Ignoring.")
            return
        self.size = sz
        self.options['s'] = sz

    def _make_command(self):
        cmd = [self.FFMPEG, '-an']
        for k,v in do_iter(self.options):
            cmd.extend(['-%s' % k, v])
        return cmd

    def extract_images(self, inpfn):
        if not os.path.exists(inpfn):
            print("Failed to process {0} as it doesn't exist!".format(inpfn))
            return False

        output_dir = mkdtemp()

        cmd = self._make_command()
        cmd.insert(1, '-i')
        cmd.insert(2, inpfn)
        cmd.append('%s/tmp_%%06d.png' % output_dir)

        print("Processing {0} with temp directory {1}".format(inpfn, output_dir))

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            print("Extraction failed: ", err)
            return False
        for imgfn in sorted(os.listdir(output_dir)):
            seqfn = os.path.join(self.tmpdir, 'seq_%06d.png' % self.seq)
            os.rename(os.path.join(output_dir, imgfn), seqfn)
            self.seq += 1
        os.rmdir(output_dir)
        return True

    def build_movie(self, outputfn=None):
        if self.seq == 0:
            print("No images to make into movie.")
            return False

        print("\nCreating movie from {0} images...\n".format(self.seq))

        moviefn = '%s/timelapse.mp4' % self.tmpdir if outputfn is None else outputfn
        cmd = [self.FFMPEG, '-i', '%s/seq_%%06d.png' % self.tmpdir,
               '-c:v', 'libx264',
               '-r', '30',
               '-pix_fmt', 'yuv420p',
               moviefn]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        for fn in os.listdir(self.tmpdir):
            if fn.endswith('png'):
                os.unlink(os.path.join(self.tmpdir, fn))

        if proc.returncode != 0:
            print("Extraction failed: ", err)
            return False
        print("Movie created as {0}".format(moviefn))
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to create timelapse movie from MP4(s)')
    parser.add_argument('videos', nargs='+', help='video file to transform')
    parser.add_argument('--interval', type=int, metavar='SECONDS', default="2", help='timelapse interval [default=2]')
    parser.add_argument('--output', help='final movie filename')
    parser.add_argument('--size', help='size of images and final movie')

    args = parser.parse_args()
    print(args)
    tc = TimelapseConversion(args.interval)
    if args.size:
        tc.set_size(args.size)
    for fn in args.videos:
        tc.extract_images(fn)
    tc.build_movie(args.output)
