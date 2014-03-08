from django.test import TestCase
from afkradio.models import Songs, Types
from django.utils import timezone
import datetime

class SongsMethodTests(TestCase):
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

class TypesMethodTests(TestCase):
	def test_add_types(self):
		"""
		Test if a new type can be added with add_types() function
		"""
		Types.add_types('add_test')
		self.assertQuerysetEqual(Types.objects.all(),['<Types: add_test>'])

	def test_add_types_with_same_entry(self):
		"""
		Test if a new type can be added with add_types() function
		"""
		Types.add_types('add_test')
		Types.add_types('add_test')
		self.assertQuerysetEqual(list(Types.objects.all()),['<Types: add_test>'])

	def test_add_types_multiple_entries(self):
		"""
		Test if a new type can be added with add_types() function
		"""
		Types.add_types('add_test1')
		Types.add_types('add_test2')
		self.assertQuerysetEqual(list(Types.objects.all()),[
			'<Types: add_test1>', 
			'<Types: add_test2>',
			])

	def test_remove_types_single_entry(self):
		"""
		Test if a type can be removed with remove_types() function
		"""
		Types.add_types('remove_test')
		self.assertQuerysetEqual(Types.objects.all(),['<Types: remove_test>'])
		Types.remove_types('remove_test')
		self.assertQuerysetEqual(Types.objects.all(),[])

	def test_remove_types_nonexistant_entry(self):
		"""
		Test if a type that doesn't can attempt to be removed with 
		remove_types() function
		"""
		self.assertQuerysetEqual(Types.objects.all(),[])
		Types.remove_types('remove_test')
		self.assertQuerysetEqual(Types.objects.all(),[])


	def test_remove_types_multiple_entry(self):
		"""
		Test if multiple types can be removed with remove_types() function
		"""
		Types.add_types('remove_test1')
		Types.add_types('remove_test2')
		self.assertQuerysetEqual(list(Types.objects.all()),[
			'<Types: remove_test1>', 
			'<Types: remove_test2>',
			])
		Types.remove_types('remove_test1')
		self.assertQuerysetEqual(list(Types.objects.all()),[
			'<Types: remove_test2>'
			])
		Types.remove_types('remove_test2')
		self.assertQuerysetEqual(Types.objects.all(),[])


