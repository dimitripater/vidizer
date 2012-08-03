"""
This Python script uses ffmpeg to extract a n-number of png files from a movie, whatever its length.
It then plays back the movie starting with the frame that was extracted, so you can preview it.
If you want to keep the movie and stills, the files are moved to another directory. If not, all the files will be deleted.

TODO: something breaks (i.e. too many stills are generated) when 'start' (ffmpeg -i filename) does not equal 0.000000.

TODO: turn this into a Django management command

NOTE: only tested in Linux Ubuntu 12.04

Dimitri Pater ~ Django Web Studio
"""

import sys,os,re
from subprocess import *
import datetime
import glob
import shutil

frames = 10.0
tagging = "1=tag1, 2=tag2, 3=tag3, 4=tag4, 5=tag5"
view_for = 5
vid_ext = ('.mp4','.avi','.wmv','.mpg','.avi','.mpeg') # add more
current_dir = os.getcwd()

for video in os.listdir('.'):
    if video.endswith(vid_ext):
        # todo: store video filename in a database
        output = Popen(["ffmpeg", "-i", video], stderr=PIPE).communicate()

        # search for duration
        re_duration = re.compile("Duration: (.*?)\.")
        duration = re_duration.search(output[1]).groups()[0]
        # todo: if this filename already exists in database and duration is not equal -> rename it, else skip
        # search for start
        re_start = re.compile("start: (\d+.\d+)")
        start = re_start.search(output[1]).groups()[0]
        
        if start != "0.000000":
            print start
            print "..... %s was put aside for later processing ....." % video
            # move this file to shelf directory for later processing
            # ffmpeg generates too many png files, some sort of offset me thinks
            shutil.move(video,current_dir+'/shelf')

        else:
            seconds = reduce(lambda x,y:x*60+y,map(int,duration.split(":")))
            rate = frames/seconds#+float(start) # does adding the start offset helps?

            output = Popen(["ffmpeg", "-i", video, "-r", str(rate), "-vcodec", "png", '%s-%s.png' % (video,"%d")]).communicate()
    
            start_time = datetime.datetime(1,1,1,0,0,0)
            sequence = ['00:00:00']
            interval = int(1/rate)
            for i in range(int(frames)):
                x = start_time+datetime.timedelta(seconds=interval)
                # todo: store the -ss in a database, only the interval or the whole sequence; not sure which one is better
                sequence.append(x.time().strftime("%H:%M:%S"))
                interval += 1/rate
                # preview: play n seconds from every still
                output = Popen(["mplayer", video, "-vo", "x11", "-ss", x.time().strftime("%H:%M:%S"), "-endpos", str(view_for) ]).communicate()
            # remove first frame because it is generated twice by ffmpeg, I don't know why it is generated twice.
            os.remove("%s-1.png" % video)
            # maybe after watching it do not store the object in a database and delete the files
            delete = raw_input('Delete this video (Y/N)? (warning: this cannot be undone) ')
            if delete=="Y":
                os.remove(video)
                for fn in glob.glob(video+'*.*'):
                    os.remove(fn)
            else:
                # after watching we want to rate and tag this video
                # todo: store rating and tags in a database
                rating = raw_input('Rate this video (1-10): ')
                print "You rated: ", rating
                tags = raw_input('Tag this video %s: ' % tagging)
                print "Your tags: ", tags
                # commit save
                # do some cleaning up: move video and png files from current working directory
                shutil.move(video,current_dir+'/videos')
                for fn in glob.glob(video+'*.*'):
                    shutil.move(fn,current_dir+'/stills')

