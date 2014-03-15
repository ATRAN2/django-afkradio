from django.db import models
from django.utils import timezone
from afkradio.errors import *
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
import random
import json
import os
import subprocess

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(APP_ROOT,'config.json')) as config_file:
	config_data = json.load(config_file)
	MPD_DB_ROOT = config_data['MPD DB root']


# Songs Model
# Store Songs as well as their metadata here
# title is Song Title
# artist is Song Artist
# album is Song Album
# year is Year the song was released
# duration is Duration of the song in H:MM:SS
# filepath is the path to the song in relation to the mpd song db root
# 	(i.e. if the root of the mpd is '~/mpd_music'
# 	the song is located in '~/mpd_music/album/artist/example.mp3'
# 	then filepath would be '/album/artist/example.mp3'
# date_added is the date the song was added to the database
# extra is for any other extra data or tags to aid in searching
class SongManager(models.Manager):
	def check_if_exists(self, song_query, field=id):
		try: 
			song_check = self.filter(**{field:song_query})
		except FieldError:
			raise FieldNotFoundError('The field ' + field + ' does not exist in the Songs model')
			return False
		if song_check:
			return True
		else:
			raise SongNotFoundError('The song with the ' + field + ' ' + song_query +
				' does not exist')
			return False
	
	def check_if_id_exists(self, song_id):
		try:
			self.get(id=song_id)
			return True
		except Song.DoesNotExist:
			raise SongNotFoundError('The song with the id ' + song_id +
				' does not exist')
			return False
	
	def get_random(self):
		if self.count():
			last = self.count() - 1
			index = random.randint(0, last)
			return self.all()[index]
		else:
			raise SongNotFoundError( 'There are no songs in the database yet. Please click ' + \
				'Update Database in the admin panel or run Control.scan_for_songs() in ' + \
				' afkradio.utils from the shell' )
			return False

	def get_random_from_active_types(self):
		active_songs = list(Type.objects.song_ids_of_active_types())
		if not active_songs or not active_songs[0]:
			raise SongNotFoundError( 'There are no songs associated to the active types' )
			return False
		else:
			active_song_count = len(active_songs)
			index = random.randint(0,active_song_count-1)
			random_active_song_id = active_songs[index]
			return self.get(id=random_active_song_id)


class Song(models.Model):
	title = models.CharField(max_length=200, blank=True)
	artist = models.CharField(max_length=200, blank=True)
	album = models.CharField(max_length=200, blank=True)
	year = models.CharField(max_length=20, blank=True)
	duration = models.CharField(max_length=20, blank=True)
	filepath = models.CharField(max_length=500, blank=True)
	date_added = models.DateTimeField('Date Added', null=True, blank=True)
	extra = models.CharField(max_length=500, blank=True)
	times_played = models.PositiveIntegerField(default=0)
	times_faved = models.PositiveIntegerField(default=0)
	objects = SongManager()

	# add_song_exiftool method
	# Given the song path relative MPD_DB_ROOT, runs exiftool
	# on the song and adds the song to the database with existing
	# metadata
	@classmethod
	def add_song_exiftool(cls, rel_song_path, extra=None):
		# First check if MPD Root is set
		if MPD_DB_ROOT == '':
			raise MPDRootNotFound()
			return
		# Get absolute path of song
		abs_song_path = os.path.join(MPD_DB_ROOT, rel_song_path)
		# First check if the file is a duplicate
		if cls.objects.filter(filepath=rel_song_path):
			raise DuplicateEntryError("There is already a song with the same path in the database: " +
					abs_song_path)
			return abs_song_path
		# Create our new song instance and tie fields to variables
		new_song = cls()
		# Get absolute path of song
		abs_song_path = os.path.join(MPD_DB_ROOT, rel_song_path)
		# List supported file types in supporteD_file_types
		supported_file_types = ('MP3', 'OGG', 'FLAC',)
		# Dict of metadata that we want from exiftool and corresponding fields
		# Keys are exiftool labels for the metadata
		# Values are the corresponding field names of our new Songs model object
		metadata_dict = {
				'Title' : 'title',
				'Album' : 'album',
				'Year' : 'year',
				'Artist' : 'artist',
				'Duration' : 'duration',
				}
		# Run exiftool on the song
		proc = subprocess.Popen([APP_ROOT + '/exiftool/exiftool', abs_song_path],
				 stderr = subprocess.STDOUT,
				 stdout = subprocess.PIPE)
		while True:
			line = proc.stdout.readline()
			# Halt if no file was found in the rel_song_path
			if line.startswith('File not found'):
				raise FileNotFoundError("File not found: " + abs_song_path)
				return abs_song_path
			# Halt if the file is not a supported file type
			elif line.startswith('File Type'):
				colon_index = line.find(':')
				exiftool_metadata_contents = line[(colon_index+2):-1]
				file_type = exiftool_metadata_contents
				if file_type not in supported_file_types:
					raise FileTypeError(
						'Not a supported file type. "' + file_type + '" is not ' 
						+ str(supported_file_types)
					)
					return abs_file_path
			elif line !='':
				# Get any metadata we can find from the song that's one of the
				# metadata entries defined in metadata_dict
				for metadata_entry in metadata_dict.keys():
					if line.startswith(metadata_entry):
						colon_index = line.find(':')
						exiftool_metadata_contents = line[(colon_index+2):-1]
						# Set field to the exiftool metadata we found
						setattr(new_song, metadata_dict[metadata_entry],
								exiftool_metadata_contents)
			else:
				break
		# exiftool has (approx) after duration.  Let's get rid of it
		if new_song.artist == 'volume: n/a   repeat:':
			return "'volume: n/a   repeat:' is an invalid artist.  " + \
					"Please don't try to break the stream"
		if new_song.duration is not None:
			new_song.duration = new_song.duration[0:7]
		# Add file path data
		new_song.filepath = rel_song_path
		# Add Date Added data
		new_song.date_added = timezone.now()
		# Add extra data if we got some
		if extra is not None and not '':
			new_song.extra = extra
		new_song.save()

	def __unicode__(self):
		try:
			return self.title
		except TypeError:
			return 'Empty title field'

