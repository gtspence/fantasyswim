from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^events/$', views.EventsView.as_view(), name='events'),
    url(r'^leagues/$', views.LeaguesView.as_view(), name='leagues'),
    url(r'^overall/$', views.OverallView.as_view(), name='overall'),
    url(r'^schedule/$', views.ScheduleView.as_view(), name='schedule'),
    url(r'^team(?P<pk>[0-9]+)/$', views.TeamView.as_view(), name='team'),
    url(r'^league(?P<pk>[0-9]+)/$', views.LeagueView.as_view(), name='league'),
    url(r'^user(?P<pk>[0-9]+)/$', views.user, name='user'),
    url(r'^event(?P<pk>[0-9]+)/$', views.EventView.as_view(), name='event'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', auth_views.login, {'extra_context': {'title': 'Login'}}, name='login'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^team_new/$', views.team_edit, name='team_new'),
    url(r'^league_create/$', views.league_create, name='league_create'),
	url(r'^team_edit/(?P<id>\d+)/$', views.team_edit, name='team_edit'),
]
