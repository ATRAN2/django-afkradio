from django.shortcuts import render, get_object_or_404
from django.views import generic

from afkradio.models import Songs, Playlist, PlayHistory, Types

import logging

class ListView(generic.ListView):
	template_name = 'afkradio/songs.html'
	context_object_name = 'songs_list'

	def get_queryset(self):
		return Songs.objects.all()
