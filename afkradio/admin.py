from django.contrib import admin
from django.core.urlresolvers import reverse
from afkradio.models import Song, Setlist, Playlist, PlayHistory


class SetlistAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_display = ('setlist', 'active',)
	exclude = ('associated_songs',)

class SetlistInline(admin.TabularInline):
	model = Setlist.associated_songs.through

class SongAdmin(admin.ModelAdmin):
	list_per_page = 20
	list_display = ('id', 'artist', 'title', 'album', 'playcount', 'favecount')
	search_fields = ['title']
	inlines = [SetlistInline]

class PlayHistoryAdmin(admin.ModelAdmin):
	def song_title_edit(self, object):
		url = reverse('admin:%s_%s_change' %(object._meta.app_label, 'song'), args=(object.song_id,))
		title = object.song_title()
		return u'<a href="%s">%s</a>' %(url, title)

	list_per_page = 30
	list_display = ('song_id', 'song_title_edit', 'played_time')
	song_title_edit.allow_tags=True

class PlaylistAdmin(admin.ModelAdmin):
	def song_title_edit(self, object):
		url = reverse('admin:%s_%s_change' %(object._meta.app_label, 'song'), args=(object.song_id,))
		title = object.song_title()
		return u'<a href="%s">%s</a>' %(url, title)

	list_per_page = 30
	list_display = ('song_id', 'song_title_edit', 'user_requested', 'add_time')
	ordering = ['-user_requested', 'add_time']
	song_title_edit.allow_tags = True

admin.site.register(Song, SongAdmin)
admin.site.register(Setlist, SetlistAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(PlayHistory, PlayHistoryAdmin)
