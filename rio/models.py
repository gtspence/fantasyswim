from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible

class Event(models.Model):
	name = models.CharField(max_length=50)
	date = models.DateField("Date of Final", null=True, blank=True)
	order = models.IntegerField("Event Number", null=True, blank=True)
	relay = models.BooleanField(default=False)
	wr = models.BooleanField(default=False)
	scored = models.BooleanField(default=False)
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse('event', args=(self.id,))
	def gold(self):
		return self.participant_set.filter(points=5).select_related('swimmer')
	def silver(self):
		return self.participant_set.filter(points=2).select_related('swimmer')
	def bronze(self):
		return self.participant_set.filter(points=1).select_related('swimmer')
	class Meta:
		ordering = ['id']

@python_2_unicode_compatible
class League(models.Model):
	creator = models.OneToOneField(User)
	name = models.CharField("League Name", max_length=100, unique=True)
	description = models.CharField("League Description", max_length=200, null=True, blank=True)
	date_created = models.DateTimeField("Date Created", null=True, blank=True)
	class Meta:
		ordering = ['name']
	def get_absolute_url(self):
		return reverse('league', args=(self.id,))
	def size(self):
		return len(self.team_set.all())
	def __str__(self):
		return '%s (Created by: %s, Number of teams: %d)' % (self.name, self.creator.username, self.size())

@python_2_unicode_compatible
class Team(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField("Team Name", max_length=200)
	league = models.ForeignKey(League, on_delete=models.SET_NULL, blank=True, null=True)
	WR_event = models.ForeignKey(Event, limit_choices_to={'relay': False}, 
								blank=True, null=True, 
								related_name="WR_event", verbose_name=u'WR event 1')
	WR_event2 = models.ForeignKey(Event, limit_choices_to={'relay': False}, 
								blank=True, null=True, 
								related_name="WR_event2", verbose_name=u'WR event 2')
	WR_event3 = models.ForeignKey(Event, limit_choices_to={'relay': False}, 
								blank=True, null=True, 
								related_name="WR_event3", verbose_name=u'WR event 3')
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse('team', args=(self.id,))
	def points(self):
# 		self.participant_set.aggregate(Sum('points'))
		team_points = [Participant.objects.filter(choice__team=self).aggregate(Sum('points'))['points__sum']]
		for nomination in [self.WR_event, self.WR_event2, self.WR_event3]:
			if nomination:
				team_points.append(5*nomination.wr)
		return sum(p for p in team_points if p is not None)
	def correct_golds(self):
		return Participant.objects.filter(choice__team=self, points=5).count()
	def std_points(self):
		return self.points() * 100 + self.correct_golds()
	def complete(self):
		choices_or_wr_events_none = [Choice.objects.filter(team=self, participant=None).count() == 0,
									self.WR_event != None, self.WR_event2 != None, self.WR_event3 != None]
		return all(choices_or_wr_events_none)


class Swimmer(models.Model):
	name = models.CharField(max_length=200)
	country = models.CharField(max_length=200)
	def __str__(self):
		return self.name

def time_converter(t):
	minutes = t / 6000
	remain = t - minutes*6000
	seconds = remain / 100
	hundredths = remain - seconds*100
	if minutes == 0:
		return str(seconds).zfill(2) + "." + str(hundredths).zfill(2)
	else:
		return str(minutes) + ":" + str(seconds).zfill(2) + "." + str(hundredths).zfill(2)

class Participant(models.Model):
	event = models.ForeignKey(Event)
	swimmer = models.ForeignKey(Swimmer)
	time = models.IntegerField("Season Best", null=True, blank=True)
	STATUS_CHOICES = (('Confirmed', 'Confirmed'), ('Unconfirmed', 'Unconfirmed'), ('Not swimming', 'Not swimming'))
	status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Unconfirmed')
	points = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return '%s %s %s (%s)' % (self.swimmer.name, self.swimmer.country, time_converter(self.time), self.status)
	def display_time(self):
		return time_converter(self.time)
	def choice_count(self):
		return len(self.choice_set.all())
	class Meta:
		unique_together = ('event', 'swimmer')
		ordering = ['time']
	
class Choice(models.Model):
	team = models.ForeignKey(Team)
	event = models.ForeignKey(Event)
	participant = models.ForeignKey(Participant, blank=True, null=True)
	def points(self):
		if self.participant:
			return self.participant.points
		else:
			return None
	def __str__(self):
		return '%s: %s' % (self.team, self.event)
	class Meta:
		unique_together = ('team', 'event')

@python_2_unicode_compatible
class News(models.Model):
	text = models.CharField(max_length=300)
	date_time = models.DateTimeField("Date")
	def date(self):
		return self.date_time.date()
	all_users = models.BooleanField(default=False)
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, blank=True, null=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True)
	league = models.ForeignKey(League, on_delete=models.SET_NULL, blank=True, null=True)
	TYPE_CHOICES = (('result', 'result'), ('wr', 'wr'), ('summary', 'summary'), ('other', 'other'))
	type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='other')
	class Meta:
		ordering = ['-date_time']
	def __str__(self):
		return 'News item %d' % (self.id)
