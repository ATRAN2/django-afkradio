from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
from django.db.models import Q

from afkradio.models import Song, Playlist, PlayHistory, Setlist
from afkradio.utils import Control
import logging

GLOBAL_PAGINATION = 20

def pagination(request, songs_list, entries_per_page):
	if songs_list.count() <= entries_per_page:
		return songs_list
	else:
		paginator = Paginator(songs_list, entries_per_page)
		page = request.GET.get('page')
		try:
			contents = paginator.page(page)
		except PageNotAnInteger:
			contents = paginator.page(1)
		except EmptyPage:
			contents = paginator.page(paginator.num_pages)
		return contents

def search(request):
	if 'query' in request.GET and request.GET['query']:
		query = request.GET['query']
		songs_list = Song.objects.filter(
				Q(title__icontains=query) | Q(artist__icontains=query) | \
				Q(extra__icontains=query) | Q(album__icontains=query) \
				).order_by('title','artist','extra','album')
		contents = pagination(request, songs_list, GLOBAL_PAGINATION)
		search = True;
		return render_to_response('afkradio/songs.html', \
				{'songs_list':contents, 'query':query, 'page_obj':contents, 'search':search})
	else:
		message = 'You searched for: %r' % request.GET['query'] + \
			' Please submit a valid search query.'
	return HttpResponse(message)

def artist(request):
	if 'name' in request.GET and request.GET['name']:
		artist_query = request.GET['name']
		songs_list = Song.objects.filter(artist=artist_query).order_by( \
				'year','album','trackno','title')
		contents = pagination(request, songs_list, GLOBAL_PAGINATION)
		return render_to_response('afkradio/artist.html', \
				{'songs_list':contents, 'query': artist_query, 'page_obj':contents})
	else:
		message = 'You searched for: %r' % request.GET['name'] + \
			' Please submit a valid search query.'
	return HttpResponse(message)

def album(request):
	if 'name' in request.GET and request.GET['name']:
		album_query = request.GET['name']
		songs_list = Song.objects.filter(album=album_query).order_by( \
				'trackno','title','artist')
		contents = pagination(request, songs_list, GLOBAL_PAGINATION)
		return render_to_response('afkradio/album.html', \
				{'songs_list':contents, 'query':album_query, 'page_obj':contents})
	else:
		message = 'You searched for: %r' % request.GET['name'] + \
			' Please submit a valid search query.'
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
	paginate_by = GLOBAL_PAGINATION
	
	def post(self, request, *args, **kwargs):
		song_request(self.request)
		return HttpResponseRedirect(reverse('afkradio:songs'))

	def get_queryset(self):
		return Song.objects.all().order_by('-pk')

class SingleSongView(generic.DetailView):
	template_name = 'afkradio/singlesong.html'
	model = Song
	context_object_name = 'song'
