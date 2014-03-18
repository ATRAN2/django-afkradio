from afkradio.models import Song, Setlist, PlayHistory, Playlist
from afkradio.errors import *
from django.utils import timezone
from time import sleep
import logging
import json
import fnmatch
import os
import subprocess

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(APP_ROOT,'config.json')) as config_file:
	config_data = json.load(config_file)
	MPD_DB_ROOT = config_data['MPD DB root']
	PLAYLIST_SIZE = config_data['Playlist size']

check_os = os.name
if check_os == 'posix':
	NULL_DEVICE = open('/dev/null', 'w')
elif check_os == 'nt':
	NULL_DEVICE = open('nul', 'w')
else:
	print 'Not a supported system'
	exit()
		


class Playback:

	@staticmethod
	def mpc_play():
		proc = subprocess.Popen(["mpc", "play"], stdout=NULL_DEVICE).wait()
		return "Played mpc"

	@staticmethod
	def mpc_stop():
		proc = subprocess.Popen(["mpc", "stop"], stdout=NULL_DEVICE).wait()
		return "Stopped mpc"

	@staticmethod 
	def mpc_clear():
		proc = subprocess.Popen(["mpc", "clear"], stdout=NULL_DEVICE).wait()
		return "Cleared mpc playlist"

	@staticmethod 
	def mpc_crop():
		proc = subprocess.Popen(["mpc", "crop"], stdout=NULL_DEVICE).wait()
		return "Cleared mpc playlist except currently playing song"

	@staticmethod
	def mpc_update():
		proc = subprocess.Popen(["mpc", "update"], stdout=NULL_DEVICE).wait()
		return "Scanned MPD root and updated MPD db (NOT models.Song DB)"

	@staticmethod
	def mpc_add(song_path):
		proc = subprocess.Popen(["mpc", "add", song_path], stdout=NULL_DEVICE).wait()
		return "Added " + song_path + " to the playlist"

	@staticmethod
	def mpc_delete(song_position=1):
		proc = subprocess.Popen(["mpc", "del", str(song_position)], stdout=NULL_DEVICE).wait()
		return "Deleted the song in position " + str(song_position) + " of the playlist"

	@staticmethod
	def mpc_currently_playing():
		proc = subprocess.Popen(["mpc"], stdout=subprocess.PIPE)
		line = proc.stdout.readline()
		if line.startswith("volume: n/a"):
			return "No song is currently playing"
		else:
			return line[0:-1].decode('utf-8')

class Database:
	# update_song_db
	# First runs mpc_update to update the mpd music database
	# Then it will read from the mpd music root defined in afkradio.models for any
	# .mp3, .ogg, and .flac music files and add them with their respective metadata
	# to the Songs model

	@staticmethod
	def update_song_db():
		dupe_list = []
		matches = []
		supported_file_types = ('mp3', 'ogg', 'flac')
		if MPD_DB_ROOT == '':
			raise MPDRootNotFound()
			return []
		for root, dirs, files in os.walk(MPD_DB_ROOT):
			for extension in supported_file_types:
				for filename in fnmatch.filter(files, '*.' + extension):
					# Get relative path of song from MPD_DB_ROOT
					song_path = os.path.relpath(os.path.join(root, filename), MPD_DB_ROOT)
					try:
						Song.add_song_exiftool(song_path, None)
					except DuplicateEntryError:
						dupe_list.append(os.path.join(root, filename))
		return dupe_list
		
	@staticmethod
	# associate_setlist_to_song
	# Associates a Song in Song.models to a Setlist in Setlist.models
	def associate_setlist_to_song(song_id, associate_setlist):
		# Check if the setlist exists
		if Setlist.objects.check_if_exists(associate_setlist) is True:
			setlist_to_associate = Setlist.objects.get(setlist=associate_setlist)
		else:
			return associate_setlist
		# Check if the Song exists
		if Song.objects.check_if_id_exists(song_id) is True:
			song_to_associate = Song.objects.get(id=song_id)
		else:
			return song_id
		setlist_to_associate.associated_songs.add(song_to_associate)

	@staticmethod
	def dissociate_setlist_to_song(song_id, dissociate_setlist):
		# Check if the setlist exists
		if Setlist.objects.check_if_exists(dissociate_setlist) is True:
			setlist_to_dissociate = Setlist.objects.get(setlist=dissociate_setlist)
		else:
			return dissociate_setlist
		# Check if the Song exists
		if Song.objects.check_if_id_exists(song_id) is True:
			song_to_dissociate = Song.objects.get(id=song_id)
		else:
			return song_id
		setlist_to_dissociate.associated_songs.remove(song_to_dissociate)

