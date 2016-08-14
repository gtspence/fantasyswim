from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News
from django.db.models import Count, Sum, Case, When, F
from django.db import models
from rio.views import get_all_teams, league_position, SUFFIXES, ordinal


from datetime import datetime
# 
class Command(BaseCommand):
	help = 'Creates final score news items for all users with teams'

	def handle(self, *arg, **options):
		
		teams = get_all_teams().select_related('user')
		
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
			
			text = "Final Scores: Your team scored %s and %s." % (points, golds)
			
			overall_position = league_position(team, teams)
			text += " You finished "
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
		self.stdout.write(self.style.SUCCESS('Successfully created final news items'))