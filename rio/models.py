from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Team(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    def __str__(self):
		return self.name

class Event(models.Model):
	event = models.CharField(max_length=50)
	date = models.DateField("Date of Final", null=True, blank=True)
	def __str__(self):
		return self.event
# 	def event_complete(self):
# 		today = datetime.today()
# 		return self.date < today	#NB ISSUE WITH TIMEZONES ETC!!! 
# 	was_published_recently.admin_order_field = 'date'
# 	was_published_recently.boolean = True
# 	was_published_recently.short_description = 'Has final of event been swum?'
	
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
	
class Choice(models.Model):
	team = models.ForeignKey(Team)
	event = models.ForeignKey(Event)
	participant = models.ForeignKey(Participant)
