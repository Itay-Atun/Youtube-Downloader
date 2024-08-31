#!/usr/bin/python3
from  pytube import YouTube
import ssl
from moviepy.editor import *
import os

ssl._create_default_https_context = ssl._create_stdlib_context

# Downloading Youtube Video in mp4 Format
def download_from_youtube(musicFileInput: str) -> None:
    musicFile = open(musicFileInput, "r")
    for line in musicFile:
        videoURL = YouTube(line)
        print(f"downloading {videoURL.title}")
        streamVid = videoURL.streams.filter(file_extension="mp4").first().download("./playlist")

# Converting downloaded mp4 to mp3 files
def convert_to_mp3(list: list) -> None:   
    mylist = os.listdir(list)
    print (mylist)
    for fileName in mylist:
        print(f"Converting {fileName}")
        video = VideoFileClip(f"./playlist/{fileName}")
        baseName = fileName.rsplit(".mp4")
        video.audio.write_audiofile(f"converted/{baseName[0]}.mp3")

# Main function to run program
def main() -> None:
    download_from_youtube("./music.txt")
    convert_to_mp3("/Users/itayat/Learning/GitHub-Projects/Youtube-Downloader/playlist/")

# Running program locally
if __name__ == "__main__":
   main()