# Types Model
# Available Types to associate with songs are stored here.
# Types are created and associated with songs in order to have
# song subsets.  Types can be activated in afkradio to limit
# the types of songs selected when shuffled (i.e. If only 
# fast songs are desired select the corresponding types
# and so slow songs will creep in due to shuffle). Both type
# selection and type association will be handled by users.
class TypeManager(models.Manager):
	def check_if_exists(self, check_type):
		try:
			type_to_check = self.get(type=check_type)
			return True
		except Type.DoesNotExist:
			raise TypeNotFoundError('The Type with the type ' + check_type + \
				' does not exist')
			return False

	def activate_type(self, type_to_activate):
		if self.check_if_exists(type_to_activate):
			type_to_activate = self.get(type=type_to_activate)
			type_to_activate.active = True
			type_to_activate.save()

	def deactivate_type(self, type_to_deactivate):
		if self.check_if_exists(type):
			type_to_deactivate = self.get(type=type_to_deactivate)
			type_to_deactivate.active = False
			type_to_deactivate.save()

	def inactive_types(self):
		return self.filter(active=False)
	
	def active_types(self):
		return self.filter(active=True)

	def song_ids_of_active_types(self):
		return self.filter(active=True).values_list('associated_songs', flat=True).distinct()

class Type(models.Model):
	type = models.CharField(max_length=50)
	associated_songs = models.ManyToManyField(Song)
	active = models.BooleanField(default=False)
	objects = TypeManager()
	
	@classmethod
	def add_type(cls, new_type):
		new_type_exists = cls.objects.filter(type=new_type)
		if new_type_exists:
			return 'Type already exists'
		else:
			add_type = cls(type=new_type)
			add_type.save()
			return 'Type ' + new_type + ' added to types'

	@classmethod
	def remove_type(cls, remove_type):
		remove_type_exists = cls.objects.filter(type=remove_type)
		if remove_type_exists:
			remove_type_exists.delete()
			return 'Type ' + remove_type + ' removed from types'


	def __unicode__(self):
		return self.type

class Timer(models.Model):
	function = models.CharField(max_length=50)
	user = models.CharField(max_length=75, blank=True)
	votes = models.CharField(max_length=5, blank=True)
	create_time = models.DateTimeField('Create time')
	expire_time = models.DateTimeField('Expire time')

class PlayHistoryManager(models.Manager):
	def clear_playhistory(self):
		self.all().delete()

class PlayHistory(models.Model):
	song_id = models.CharField(max_length=16)
	played_time = models.DateTimeField('Time Played')
	
	@classmethod
	def add_song(cls, new_song_id, set_played_time):
		new_song = cls(song_id = new_song_id, played_time = set_played_time)
		new_song.save()

	def __unicode__(self):
		return self.song_id

class PlaylistManager(models.Manager):

	# Get current song with precedence to user_requested songs
	def current_song(self):
		try:
			current_song = self.order_by('-user_requested', 'add_time')[0]
			return current_song
		except Playlist.DoesNotExist:
			raise SongNotFoundError('There are no songs in the Playlist')
			return False

	# Get next song with precedence to user_requested songs
	def next_song(self):
		try:
			next_song = self.order_by('-user_requested', 'add_time')[1]
			return next_song
		except Playlist.DoesNotExist:
			raise SongNotFoundError('Next song does not exist in the Playlist')
			return False

	def clear_playlist_full(self):
		self.all().delete()

	def clear_playlist_retain_requested(self):
		self.filter(user_requested=False).delete()

	def queue_sorted(self):
		return self.order_by('-user_requested', 'add_time')


class Playlist(models.Model):
	song_id = models.CharField(max_length=16)
	add_time = models.DateTimeField('Add Time')
	user_requested = models.BooleanField(default=False)
	objects = PlaylistManager()

	def song_title(self):
		return Song.objects.get(id=self.song_id).title

	@classmethod
	def add_song(cls, new_song_id, requested=False):
		new_song = cls(
				song_id = new_song_id,
				add_time = timezone.now(),
				user_requested = requested,
				)
		new_song.save()
	
	def __unicode__(self):
		return self.song_id

