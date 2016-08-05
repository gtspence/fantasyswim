from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News
from django.db.models import Count, Sum, Case, When, F
from django.db import models

def get_all_teams():
	return Team.objects.annotate(
		total_points=Sum('choice__participant__points') +
			Case(
				When(WR_event__wr=True, then=5),
				default=0,
				output_field=models.IntegerField()
				) + 
			Case(
				When(WR_event2__wr=True, then=5),
				default=0,
				output_field=models.IntegerField()
				) +
			Case(
				When(WR_event3__wr=True, then=5),
				default=0,
				output_field=models.IntegerField()
				),
		correct_golds=Sum(
			Case(
				When(choice__participant__points=5, then=1),
				default=0,
				output_field=models.IntegerField()
				)
			),
		).annotate(std_points=F('total_points')*100+F('correct_golds')).order_by('-std_points', 'name')


def league_position(team, teams):
	position = sum([t.std_points > team.std_points for t in teams]) + 1
	joint = sum([t.std_points == team.std_points for t in teams]) > 1
	return {'position': position, 'joint': joint}

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
	# I'm checking for 10-20 because those are the digits that
	# don't follow the normal counting scheme. 
	if 10 <= num % 100 <= 20:
		suffix = 'th'
	else:
		# the second parameter is a default.
		suffix = SUFFIXES.get(num % 10, 'th')
	return "{:,}".format(num) + suffix

from datetime import datetime
# 
class Command(BaseCommand):
	help = 'Sets all non-scoring participants in an event to zero points'

	def add_arguments(self, parser):
		parser.add_argument('time')

	def handle(self, *arg, **options):
		
		teams = get_all_teams().exclude(std_points=None).select_related('user')
		
		for team in teams:
			
			if team.total_points == 1:
				points = "1 point"
			elif team.total_points in [0, None]:
				points = "0 points"
			else:
				points = "%d points" % team.total_points
			
			if team.correct_golds == 1:
				golds = "1 correct gold"
			elif team.correct_golds in [0, None]:
				golds = "0 correct golds"
			else:
				golds = "%d correct golds" % team.correct_golds
			
			text = "%s: your team has %s and %s." % (options['time'], points, golds)
			
			overall_position = league_position(team, teams)
			text += " You are now "
			if overall_position['joint']:
				text += "joint "
			text += ordinal(overall_position['position']) + "/%d overall" % (len(teams))
			
			if team.league:
				league_teams = teams.filter(league=team.league)
				minileague_position = league_position(team, league_teams)
				text += " and "
				if minileague_position['joint']:
					text += "joint "
				text += ordinal(minileague_position['position']) + "/%d in your league" % (len(league_teams))
			text += "!"
			News.objects.create(
				text=text,
				date_time=datetime.now(),
				user=team.user,
				team=team,
				type='summary',
				)
		self.stdout.write(self.style.SUCCESS('Successfully created summary items for "%s"' % options['time']))