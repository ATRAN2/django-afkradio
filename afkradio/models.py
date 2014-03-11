from django.db import models
from django.utils import timezone
from afkradio.errors import *
import os
import subprocess

MPD_DB_ROOT = '/home/reinforce/music/'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

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
class SongsManager(models.Manager):
	def check_if_exists(self, song_query, field=id):
		try: 
			song_check = self.filter(field=song_query)
		except FieldError:
			raise FieldDoesNotExistError('The field ' + field + ' does not exist in the Songs model')
			return False
		if song_check is not []:
			return True
		else:
			raise SongDoesNotExistError('The song with the ' + field + ' ' + song_query +
				' does not exist')
			return False
	
	def check_if_id_exists(self, song_id):
		try:
			self.get(id=song_id)
			return True
		except Songs.DoesNotExist:
			raise SongNotFoundError('The song with the id ' + song_id +
				' does not exist')
			return False

class Songs(models.Model):
	title = models.CharField(max_length=200, blank=True)
	artist = models.CharField(max_length=200, blank=True)
	album = models.CharField(max_length=200, blank=True)
	year = models.CharField(max_length=20, blank=True)
	duration = models.CharField(max_length=20, blank=True)
	filepath = models.CharField(max_length=500, blank=True)
	date_added = models.DateTimeField('Date Added', null=True, blank=True)
	extra = models.CharField(max_length=500, blank=True)
	objects = SongsManager()

	# add_song_exiftool method
	# Given the song path relative MPD_DB_ROOT, runs exiftool
	# on the song and adds the song to the database with existing
	# metadata
	@classmethod
	def add_song_exiftool(cls, rel_song_path, extra=None):
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
					raise FileTypeError('Not a supported file type. "' + file_type + '" is not ' + str(supported_file_types))
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
class TypesManager(models.Manager):
	def check_if_exists(self, type):
		try:
			type_to_check = self.get(types=type)
			return True
		except Types.DoesNotExist:
			raise TypeNotFoundError('The Type with the type ' + type +
				' does not exist')
			return False

class Types(models.Model):
	types = models.CharField(max_length=50)
	associated_songs = models.ManyToManyField(Songs)
	objects = TypesManager()
	
	@classmethod
	def add_type(cls, new_type):
		new_type_exists = cls.objects.filter(types=new_type)
		if new_type_exists:
			return 'Type already exists'
		else:
			add_type = cls(types=new_type)
			add_type.save()
			return 'Type ' + new_type + ' added to types'

	@classmethod
	def remove_type(cls, remove_type):
		remove_type_exists = cls.objects.filter(types=remove_type)
		if remove_type_exists:
			remove_type_exists.delete()
			return 'Type ' + remove_type + ' removed from types'


	def __unicode__(self):
		return self.types


# class PlayHistory(model.Model):

# class Playlist(model.Model):
