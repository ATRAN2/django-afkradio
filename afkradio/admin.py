from django.contrib import admin
from django.core.urlresolvers import reverse
from afkradio.models import Song, Type, Playlist, PlayHistory


class TypeAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_display = ('type', 'active',)
	exclude = ('associated_songs',)

class TypeInline(admin.TabularInline):
	model = Type.associated_songs.through

class SongAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_display = ('id', 'artist', 'title', 'album',)
	search_fields = ['title']
	inlines = [TypeInline]

class PlaylistAdmin(admin.ModelAdmin):
	def url_to_edit_song(self, object):
		url = reverse('admin:afkradio_Playlist_change', args=[object.id])
		return u'<a href="%s">Edit %s</a>' %(url, object.__unicode())

	list_per_page = 30
	list_display = ('song_id', 'song_title', 'url_to_edit_song', 'user_requested', 'add_time')
	ordering = ['-user_requested', 'add_time']
	

admin.site.register(Song, SongAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Playlist, PlaylistAdmin)
