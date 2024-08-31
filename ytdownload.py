#!/usr/bin/python3

from  pytube import YouTube
import ssl
from moviepy.editor import *
import os

ssl._create_default_https_context = ssl._create_stdlib_context
musicFile = open("./music.txt", "r")

for line in musicFile:
  videoURL = YouTube(line)
  print(f"downloading {videoURL.title}")
  streamVid = videoURL.streams.filter(file_extension="mp4").first().download("./playlist")


mylist = os.listdir("/Users/itayat/Learning/GitHub-Projects/Youtube-Downloader/playlist/")
print (mylist)
for fileName in mylist:
    print(f"Converting {fileName}")
    video = VideoFileClip(f"./playlist/{fileName}")
    baseName = fileName.rsplit(".mp4")
    video.audio.write_audiofile(f"converted/{baseName[0]}.mp3")

    