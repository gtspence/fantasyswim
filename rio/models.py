from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum


class Event(models.Model):
	name = models.CharField(max_length=50)
	date = models.DateField("Date of Final", null=True, blank=True)
	relay = models.BooleanField(default=False)
	wr = models.BooleanField(default=False)
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse('event', args=(self.id,))
	class Meta:
		ordering = ['id']

class Team(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField("Team Name", max_length=200)
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
		team_points = [Participant.objects.filter(choice__team=self).aggregate(Sum('points'))['points__sum']]
		for nomination in [self.WR_event, self.WR_event2, self.WR_event3]:
			if nomination:
				team_points.append(5*nomination.wr)
		return sum(p for p in team_points if p is not None)
	def correct_golds(self):
		return Participant.objects.filter(choice__team=self, points=5).count()
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