from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)

class Event(models.Model):
	event = models.CharField(max_length=50)
	
class Swimmer(models.Model):
	name = models.CharField(max_length=200)
	country = models.CharField(max_length=200)

class Participant(models.Model):
	event = models.ForeignKey(Event)
	swimmer = models.ForeignKey(Swimmer)
	time=models.CharField("Season Best", max_length=50)
	STATUS_CHOICES = (('Y', 'Yes'), ('N', 'No'),)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
	
class Nomination(models.Model):
	team = models.ForeignKey(Team)
	event = models.ForeignKey(Event)
	participant = models.ForeignKey(Participant)
