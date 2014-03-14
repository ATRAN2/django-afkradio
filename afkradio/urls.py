from django.conf.urls import patterns, url

from afkradio import views

urlpatterns = patterns ('',
		# ex:/afkradio/
		url(r'^$', views.ListView.as_view(), name='index'),
)
