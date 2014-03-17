from django.conf.urls import patterns, url

from afkradio import views

urlpatterns = patterns ('',
		# ex:/afkradio/
		url(r'^$', views.HomeView.as_view(), name='home'),
		url(r'^Song/', views.SongView.as_view(), name='songs'),
)
