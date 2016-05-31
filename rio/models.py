from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	team_name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.user.username