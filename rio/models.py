from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
