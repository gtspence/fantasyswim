from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
	url(r'^login/$', auth_views.login, {'template_name': 'rio/login.html', 
										'extra_context': {'title': 'Login'},
										}),
	url(r'^logout/$', auth_views.logout, {'next_page': '/rio/'}),
	url(r'^password_reset/$', auth_views.password_reset, 
		{'template_name':'rio/password_reset_form.html',
       	 'email_template_name':'rio/password_reset_email.html',
       	 'subject_template_name':'rio/password_reset_subject.txt',
        'post_reset_redirect':'/rio/password_reset_done/',
        }),
    url(r'^password_reset_done/$', auth_views.password_reset_done,
    	{'template_name':'rio/password_reset_done.html',
        }),
    url(r'^reset/done/$', auth_views.password_reset_complete,
    	{'template_name':'rio/password_reset_complete.html',
        }, name="password_reset_complete"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
		auth_views.password_reset_confirm,
		{'template_name':'rio/password_reset_confirm.html'},
		name="password_reset_confirm"),
	url(r'^password_change/$', auth_views.password_change,
    	{'template_name':'rio/password_change_form.html',
        }, name="password_change"),
	url(r'^password_change/done/$', auth_views.password_change,
    	{'template_name':'rio/password_change_done.html',
        }, name="password_change_done"),
    url(r'^team_create/$', views.team_create, name='team_create'),
]


