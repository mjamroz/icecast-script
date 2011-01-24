#!/usr/bin/env python
#public domain, Michal Jamroz, jamroz AT chem.uw.edu.pl
# REQUIRE "libshout binding for python". You can download source from icecast.org

#script run stream in python threads - you can init few streams from this one script
#additionaly, script plays jingles
#and write 7 future songs to file "mountpoint-current.txt"

#you can stream movie, too - check examples at bottom

#CHANGE:
hostname = "localhost"
port = 8000
password = "password"
jingle_after = 4 #play jingle after each 4 songs
jingles="/home/user/jingles" #directory with jingle files, if you dont have jingles - leave empty ""

#defaults: bitrate 128, channels: 2, samplerate: 44100, music format: mp3 (can be "vorbis")
#at the bottom of file you have examples


import shout
import sys
from glob import glob
from random import shuffle,choice
import threading

class RunStream (threading.Thread):
   def __init__ (self, channel_mount, music_directory, station_url, genre,name, description, bitrate="128", samplerate="44100", channels="2",music_format="mp3",jingle_dir="",ogv=0):
      #init shout connection
      global hostname,port,password
      self.song_counter = 0
      self.s = shout.Shout()
      self.s.audio_info = {shout.SHOUT_AI_BITRATE:bitrate, shout.SHOUT_AI_SAMPLERATE:samplerate, shout.SHOUT_AI_CHANNELS:channels}
      self.s.name = name
      self.ogv = ogv
      self.s.description = description
      self.s.host = hostname
      self.s.format = music_format # vorbis OR mp3
      if(ogv==1):
         self.s.format = vorbis
      self.s.port = port
      self.s.password = password
      self.s.mount = channel_mount
      self.s.url = station_url
      self.s.genre = genre
      print self.s.open()
      self.jingle_dir = jingle_dir
      self.music_directory = music_directory
      
      threading.Thread.__init__ (self)
   def scan_directories_ogv(self):
      if (len(self.jingle_dir)>1):
         print "jingle dir: "+self.jingle_dir
         self.jingle_files = glob(self.jingle_dir+"/*.[oO][gG][vV]")
      # only 3-depth !!!!!!!!!!!!!!!!!!!
      self.files_array = glob(self.music_directory+"/*.[oO][gG][vV]")  + glob(self.music_directory+"/*/*.[oO][gG][vV]") + glob(self.music_directory+"/*/*/*.[oO][gG][vV]")
      print str(len(self.files_array))+" files"
      shuffle(self.files_array) # random playlist, if you dont like - comment
      
   def scan_directories(self):
      if (len(self.jingle_dir)>1):
         print "jingle dir: "+self.jingle_dir
         self.jingle_files = glob(self.jingle_dir+"/*.[mM][Pp]3")
      # only 3-depth !!!!!!!!!!!!!!!!!!!
      self.files_array = glob(self.music_directory+"/*.[mM][Pp]3")  + glob(self.music_directory+"/*/*.[mM][Pp]3") + glob(self.music_directory+"/*/*/*.[mM][Pp]3")
      print str(len(self.files_array))+" files"
      shuffle(self.files_array) # random playlist, if you dont like - comment
      
   def run (self):
      global jingle_after
      while 1: #infinity
         if(self.ogv==0):
            self.scan_directories() # rescan dir, maybe in time you add some new songs
         else:
            self.scan_directories_ogv() #scan movies
         self.song_counter = 0   
         for e in self.files_array:
            self.write_future()
            self.sendfile(e)
            self.song_counter = self.song_counter + 1
            if(self.song_counter%jingle_after==0):
               self.sendfile(choice(self.jingle_files)) # play random jingle/movieclip
         
   def format_songname(self,song): # format song name - on filename (strip "mp3", change _ to " ". You can add here some mp3 tag reader library
      result = song.split("/")[-1].split(".")
      result = ".".join(result[:len(result)-1]).replace("_"," ").replace("-"," - ")
      return result
      
   def write_future(self): #write playlist
      filename = self.s.mount.replace("/","")+"-current.txt"
      fa = open(filename,"w")
      aid = self.song_counter
      pos = 7 # CHANGE if you want more songs in future playlist
      for s in self.files_array[aid:]:
         fa.write(self.format_songname(s)+"\n")
         pos = pos - 1
         if (pos==0):
            break
      if (pos>0):
         for s in self.files_array[:pos+1]:
            fa.write(self.format_songname(s)+"\n")
      fa.close()   
         
   def sendfile(self,fa):
      print "opening file %s" % fa
      
      f = open(fa)
      self.s.set_metadata({'song': self.format_songname(fa)})
      nbuf = f.read(4096)
      while 1:
         buf = nbuf
         nbuf = f.read(4096)
         if len(buf) == 0:
            break
         self.s.send(buf)
         self.s.sync()
      f.close()


# run stream with bitrate 128
RunStream(channel_mount="/stream",music_directory="/home/user/mp3",station_url="http://music.com",genre="tekno, hardcore, tribe, mental",name="my radiostation",description="some desc",jingle_dir=jingles).start()


# run another stream with bitrate 128
RunStream(channel_mount="/stream23",music_directory="/home/user/mp3_classics",station_url="http://music.com",genre="tekno, hardcore, tribe, mental",name="my radiostation",description="some desc",jingle_dir=jingles).start()


#run copy of stream with bitrate 64
RunStream(channel_mount="/stream2",music_directory="/home/user/mp3",station_url="http://music.com",genre="tekno, hardcore, tribe, mental",name="my radiostation",description="some desc",jingle_dir=jingles,bitrate="64").start()

#run same stream with bitrate 256
RunStream(channel_mount="/stream3",music_directory="/home/user/mp3",station_url="http://music.com",genre="tekno, hardcore, tribe, mental",name="my radiostation",description="some desc",jingle_dir=jingles,bitrate="256").start()

#run movie stream
#playing ogv (theora format) movies from /home/user/ogv and advertisements from $HOME/adv
RunStream(channel_mount="/television.ogv",music_directory="/home/user/ogv",station_url="http://tv.com",genre="melodrama",name="my tv station",description="some desc",jingle_dir="/home/user/adv",ogv=1).start()
