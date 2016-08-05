from django.contrib import admin

from .models import Team, Event, Swimmer, Participant, Choice, League, News

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class ChoiceInline(admin.TabularInline):
	model = Choice
	extra = 1

class ParticipantInline(admin.TabularInline):
	model = Participant
	extra = 1

class EventAdmin(admin.ModelAdmin):
	list_display = ('name', 'date', 'order')

class ParticipantAdmin(admin.ModelAdmin):
	list_display = ('event', 'swimmer', 'time', 'status', 'points')
	list_filter = ['event']

class SwimmerAdmin(admin.ModelAdmin):
	list_display = ('name', 'country')
	list_filter = ['country']
	inlines = [ParticipantInline]

class TeamAdmin(admin.ModelAdmin):
	list_display = ('user', 'name', 'league', 'points', 'correct_golds')
 
class ChoiceAdmin(admin.ModelAdmin):
	list_display = ('event', 'team', 'participant', 'points')
	list_filter = ['team']

class NewsAdmin(admin.ModelAdmin):
	list_display = ('date_time', 'text', 'event', 'user', 'team', 'league', 'all_users', 'type')
	list_filter = ['user', 'event', 'type']

class LeagueAdmin(admin.ModelAdmin):
	list_display = ('name', 'creator', 'date_created')

UserAdmin.list_display = ('username', 'email', 'date_joined', 'last_login', 'is_staff', 'is_superuser')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Swimmer, SwimmerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(News, NewsAdmin)