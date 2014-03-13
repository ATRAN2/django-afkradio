from django.test import TestCase
from afkradio.models import Songs, Types
from django.utils import timezone
from afkradio.utils import Playback, Database, Playlist, PlayHistory
from afkradio.errors import *
import datetime
import time

# If you want to run these tests, then please place the folder 'Test Path' located
# in the app root into your MPD music root folder.

class ModelSongsMethodTests(TestCase):
	def test_add_song_exiftool_test_song(self):
		"""
		Tests if we can add a new song to the database as well as
		getting the corresponding metadata using exiftool
		"""
		Songs.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		new_song = Songs.objects.get(year='1111')
		self.assertTrue(timezone.now()-datetime.timedelta(seconds=5) < new_song.date_added)
		metadata_dict = {
				'Test_Title' : 'title',
				'Test_Artist' : 'artist',
				'Test_Album' : 'album',
				'1111' : 'year',
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
		Tests handling of add_song_exiftool() if the song in the path 
		does not exist
		"""
		with self.assertRaises(FileNotFoundError):
			Songs.add_song_exiftool("this folder path/doesn't exist.mp3")
		self.assertQuerysetEqual(Songs.objects.all(), [])
	
	def test_add_song_exiftool_nonsupported_format(self):
		"""
		Tests handling of add_song_exiftool() if the song in the path
		is not a supported file type
		"""
		with self.assertRaises(FileTypeError):
			Songs.add_song_exiftool("Test Path/exiftool")
		self.assertQuerysetEqual(Songs.objects.all(), [])

	def test_add_song_exiftool_same_song(self):
		"""
		Tests handling of add_song_exiftool() if the same song is added twice
		"""
		Songs.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		with self.assertRaises(DuplicateEntryError):
			Songs.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		self.assertQuerysetEqual(Songs.objects.all(), ['<Songs: Test_Title>'])

	def test_check_if_exists(self):
		Songs.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		self.assertTrue(Songs.objects.check_if_exists("Test_Title", 'title'))
		self.assertTrue(Songs.objects.check_if_exists("Test_Artist", 'artist'))
		with self.assertRaises(SongNotFoundError):
			Songs.objects.check_if_exists("Test_Album", 'extra')
		with self.assertRaises(SongNotFoundError):
			Songs.objects.check_if_exists("2222", 'year')
		with self.assertRaises(FieldNotFoundError):
			Songs.objects.check_if_exists("95328", 'NotAValidField')

	def test_check_if_id_exists(self):
		Songs.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		self.assertTrue(Songs.objects.check_if_id_exists("1"))
		with self.assertRaises(SongNotFoundError):
			Songs.objects.check_if_id_exists("2")

	def test_get_random(self):
		with self.assertRaises(FieldNotFoundError):
			Songs.objects.get_random()
		Database.update_songs_db()
		random_song = Songs.objects.get_random()
		self.assertTrue(Songs.objects.check_if_id_exists(random_song.id))



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
		self.assertQuerysetEqual(list(Types.objects.all()),
			['<Types: add_test1>', '<Types: add_test2>',])

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
		self.assertQuerysetEqual(list(Types.objects.all()),
			['<Types: remove_test1>', '<Types: remove_test2>',])
		Types.remove_type('remove_test1')
		self.assertQuerysetEqual(list(Types.objects.all()),
			['<Types: remove_test2>'])
		Types.remove_type('remove_test2')
		self.assertQuerysetEqual(Types.objects.all(),[])

class PlayHistoryMethodTests(TestCase):
	def test_add_song(self):
		PlayHistory.add_song('1', timezone.now())
		PlayHistory.add_song('2', timezone.now())
		new_song1 = PlayHistory.objects.get(song_id=1)
		self.assertTrue(timezone.now()-datetime.timedelta(seconds=5) < new_song1.played_time)
		self.assertQuerysetEqual(list(PlayHistory.objects.all()),
			['<PlayHistory: 1>', '<PlayHistory: 2>',])

class ModelPlaylistMethodTests(TestCase):
	def test_current_song_no_user_requested(self):
		Playlist.add_song('1')
		Playlist.add_song('2')
		Playlist.add_song('3')
		self.assertEqual(Playlist.objects.current_song().song_id, '1')

	def test_current_song_only_user_requested(self):
		Playlist.add_song('1', True)
		Playlist.add_song('2', True)
		Playlist.add_song('3', True)
		self.assertEqual(Playlist.objects.current_song().song_id, '1')

	def test_current_song_both_non_requested_and_one_requested(self):
		Playlist.add_song('1')
		Playlist.add_song('2')
		Playlist.add_song('3')
		Playlist.add_song('4', True)
		self.assertEqual(Playlist.objects.current_song().song_id, '4')

	def test_current_song_both_non_requested_and_requested(self):
		Playlist.add_song('1')
		Playlist.add_song('2')
		Playlist.add_song('3')
		Playlist.add_song('4', True)
		Playlist.add_song('5', True)
		Playlist.add_song('6', True)
		self.assertEqual(Playlist.objects.current_song().song_id, '4')

	def test_next_song_no_user_requested(self):
		Playlist.add_song('1')
		Playlist.add_song('2')
		Playlist.add_song('3')
		self.assertEqual(Playlist.objects.next_song().song_id, '2')

	def test_next_song_only_user_requested(self):
		Playlist.add_song('1', True)
		Playlist.add_song('2', True)
		Playlist.add_song('3', True)
		self.assertEqual(Playlist.objects.next_song().song_id, '2')

	def test_next_song_both_non_requested_and_one_requested(self):
		Playlist.add_song('1')
		Playlist.add_song('2')
		Playlist.add_song('3')
		Playlist.add_song('4', True)
		self.assertEqual(Playlist.objects.next_song().song_id, '1')

	def test_next_song_both_non_requested_and_requested(self):
		Playlist.add_song('1')
		Playlist.add_song('2')
		Playlist.add_song('3')
		Playlist.add_song('4', True)
		Playlist.add_song('5', True)
		Playlist.add_song('6', True)
		self.assertEqual(Playlist.objects.next_song().song_id, '5')

# class UtilPlaybackMethodTests(TestCase):
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
# 	def test_mpc_play_from_song_added_to_Songs(self):
# 		"""
# 		Clears the current playlist, adds test song /MPD_ROOT/Test Path/test.mp3
# 		to models.Songs, adds the song to mpc, then plays it
# 		"""
# 		Songs.add_song_exiftool("Test Path/test.mp3")
# 		test_song = Songs.objects.get(id=1)
# 		Playback.mpc_clear()
# 		Playback.mpc_add(test_song.filepath)
# 		Playback.mpc_play()
#		time.sleep(2)
#		currently_playing = mpc_currently_playing()
#		self.assertTrue(currently_playing, 'Test_Artist - Test_Title')

class UtilDatabaseMethodTests(TestCase):
	def test_update_songs_db(self):
		"""
		Tests the update_songs_model method, also checks if it ignores duplicate files
		"""
		self.assertQuerysetEqual(Songs.objects.all(), [])
		dupe_list = Database.update_songs_db()
		self.assertTrue(dupe_list == [])
		first_update_songs_count = Songs.objects.count()
		dupe_list = Database.update_songs_db()
		self.assertFalse(dupe_list == [])
		self.assertEqual(Songs.objects.count(), first_update_songs_count)


	def test_associate_type_to_song(self):
		Types.add_type('test_type')
		test_type = Types.objects.get(types='test_type')
		Songs.add_song_exiftool("Test Path/test.mp3")
		test_song = Songs.objects.get(title='Test_Title')
		Database.associate_type_to_song(test_song.id, test_type.types)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type').associated_songs.all()),
			['<Songs: Test_Title>']
		)
		self.assertQuerysetEqual(
			list(Songs.objects.get(title='Test_Title').types_set.all()),
			['<Types: test_type>']
		)

	def test_associate_type_to_song_multiple_types_multiple_songs(self):
		Types.add_type('test_type1')
		Types.add_type('test_type2')
		test_type1 = Types.objects.get(types='test_type1')
		test_type2 = Types.objects.get(types='test_type2')
		Songs.add_song_exiftool("Test Path/test.mp3")
		Songs.add_song_exiftool("Test Path/test2.mp3")
		test_song1 = Songs.objects.get(id=1)
		test_song2 = Songs.objects.get(id=2)
		Database.associate_type_to_song(test_song1.id, test_type1.types)
		Database.associate_type_to_song(test_song1.id, test_type2.types)
		Database.associate_type_to_song(test_song2.id, test_type1.types)
		Database.associate_type_to_song(test_song2.id, test_type2.types)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type1').associated_songs.all()),
			['<Songs: Test_Title>', '<Songs: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type2').associated_songs.all()),
			['<Songs: Test_Title>', '<Songs: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Songs.objects.get(id=1).types_set.all()),
			['<Types: test_type1>', '<Types: test_type2>',]
		)
		self.assertQuerysetEqual(
			list(Songs.objects.get(id=2).types_set.all()),
			['<Types: test_type1>', '<Types: test_type2>',]
		)

	def test_associate_type_to_song_missing_type(self):
		nonexistant_type = 'no_type'
		Songs.add_song_exiftool("Test Path/test.mp3")
		test_song = Songs.objects.get(title='Test_Title')
		with self.assertRaises(TypeNotFoundError):
			Database.associate_type_to_song(test_song.id, nonexistant_type)

	def test_associate_type_to_song_missing_song(self):
		Types.add_type('test_type')
		test_type = Types.objects.get(types='test_type')
		nonexistant_song_id = '33333'
		with self.assertRaises(SongNotFoundError):
			Database.associate_type_to_song(nonexistant_song_id, test_type.types)


	def test_dissociate_type_to_song(self):
		Types.add_type('test_type1')
		Types.add_type('test_type2')
		test_type1 = Types.objects.get(types='test_type1')
		test_type2 = Types.objects.get(types='test_type2')
		Songs.add_song_exiftool("Test Path/test.mp3")
		Songs.add_song_exiftool("Test Path/test2.mp3")
		test_song1 = Songs.objects.get(id=1)
		test_song2 = Songs.objects.get(id=2)
		Database.associate_type_to_song(test_song1.id, test_type1.types)
		Database.associate_type_to_song(test_song1.id, test_type2.types)
		Database.associate_type_to_song(test_song2.id, test_type1.types)
		Database.associate_type_to_song(test_song2.id, test_type2.types)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type1').associated_songs.all()),
			['<Songs: Test_Title>', '<Songs: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Songs.objects.get(id=1).types_set.all()),
			['<Types: test_type1>', '<Types: test_type2>',]
		)
		Database.dissociate_type_to_song(test_song1.id, test_type1.types)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type1').associated_songs.all()),
			['<Songs: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Songs.objects.get(id=1).types_set.all()),
			['<Types: test_type2>',]
		)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type2').associated_songs.all()),
			['<Songs: Test_Title>', '<Songs: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Songs.objects.get(id=2).types_set.all()),
			['<Types: test_type1>', '<Types: test_type2>',]
		)

	def test_dissociate_type_to_song_not_associated(self):
		Types.add_type('test_type')
		test_type = Types.objects.get(types='test_type')
		Songs.add_song_exiftool("Test Path/test.mp3")
		test_song = Songs.objects.get(title='Test_Title')
		Database.dissociate_type_to_song(test_song.id, test_type.types)
		self.assertQuerysetEqual(
			list(Types.objects.get(types='test_type').associated_songs.all()),[])
		self.assertQuerysetEqual(
			list(Songs.objects.get(title='Test_Title').types_set.all()), [])

