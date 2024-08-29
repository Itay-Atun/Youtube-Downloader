#!/usr/bin/python3

from  pytube import YouTube
import ssl

ssl._create_default_https_context = ssl._create_stdlib_context
musicFile = open("/Users/itayat/Learning/Programing/Python/YoutubeDownload/music.txt", "r")

for line in musicFile:
  videoURL = YouTube(line)
  print(f"downloading {videoURL.title}")
  streamVid = videoURL.streams.filter(only_audio=True).first().download("/Users/itayat/Learning/Programing/Python/YoutubeDownload/playlist")
