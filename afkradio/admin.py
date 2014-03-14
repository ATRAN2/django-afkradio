from django.contrib import admin
from afkradio.models import Songs

admin.site.register(Songs)

class SongAdmin(admin.ModelAdmin):
	list_per_page = 20

	fieldsets = [
		(None, {'fields': ['title']}),
		('Date Information', {'fields': ['date_added'], 'classes':['collapse']}),
	]

