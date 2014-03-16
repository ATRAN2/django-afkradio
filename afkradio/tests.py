from django.test import TestCase
from afkradio.models import Song, Setlist
from django.utils import timezone
from afkradio.utils import Playback, Database, Playlist, PlayHistory
from afkradio.errors import *
import datetime
import time

# If you want to run these tests, then please place the folder 'Test Path' located
# in the app root into your MPD music root folder.

class ModelSongMethodTests(TestCase):
	def test_add_song_exiftool_test_song(self):
		"""
		Tests if we can add a new song to the database as well as
		getting the corresponding metadata using exiftool
		"""
		Song.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		new_song = Song.objects.get(year='1111')
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
			Song.add_song_exiftool("this folder path/doesn't exist.mp3")
		self.assertQuerysetEqual(Song.objects.all(), [])
	
	def test_add_song_exiftool_nonsupported_format(self):
		"""
		Tests handling of add_song_exiftool() if the song in the path
		is not a supported file type
		"""
		with self.assertRaises(FileTypeError):
			Song.add_song_exiftool("Test Path/exiftool")
		self.assertQuerysetEqual(Song.objects.all(), [])

	def test_add_song_exiftool_same_song(self):
		"""
		Tests handling of add_song_exiftool() if the same song is added twice
		"""
		Song.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		with self.assertRaises(DuplicateEntryError):
			Song.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		self.assertQuerysetEqual(Song.objects.all(), ['<Song: Test_Title>'])

	def test_check_if_exists(self):
		Song.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		self.assertTrue(Song.objects.check_if_exists("Test_Title", 'title'))
		self.assertTrue(Song.objects.check_if_exists("Test_Artist", 'artist'))
		with self.assertRaises(SongNotFoundError):
			Song.objects.check_if_exists("Test_Album", 'extra')
		with self.assertRaises(SongNotFoundError):
			Song.objects.check_if_exists("2222", 'year')
		with self.assertRaises(FieldNotFoundError):
			Song.objects.check_if_exists("95328", 'NotAValidField')

	def test_check_if_id_exists(self):
		Song.add_song_exiftool("Test Path/test.mp3", "Test_Extra")
		self.assertTrue(Song.objects.check_if_id_exists("1"))
		with self.assertRaises(SongNotFoundError):
			Song.objects.check_if_id_exists("2")

	def test_get_random(self):
		with self.assertRaises(SongNotFoundError):
			Song.objects.get_random()
		Database.update_song_db()
		random_song = Song.objects.get_random()
		self.assertTrue(Song.objects.check_if_id_exists(random_song.id))

	def test_get_random_from_active_setlists(self):
		with self.assertRaises(SongNotFoundError):
			Song.objects.get_random_from_active_setlists()
		Database.update_song_db()
		Setlist.add_setlist('Test_Setlist1')
		Setlist.add_setlist('Test_Setlist2')
		Setlist.add_setlist('Test_Setlist3')
		Setlist.objects.activate_setlist('Test_Setlist1')
		Setlist.objects.activate_setlist('Test_Setlist3')
		with self.assertRaises(SongNotFoundError):
			Song.objects.get_random_from_active_setlists()
		Database.associate_setlist_to_song('1', 'Test_Setlist1')
		Database.associate_setlist_to_song('2', 'Test_Setlist1')
		Database.associate_setlist_to_song('3', 'Test_Setlist2')
		Database.associate_setlist_to_song('4', 'Test_Setlist3')
		Database.associate_setlist_to_song('5', 'Test_Setlist3')
		self.assertTrue(len(Setlist.objects.song_ids_of_active_setlists()) == 4)
		self.assertEqual(Song.objects.get_random_from_active_setlists().title, 'Test_Title')