# Most of the high level functionality is contained in the Control class
class Control:
	# Gets a random song from any song that has a setlist that's active
	# Can be set to False which will get a song from complete random
	@staticmethod
	def add_random_song(from_setlists=True):
		if from_setlists:
			random_song = Song.objects.get_random_from_active_setlists()
			log_setlisted = 'from setlists '
			if not random_song:
				try:
					if not Setlist.objects.active_setlists():
						raise SetlistNotFoundError('No Setlists are currently active. ' + \
							'Ignoring setlists and playing a random song instead')
					else:
						raise SongNotFoundError('No songs associated to set active ' + \
							'setlists.  Ignoring setlists and playing a random song instead')
				except (SetlistNotFoundError, SongNotFoundError):
					random_song = Song.objects.get_random()
					log_setlisted = ''
		else:
			random_song = Song.objects.get_random()
			log_setlisted = ''
		if random_song:
			Playlist.add_song(random_song.id)
			Playback.mpc_add(random_song.filepath)
			logging.info('Random song ' + log_setlisted + random_song.title + \
					' (Song ID: ' + str(random_song.id) + ') has been added ' + \
					'to the playlist.  Filepath: ' + random_song.filepath)
		else:
			# No songs in the database
			exit()
	
	@staticmethod
	def scan_for_songs():
		Playback.mpc_update()
		dupe_list = Database.update_song_db()
		logging.info('Scanned MPC root and updated Songs model and MPC playlist')
		return dupe_list

# 	@staticmethod
# 	def request_song(song_id):
		

	# run_stream is the main stream method that will run mpc and keep it
	# persistently listening to commands with mpc idle.  It plays songs in
	# activated setlists by default, but if no setlists are active, then it will
	# play from all songs
	@staticmethod
	def run_stream(init=True, from_setlists=True):
		logging.info('Stream has been initiated')
		if init:
			Playback.mpc_clear()
			Playlist.objects.clear_playlist_full()
			for song_count in range(int(PLAYLIST_SIZE)):
				Control.add_random_song(from_setlists)
		Playback.mpc_play()
		# Add played song to PlayHistory
		PlayHistory.add_song(Playlist.objects.current_song().song_id, timezone.now())
		while True:
			proc = subprocess.Popen(["mpc", "idle"], stdout=subprocess.PIPE)
			sleep(0.5)
			line = proc.stdout.readline()
			while True:
				if line[0:-1] == 'player':
					check_state = subprocess.Popen(["mpc"], stdout=subprocess.PIPE)
					state_line = check_state.stdout.readline()
					if state_line.startswith('volume: n/a   repeat:'):
						return
					else:
						Playlist.objects.current_song().delete()
						new_song_id = Playlist.objects.current_song().song_id
						logging.info('Played ' + Playback.mpc_currently_playing() + \
								'(Song ID: ' + new_song_id + ')')
						PlayHistory.add_song(new_song_id, timezone.now())
						Control.add_random_song()
						Playback.mpc_delete(1)
						break
				else:
					continue
	
class Config:
	# Edits config.json file with new values. Takes a list that has values that
	# correspong to: [MPD db root, ]
	@staticmethod
	def config_write(new_config):
		# Set default values
		if new_config[0] == '':
			return	
	

	

