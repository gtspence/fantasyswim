from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Team(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField("Team Name", max_length=200)
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse('team', args=(self.id,))
	def points(self):
		team_choices = self.choice_set.all()
		team_points = [ch.participant.points for ch in team_choices]
		return sum(filter(None, team_points))
	def correct_golds(self):
		team_choices = self.choice_set.all()
		team_points = [ch.participant.points for ch in team_choices]
		return sum([x==5 for x in team_points])


class Event(models.Model):
	name = models.CharField(max_length=50)
	date = models.DateField("Date of Final", null=True, blank=True)
	relay = models.BooleanField(default=False)
	def __str__(self):
		return self.name
	def get_absolute_url(self):
		return reverse('event', args=(self.id,))
	
class Swimmer(models.Model):
	name = models.CharField(max_length=200)
	country = models.CharField(max_length=200)
	def __str__(self):
		return self.name

class Participant(models.Model):
	event = models.ForeignKey(Event)
	swimmer = models.ForeignKey(Swimmer)
	time = models.CharField("Season Best", max_length=50)
	STATUS_CHOICES = (('Y', 'Yes'), ('N', 'No'),)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
	points = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return '%s %s %s (Confirmed: %s)' % (self.swimmer.name, self.swimmer.country, self.time, self.status)
	class Meta:
		unique_together = ('event', 'swimmer')
	
class Choice(models.Model):
	team = models.ForeignKey(Team)
	event = models.ForeignKey(Event)
	participant = models.ForeignKey(Participant)
	def points(self):
		return self.participant.points
	def __str__(self):
		return '%s: %s' % (self.event.name, self.participant.swimmer.name)
	class Meta:
		unique_together = ('team', 'event')