class ModelSetlistMethodTests(TestCase):
	def test_add_setlist(self):
		"""
		Test if a new setlist can be added with add_setlists() function
		"""
		Setlist.add_setlist('add_test')
		self.assertQuerysetEqual(Setlist.objects.all(),['<Setlist: add_test>'])

	def test_add_setlist_with_same_entry(self):
		"""
		Test if a new setlist can be added with add_setlists() function
		"""
		Setlist.add_setlist('add_test')
		Setlist.add_setlist('add_test')
		self.assertQuerysetEqual(list(Setlist.objects.all()),['<Setlist: add_test>'])

	def test_add_setlist_multiple_entries(self):
		"""
		Test if a new setlist can be added with add_setlists() function
		"""
		Setlist.add_setlist('add_test1')
		Setlist.add_setlist('add_test2')
		self.assertQuerysetEqual(list(Setlist.objects.all()),
			['<Setlist: add_test1>', '<Setlist: add_test2>',])

	def test_remove_setlist_single_entry(self):
		"""
		Test if a setlist can be removed with remove_setlists() function
		"""
		Setlist.add_setlist('remove_test')
		self.assertQuerysetEqual(Setlist.objects.all(),['<Setlist: remove_test>'])
		Setlist.remove_setlist('remove_test')
		self.assertQuerysetEqual(Setlist.objects.all(),[])

	def test_remove_setlist_nonexistant_entry(self):
		"""
		Test if a setlist that doesn't can attempt to be removed with 
		remove_setlists() function
		"""
		self.assertQuerysetEqual(Setlist.objects.all(),[])
		Setlist.remove_setlist('remove_test')
		self.assertQuerysetEqual(Setlist.objects.all(),[])


	def test_remove_setlist_multiple_entry(self):
		"""
		Test if multiple setlists can be removed with remove_setlists() function
		"""
		Setlist.add_setlist('remove_test1')
		Setlist.add_setlist('remove_test2')
		self.assertQuerysetEqual(list(Setlist.objects.all()),
			['<Setlist: remove_test1>', '<Setlist: remove_test2>',])
		Setlist.remove_setlist('remove_test1')
		self.assertQuerysetEqual(list(Setlist.objects.all()),
			['<Setlist: remove_test2>'])
		Setlist.remove_setlist('remove_test2')
		self.assertQuerysetEqual(Setlist.objects.all(),[])

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
	def test_update_song_db(self):
		"""
		Tests the update_songs_model method, also checks if it ignores duplicate files
		"""
		self.assertQuerysetEqual(Song.objects.all(), [])
		dupe_list = Database.update_song_db()
		self.assertTrue(dupe_list == [])
		first_update_songs_count = Song.objects.count()
		dupe_list = Database.update_song_db()
		self.assertFalse(dupe_list == [])
		self.assertEqual(Song.objects.count(), first_update_songs_count)


	def test_associate_setlist_to_song(self):
		Setlist.add_setlist('test_setlist')
		test_setlist = Setlist.objects.get(setlist='test_setlist')
		Song.add_song_exiftool("Test Path/test.mp3")
		test_song = Song.objects.get(title='Test_Title')
		Database.associate_setlist_to_song(test_song.id, test_setlist.setlist)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist').associated_songs.all()),
			['<Song: Test_Title>']
		)
		self.assertQuerysetEqual(
			list(Song.objects.get(title='Test_Title').setlist_set.all()),
			['<Setlist: test_setlist>']
		)

	def test_associate_setlist_to_song_multiple_setlists_multiple_songs(self):
		Setlist.add_setlist('test_setlist1')
		Setlist.add_setlist('test_setlist2')
		test_setlist1 = Setlist.objects.get(setlist='test_setlist1')
		test_setlist2 = Setlist.objects.get(setlist='test_setlist2')
		Song.add_song_exiftool("Test Path/test.mp3")
		Song.add_song_exiftool("Test Path/test2.mp3")
		test_song1 = Song.objects.get(id=1)
		test_song2 = Song.objects.get(id=2)
		Database.associate_setlist_to_song(test_song1.id, test_setlist1.setlist)
		Database.associate_setlist_to_song(test_song1.id, test_setlist2.setlist)
		Database.associate_setlist_to_song(test_song2.id, test_setlist1.setlist)
		Database.associate_setlist_to_song(test_song2.id, test_setlist2.setlist)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist1').associated_songs.all()),
			['<Song: Test_Title>', '<Song: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist2').associated_songs.all()),
			['<Song: Test_Title>', '<Song: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Song.objects.get(id=1).setlist_set.all()),
			['<Setlist: test_setlist1>', '<Setlist: test_setlist2>',]
		)
		self.assertQuerysetEqual(
			list(Song.objects.get(id=2).setlist_set.all()),
			['<Setlist: test_setlist1>', '<Setlist: test_setlist2>',]
		)

	def test_associate_setlist_to_song_missing_setlist(self):
		nonexistant_setlist = 'no_setlist'
		Song.add_song_exiftool("Test Path/test.mp3")
		test_song = Song.objects.get(title='Test_Title')
		with self.assertRaises(SetlistNotFoundError):
			Database.associate_setlist_to_song(test_song.id, nonexistant_setlist)

	def test_associate_setlist_to_song_missing_song(self):
		Setlist.add_setlist('test_setlist')
		test_setlist = Setlist.objects.get(setlist='test_setlist')
		nonexistant_song_id = '33333'
		with self.assertRaises(SongNotFoundError):
			Database.associate_setlist_to_song(nonexistant_song_id, test_setlist.setlist)


	def test_dissociate_setlist_to_song(self):
		Setlist.add_setlist('test_setlist1')
		Setlist.add_setlist('test_setlist2')
		test_setlist1 = Setlist.objects.get(setlist='test_setlist1')
		test_setlist2 = Setlist.objects.get(setlist='test_setlist2')
		Song.add_song_exiftool("Test Path/test.mp3")
		Song.add_song_exiftool("Test Path/test2.mp3")
		test_song1 = Song.objects.get(id=1)
		test_song2 = Song.objects.get(id=2)
		Database.associate_setlist_to_song(test_song1.id, test_setlist1.setlist)
		Database.associate_setlist_to_song(test_song1.id, test_setlist2.setlist)
		Database.associate_setlist_to_song(test_song2.id, test_setlist1.setlist)
		Database.associate_setlist_to_song(test_song2.id, test_setlist2.setlist)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist1').associated_songs.all()),
			['<Song: Test_Title>', '<Song: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Song.objects.get(id=1).setlist_set.all()),
			['<Setlist: test_setlist1>', '<Setlist: test_setlist2>',]
		)
		Database.dissociate_setlist_to_song(test_song1.id, test_setlist1.setlist)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist1').associated_songs.all()),
			['<Song: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Song.objects.get(id=1).setlist_set.all()),
			['<Setlist: test_setlist2>',]
		)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist2').associated_songs.all()),
			['<Song: Test_Title>', '<Song: Test_Title>',]
		)
		self.assertQuerysetEqual(
			list(Song.objects.get(id=2).setlist_set.all()),
			['<Setlist: test_setlist1>', '<Setlist: test_setlist2>',]
		)

	def test_dissociate_setlist_to_song_not_associated(self):
		Setlist.add_setlist('test_setlist')
		test_setlist = Setlist.objects.get(setlist='test_setlist')
		Song.add_song_exiftool("Test Path/test.mp3")
		test_song = Song.objects.get(title='Test_Title')
		Database.dissociate_setlist_to_song(test_song.id, test_setlist.setlist)
		self.assertQuerysetEqual(
			list(Setlist.objects.get(setlist='test_setlist').associated_songs.all()),[])
		self.assertQuerysetEqual(
			list(Song.objects.get(title='Test_Title').setlist_set.all()), [])

