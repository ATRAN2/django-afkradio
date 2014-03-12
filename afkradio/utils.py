from afkradio.models import Songs, Types, PlayHistory, Playlist
from afkradio.errors import *
import json
import fnmatch
import os
import subprocess

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(APP_ROOT,'config.json')) as config_file:
	config_data = json.load(config_file)
	MPD_DB_ROOT = config_data['MPD DB root']
	PLAYLIST_SIZE = config_data['Playlist size']

class Playback:

	# mpc_run is the main Playback method that will run mpc, and keep it
	# persistently listening to commands with mpc idle
	@staticmethod
	def mpc_run(init=True):
		if init:
			for song_count in PLAYLIST_SIZE:
				random_song = Songs.get_random()
				Playlist.add_song(random_song.id)
				mpc_add(random_song.filepath)
		mpc_play()
		# Add played song to PlayHistory
		PlayHistory.add_song(Playlist.current_song().song_id, timezone.now())
		proc = subprocess.Popen(["mpc", "idle"], stdout=subprocess.PIPE)
		line = proc.stdout.readline()
		while True:
			if line == '':
				continue
			else:
				if line == 'player':
					check_state = subprocess.Popen(["mpc"], stdout=subprocess.PIPE)
					state_line = check_state.stdout.readline()
					if state_line.startswith('volume: n/a   repeat:'):
						return
					else:
						Playlist.current_song().delete()
						PlayHistory.add_song(Playlist.current_song().song_id, timezone.now())
						random_song = Songs.get_random()
						Playlist.add_song(random_song.id)
						mpc_delete(1)
						mpc_add(random_song.filepath)
						mpc_run(False)
				elif line == 'playlist':
					print 'Placeholder'


	@staticmethod
	def mpc_play():
		proc = subprocess.Popen(["mpc", "play"])
		return "Played mpc"

	@staticmethod
	def mpc_stop():
		proc = subprocess.Popen(["mpc", "stop"])
		return "Stopped mpc"

	@staticmethod 
	def mpc_clear():
		proc = subprocess.Popen(["mpc", "clear"])
		return "Cleared mpc playlist"

	@staticmethod 
	def mpc_crop():
		proc = subprocess.Popen(["mpc", "crop"])
		return "Cleared mpc playlist except currently playing song"

	@staticmethod
	def mpc_update():
		proc = subprocess.Popen(["mpc", "update"])
		return "Scanned MPD root and updated MPD db (NOT models.Songs DB)"

	@staticmethod
	def mpc_add(song_path):
		proc = subprocess.Popen(["mpc", "add", song_path])
		return "Added " + song_path + " to the playlist"

	@staticmethod
	def mpc_delete(song_position=1):
		proc = subprocess.Popen(["mpc", "del", song_position])
		return "Deleted the song in position " + song_position + " of the playlist"

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
		if MPD_DB_ROOT == '':
			raise MPDRootNotFound()
			return
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

	@staticmethod
	# associate_type_to_song
	# Associates a Song in Song.models to a Type in Type.models
	def associate_type_to_song(song_id, type):
		# Check if the type exists
		if Types.objects.check_if_exists(type) is True:
			type_to_associate = Types.objects.get(types=type)
		else:
			return type
		# Check if the Song exists
		if Songs.objects.check_if_id_exists(song_id) is True:
			song_to_associate = Songs.objects.get(id=song_id)
		else:
			return song_id
		type_to_associate.associated_songs.add(song_to_associate)

	@staticmethod
	def dissociate_type_to_song(song_id, type):
		# Check if the type exists
		if Types.objects.check_if_exists(type) is True:
			type_to_dissociate = Types.objects.get(types=type)
		else:
			return type
		# Check if the Song exists
		if Songs.objects.check_if_id_exists(song_id) is True:
			song_to_dissociate = Songs.objects.get(id=song_id)
		else:
			return song_id
		type_to_dissociate.associated_songs.remove(song_to_dissociate)
	
class Config:
	# Edits config.json file with new values. Takes a list that has values that
	# correspong to: [MPD db root, ]
	@staticmethod
	def config_write(new_config):
		# Set default values
		if new_config[0] == '':
			return	
	

	

