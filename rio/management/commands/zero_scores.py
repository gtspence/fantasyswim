from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News

def league_position(team, league=False):
	team_std_pts = team.std_points()
	if league:
		league_teams = Team.objects.filter(league=team.league)
	else:
		league_teams = Team.objects.all()
	position = sum([team.std_points() > team_std_pts for team in league_teams]) + 1
	joint = sum([team.std_points() == team_std_pts for team in league_teams]) > 1
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

class Command(BaseCommand):
	help = 'Sets all non-scoring participants in an event to zero points'

	def add_arguments(self, parser):
		parser.add_argument('event_name')

	def handle(self, *arg, **options):
	
		event = Event.objects.get(name=options['event_name'])

		zero_participants = Participant.objects.filter(event=event, points=None)

		for part in zero_participants:
			part.points = 0
			part.save()
		event.scored = True
		event.save()
		self.stdout.write(self.style.SUCCESS('Successfully updated zero scores and event.scored for "%s"' % options['event_name']))