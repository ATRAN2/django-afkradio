from django.template import Library, Node
from afkradio.models import Playlist

register = Library()

@register.filter(name='get_song_title')
def get_song_title(playlist_song):
	return playlist_song.song_title()

@register.filter(name='get_song_artist')
def get_song_artist(playlist_song):
	return playlist_song.song_artist()

class PlaylistContentNode(Node):
	def __init__(self, count, varname, call='all'):
		self.count = count
		self.varname = varname
		self.call = call

	def render(self, context):
		playlist_manager = getattr(Playlist, 'objects')
		model_method = getattr(playlist_manager, self.call)
		context[self.varname] = model_method()[:self.count]
		return ''

def get_playlist_requested(parser, token):
	bits = token.contents.split()
	count = Playlist.objects.requested_count()
	if len(bits) != 3:
		raise TemplateSyntaxError, "get_playlist_requested tag takes exactly 2 arguments"
	if bits[1] != 'as':
		raise TemplateSyntaxError, "Third argument to get_playlist_requested must be 'as'"
	return PlaylistContentNode(count, bits[2], 'requested_sorted')

def get_playlist_unrequested(parser, token):
	bits = token.contents.split()
	count = Playlist.objects.unrequested_count()
	if len(bits) != 3:
		raise TemplateSyntaxError, "get_playlist_requested tag takes exactly 2 arguments"
	if bits[1] != 'as':
		raise TemplateSyntaxError, "Third argument to get_playlist_requested must be 'as'"
	return PlaylistContentNode(count, bits[2], 'unrequested_sorted')

get_playlist_requested = register.tag(get_playlist_requested)
get_playlist_unrequested = register.tag(get_playlist_unrequested)