# class UtilControlMethodTests(TestCase):
# 	def test_update_db(self):
# 		"""
# 		Tests the update_database method that finds all .mp3, .ogg, .flac
# 		files in the MPD root recursively and adds it to the Songs database
# 		"""
# 		Control.scan_for_songs()
# 		test_song = Songs.objects.get(filepath='Test Path/test.mp3')
# 		self.assertEqual(test_song.album, "Test_Album")
# 		self.assertTrue(Songs.objects.count() >= 3)
# 
# 	def test_update_db_dupe(self):
# 		"""
# 		Tests if the update_database method ignores duplicate files
# 		"""
# 		Control.scan_for_songs()
# 		first_update_songs_count = Songs.objects.count()
# 		dupe_list = Control.scan_for_songs()
# 		self.assertFalse(dupe_list == [])
# 		self.assertEqual(Songs.objects.count(), first_update_songs_count)
# 
# 	def test_update_db_mpc_add_mpc_play(self):
# 		"""
# 		Add songs to songs db with Control.scan_for_songs(), then add a song to 
# 		songs db with mpc_add
# 		"""
# 		Control.scan_for_songs()
# 		test_song = Songs.objects.get(filepath='Test Path/test.mp3')
# 		Playback.mpc_clear()
# 		Playback.mpc_add(test_song.filepath)
# 		Playback.mpc_play()
# 		time.sleep(2)
# 		currently_playing = Playback.mpc_currently_playing()
# 		self.assertTrue(currently_playing, 'Test_Artist - Test_Song')
# 
