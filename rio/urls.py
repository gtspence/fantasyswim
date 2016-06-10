from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', auth_views.login, {'extra_context': {'title': 'Login'}}, name='login'),
    url('^', include('django.contrib.auth.urls')),
     url(r'^team_create/$', views.team_create, name='team_create'),
]
