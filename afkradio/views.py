from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.db.models import Q

from afkradio.models import Song, Playlist, PlayHistory, Setlist
from afkradio.utils import Control
import logging

def search(request):
	if 'query' in request.GET and request.GET['query']:
		query = request.GET['query']
		songs_list = Song.objects.filter(
				Q(title__icontains=query) | Q(artist__icontains=query) | \
				Q(extra__icontains=query) | Q(album__icontains=query) \
				).order_by('title','artist','extra','album')
		return render_to_response('afkradio/songs.html', \
				{'songs_list':songs_list, 'query':query})
	else:
		message = 'You searched for: %r' % request.GET['search-query'] + \
			' Please submit a valid search term.'
	return HttpResponse(message)

def artist(request):
	if 'artist-query' in request.GET and request.GET['artist-query']:
		query = request.GET['artist-query']
		songs_list = Song.objects.filter(artist=query).order_by( \
				'year','album','trackno','title')
		return render_to_response('afkradio/artist.html', \
				{'songs_list':songs_list, 'query': query})
	else:
		message = 'You searched for: %r' % request.GET['search-query'] + \
			' Please submit a valid search term.'
	return HttpResponse(message)

def song_request(request):
	if(request.POST.get('req_button')):
		Control.request_song( str(request.POST.get('req_song_id')) )

class HomeView(generic.ListView):
	template_name = 'afkradio/home.html'
	context_object_name = 'songs_list'

	def get_queryset(self):
		return Song.objects.all()

class SongView(generic.ListView):
	# Check song request
	template_name = 'afkradio/songs.html'
	model = Song
	context_object_name = 'songs_list'
	paginate_by = 20
	
	def post(self, request, *args, **kwargs):
		song_request(self.request)
		return HttpResponseRedirect(reverse('afkradio:songs'))

	def get_queryset(self):
		return Song.objects.all().order_by('-pk')

class SingleSongView(generic.DetailView):
	template_name = 'afkradio/singlesong.html'
	model = Song
	context_object_name = 'song'
