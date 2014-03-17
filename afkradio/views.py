from django.shortcuts import render, get_object_or_404
from django.views import generic

from afkradio.models import Song, Playlist, PlayHistory, Setlist
import logging

class HomeView(generic.ListView):
	template_name = 'afkradio/home.html'
	context_object_name = 'songs_list'

	def get_queryset(self):
		return Song.objects.all()

class SongView(generic.ListView):
	template_name = 'afkradio/songs.html'
	context_object_name = 'songs_list'

	def get_queryset(self):
		return Song.objects.all()
