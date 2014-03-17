from django.template import Library, Node
from afkradio.models import Playlist, PlayHistory
import datetime

register = Library()

@register.filter(name='get_song_title')
def get_song_title(playlist_song, length):
	title = playlist_song.song_title()
	if len(title) > length:
		title = title[:length-3] + u'...'
	return title

@register.filter(name='get_song_artist')
def get_song_artist(playlist_song, length):
	artist = playlist_song.song_artist()
	if len(artist) > length:
		artist = artist[:length-3] + u'...'
	return artist

class PlaylistContentNode(Node):
	def __init__(self, count, varname):
		self.count = count
		self.varname = varname
	
	def create_timetable(self, sorted_playlist):
		latest_song_time = PlayHistory.objects.latest('played_time').played_time
		timetable = []
		timedelta_table=[]
		count = 0
		for playlist_song in sorted_playlist:
			duration = playlist_song.song_duration()
			hrs = int(duration[0])
			mins = int(duration[2:4])
			secs = int(duration[5:7])
			if count == 0:
				time = latest_song_time + \
						datetime.timedelta(hours=hrs,minutes=mins,seconds=secs)
			else:
				time = timedelta_table[count-1] + \
						datetime.timedelta(hours=hrs,minutes=mins,seconds=secs)
			timedelta_table.append(time)
			timetable.append(time.strftime("%H:%M"))
			count += 1
		return timetable

	def check_requested(self, sorted_playlist):
		request_check = []
		for playlist_song in sorted_playlist:
			if playlist_song.user_requested:
				request_check.append(True)
			else:
				request_check.append(False)
		return request_check

	def render(self, context):
		playlist_sorted = Playlist.objects.queue_sorted()[:self.count]
		request_check = self.check_requested(playlist_sorted)
		timetable = self.create_timetable(playlist_sorted)
		context[self.varname] = zip(request_check, timetable, playlist_sorted)
		return ''

def get_playlist(parser, token):
	bits = token.contents.split()
	count = Playlist.objects.count()
	if len(bits) != 3:
		raise TemplateSyntaxError, "get_playlist tag takes exactly 2 arguments"
	if bits[1] != 'as':
		raise TemplateSyntaxError, "First argument to get_playlist_requested must be 'as'"
	return PlaylistContentNode(count, bits[2])

get_playlist = register.tag(get_playlist)
