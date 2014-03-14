from django.contrib import admin
from afkradio.models import Song

admin.site.register(Song)

class SongAdmin(admin.ModelAdmin):
	list_per_page = 20

	fieldsets = [
		(None, {'fields': ['title']}),
		('Date Information', {'fields': ['date_added'], 'classes':['collapse']}),
	]

