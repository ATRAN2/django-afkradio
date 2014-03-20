from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic

from afkradio.models import Song, Playlist, PlayHistory, Setlist
import logging

def search(request):
	if 'search-query' in request.GET and request.GET('search-query'):
		query = request.GET('search-query')
		songs = Song.objects.filter(title__icontains=query)
		return render(request, 'search_results.html', \
				{'songs':songs, 'query': query})
	else:
		message = 'You searched for: %r' % request.GET['search-query'] + \
			' Please submit a valid search term.'
	return HttpResponse(message)

class HomeView(generic.ListView):
	template_name = 'afkradio/home.html'
	context_object_name = 'songs_list'

	def get_queryset(self):
		return Song.objects.all()

class SongView(generic.ListView):
	template_name = 'afkradio/songs.html'
	model = Song
	context_object_name = 'songs_list'
	paginate_by = 10

	def get_queryset(self):
		return Song.objects.all()

class SingleSongView(generic.DetailView):
	template_name = 'afkradio/singlesong.html'
	model = Song
	context_object_name = 'song'
