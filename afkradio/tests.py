from django.test import TestCase
from afkradio.models import Songs, Types
from django.utils import timezone
from afkradio.utils import Playback
import datetime

class ModelSongsMethodTests(TestCase):
	def test_add_song_exiftool_test_song(self):
		"""
		Tests if we can add a new song to the database as well as
		getting the corresponding metadata using exiftool
		"""
		Songs.add_song_exiftool(
			"Test Path/test.mp3",
			"Test_Extra"
		)
		new_song = Songs.objects.get(year=1111)
		self.assertEqual(
				timezone.now()-datetime.timedelta(seconds=5) < new_song.date_added,
				True
				)
		metadata_dict = {
				'Test_Title' : 'title',
				'Test_Artist' : 'artist',
				'Test_Album' : 'album',
				1111 : 'year',
				'0:04:13' : 'duration',
				'Test Path/test.mp3' : 'filepath',
				'Test_Extra' : 'extra',
				} 
		for metadata_entry in metadata_dict.keys():
			self.assertEqual(
					getattr(new_song, metadata_dict[metadata_entry]),
					metadata_entry,
					)

	def test_add_song_exiftool_nonexistant_song(self):
		"""
		Tests handling of add_song_exiftool if the song in the path 
		does not exist
		"""
		Songs.add_song_exiftool(
			"this folder path/doesn't exist.mp3",
			"Test_Extra",
		)
		self.assertQuerysetEqual(Types.objects.all(), [])
	
	def test_add_song_exiftool_nonsupported_format(self):
		"""
		Tests handling of add_song_exiftool if the songi n the path
		is not a supported file type
		"""
		Songs.add_song_exiftool(
			"Test Path/exiftool",
			"Test_Extra",
		)
		self.assertQuerysetEqual(Types.objects.all(), [])

class ModelTypesMethodTests(TestCase):
	def test_add_type(self):
		"""
		Test if a new type can be added with add_types() function
		"""
		Types.add_type('add_test')
		self.assertQuerysetEqual(Types.objects.all(),['<Types: add_test>'])

	def test_add_type_with_same_entry(self):
		"""
		Test if a new type can be added with add_types() function
		"""
		Types.add_type('add_test')
		Types.add_type('add_test')
		self.assertQuerysetEqual(list(Types.objects.all()),['<Types: add_test>'])

	def test_add_type_multiple_entries(self):
		"""
		Test if a new type can be added with add_types() function
		"""
		Types.add_type('add_test1')
		Types.add_type('add_test2')
		self.assertQuerysetEqual(list(Types.objects.all()),[
			'<Types: add_test1>', 
			'<Types: add_test2>',
			])

	def test_remove_type_single_entry(self):
		"""
		Test if a type can be removed with remove_types() function
		"""
		Types.add_type('remove_test')
		self.assertQuerysetEqual(Types.objects.all(),['<Types: remove_test>'])
		Types.remove_type('remove_test')
		self.assertQuerysetEqual(Types.objects.all(),[])

	def test_remove_type_nonexistant_entry(self):
		"""
		Test if a type that doesn't can attempt to be removed with 
		remove_types() function
		"""
		self.assertQuerysetEqual(Types.objects.all(),[])
		Types.remove_type('remove_test')
		self.assertQuerysetEqual(Types.objects.all(),[])


	def test_remove_type_multiple_entry(self):
		"""
		Test if multiple types can be removed with remove_types() function
		"""
		Types.add_type('remove_test1')
		Types.add_type('remove_test2')
		self.assertQuerysetEqual(list(Types.objects.all()),[
			'<Types: remove_test1>', 
			'<Types: remove_test2>',
			])
		Types.remove_type('remove_test1')
		self.assertQuerysetEqual(list(Types.objects.all()),[
			'<Types: remove_test2>'
			])
		Types.remove_type('remove_test2')
		self.assertQuerysetEqual(Types.objects.all(),[])

class UtilPlaybackMethodTests(TestCase):
# 	def test_mpc_play(self):
# 		"""
# 		Test is mpc_play that plays a song in MPC works.
# 		"""
# 		Playback.mpc_play()
# 
# 	def test_mpc_stop(self):
# 		"""
# 		Test is mpc_stop that stops MPC works.
# 		"""
# 		Playback.mpc_stop()
	def test_mpc_play_from_song_added_to_Songs(self):
		"""
		Clears the current playlist, adds test song /MPD_ROOT/Test Path/test.mp3
		to models.Songs, adds the song to mpc, then plays it
		"""
		Songs.add_song_exiftool(
			"Test Path/test.mp3",
			"Test_Extra"
		)
		test_song = Songs.objects.get(id=1)
		Playback.mpc_clear()
		Playback.mpc_add(test_song.filepath)
		Playback.mpc_play()


