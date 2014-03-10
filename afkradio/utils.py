from afkradio.models import Songs, Types
from afkradio.models import MPD_DB_ROOT
from afkradio.errors import *
import fnmatch
import os
import subprocess

class Playback:
	def __init__(self):
		proc = subprocess.Popen(["mpc", "play"], stdout=subprocess.PIPE)


	@staticmethod
	def mpc_play():
		proc = subprocess.Popen(["mpc", "play"], stdout=subprocess.PIPE)
		return "Played mpc"

	@staticmethod
	def mpc_stop():
		proc = subprocess.Popen(["mpc", "stop"], stdout=subprocess.PIPE)
		return "Stopped mpc"

	@staticmethod 
	def mpc_clear():
		proc = subprocess.Popen(["mpc", "clear"], stdout=subprocess.PIPE)
		return "Cleared mpc playlist"

	@staticmethod 
	def mpc_crop():
		proc = subprocess.Popen(["mpc", "crop"], stdout=subprocess.PIPE)
		return "Cleared mpc playlist except currently playing song"

	@staticmethod
	def mpc_update():
		proc = subprocess.Popen(["mpc", "update"], stdout=subprocess.PIPE)
		return "Scanned MPD root and updated MPD db (NOT models.Songs DB)"

	@staticmethod
	def mpc_add(song_path):
		proc = subprocess.Popen(["mpc", "add", song_path])
		return "Added " + song_path + " to the playlist"

	@staticmethod
	def mpc_currently_playing():
		proc = subprocess.Popen(["mpc"], stdout=subprocess.PIPE)
		line = proc.stdout.readline()
		if line.startswith("volume: n/a"):
			return "No song is currently playing"
		else:
			return line

class Database:
	# update_songs_db
	# First runs mpc_update to update the mpd music database
	# Then it will read from the mpd music root defined in afkradio.models for any
	# .mp3, .ogg, and .flac music files and add them with their respective metadata
	# to the Songs model
	@staticmethod
	def update_songs_db():
		Playback.mpc_update()
		dupe_list = []
		matches = []
		supported_file_types = ('mp3', 'ogg', 'flac')
		for root, dirs, files in os.walk(MPD_DB_ROOT):
			for extension in supported_file_types:
				for filename in fnmatch.filter(files, '*.' + extension):
					# Get relative path of song from MPD_DB_ROOT
					song_path = os.path.relpath(os.path.join(root, filename), MPD_DB_ROOT)
					try:
						Songs.add_song_exiftool(song_path, None)
					except DuplicateEntryError:
						dupe_list.append(os.path.join(root, filename))
		if dupe_list is not []:
			return dupe_list
