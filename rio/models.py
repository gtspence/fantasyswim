from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField("Team Name", max_length=200)
    def __str__(self):
		return self.name

class Event(models.Model):
	name = models.CharField(max_length=50)
	date = models.DateField("Date of Final", null=True, blank=True)
	def __str__(self):
		return self.name
	
class Swimmer(models.Model):
	name = models.CharField(max_length=200)
	country = models.CharField(max_length=200)
	def __str__(self):
		return self.name

class Participant(models.Model):
	event = models.ForeignKey(Event)
	swimmer = models.ForeignKey(Swimmer)
	time=models.CharField("Season Best", max_length=50)
	STATUS_CHOICES = (('Y', 'Yes'), ('N', 'No'),)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
	def __str__(self):
		return '%s %s %s (Confirmed: %s)' % (self.swimmer.name, self.swimmer.country, self.time, self.status)
	
class Choice(models.Model):
	team = models.ForeignKey(Team)
	event = models.ForeignKey(Event)
	participant = models.ForeignKey(Participant)
	def __str__(self):
		return '%s: %s' % (self.event.name, self.participant.swimmer.name)