# class UtilControlMethodTests(TestCase):
# 	def test_update_db(self):
# 		"""
# 		Tests the update_database method that finds all .mp3, .ogg, .flac
# 		files in the MPD root recursively and adds it to the Song database
# 		"""
# 		Control.scan_for_songs()
# 		test_song = Song.objects.get(filepath='Test Path/test.mp3')
# 		self.assertEqual(test_song.album, "Test_Album")
# 		self.assertTrue(Song.objects.count() >= 3)
# 
# 	def test_update_db_dupe(self):
# 		"""
# 		Tests if the update_database method ignores duplicate files
# 		"""
# 		Control.scan_for_songs()
# 		first_update_songs_count = Song.objects.count()
# 		dupe_list = Control.scan_for_songs()
# 		self.assertFalse(dupe_list == [])
# 		self.assertEqual(Song.objects.count(), first_update_songs_count)
# 
# 	def test_update_db_mpc_add_mpc_play(self):
# 		"""
# 		Add songs to songs db with Control.scan_for_songs(), then add a song to 
# 		songs db with mpc_add
# 		"""
# 		Control.scan_for_songs()
# 		test_song = Song.objects.get(filepath='Test Path/test.mp3')
# 		Playback.mpc_clear()
# 		Playback.mpc_add(test_song.filepath)
# 		Playback.mpc_play()
# 		time.sleep(2)
# 		currently_playing = Playback.mpc_currently_playing()
# 		self.assertTrue(currently_playing, 'Test_Artist - Test_Song')
# 
