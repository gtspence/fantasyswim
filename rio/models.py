from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

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
		team_points = [team_choice.points() for team_choice in self.choice_set.all()]
		if self.WR_event:
			team_points.append(5*self.WR_event.wr)
		if self.WR_event2:
			team_points.append(5*self.WR_event2.wr)
		if self.WR_event3:
			team_points.append(5*self.WR_event3.wr)
		return sum(p for p in team_points if p is not None)
	def correct_golds(self):
		team_points_choices_only = [team_choice.points() for team_choice in self.choice_set.all()]
		return sum([x==5 for x in team_points_choices_only])
	def complete(self):
		team_choices = Choice.objects.filter(team=self)
		choices_or_wr_events_none = [choice.participant == None for choice in team_choices] + [
									self.WR_event == None, self.WR_event2 == None, self.WR_event3 == None]
		return not any(choices_or_wr_events_none)


	
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
		return str(seconds) + "." + str(hundredths)
	else:
		return str(minutes) + ":" + str(seconds).zfill(2) + "." + str(hundredths).zfill(2)

class Participant(models.Model):
	event = models.ForeignKey(Event)
	swimmer = models.ForeignKey(Swimmer)
	time = models.IntegerField("Season Best", null=True, blank=True)
	STATUS_CHOICES = (('Y', 'Yes'), ('N', 'No'),)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
	points = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return '%s %s %s (Confirmed: %s)' % (self.swimmer.name, self.swimmer.country, time_converter(self.time), self.status)
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