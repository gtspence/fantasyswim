from django.contrib import admin

from .models import Team, Event, Swimmer, Participant, Choice


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
	list_display = ('user', 'name', 'points', 'correct_golds')
 
class ChoiceAdmin(admin.ModelAdmin):
	list_display = ('event', 'team', 'participant', 'points')
	list_filter = ['team']


admin.site.register(Event, EventAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Swimmer, SwimmerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Choice, ChoiceAdmin)