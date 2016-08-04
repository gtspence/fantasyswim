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

		if News.objects.filter(event=event).exists():
			self.stdout.write(self.style.ERROR('**NEWS ITEMS ALREADY EXIST FOR "%s"**' % options['event_name']))
		if len(event.gold()) == 0:
			self.stdout.write(self.style.ERROR('**"%s" HAS NO GOLD MEDALIST?!?**' % options['event_name']))
		else:
			for team in Team.objects.all():
				golds = [s.swimmer.name for s in event.gold()]
				text = str(", ".join(golds)) + " won gold, you scored "
				if team.choice_set.get(event=event).participant == None:
					text += "0"
				else:
					text += str(team.choice_set.get(event=event).points()) 
				if team.choice_set.get(event=event).points() == 1:
					text += " point."
				else:
					text += " points."
# 				text += " You are now "
# 				if league_position(team)['joint']:
# 					text += "joint "
# 				text += ordinal(league_position(team)['position']) + " overall"
# 				if team.league:
# 					text += " and " + ordinal(league_position(team, team.league)['position']) + " in your league"
# 				text += "."
				News.objects.create(
					text=text,
					date_time=datetime.now(),
					event=event,
					user=team.user,
					team=team,
					)
			self.stdout.write(self.style.SUCCESS('Successfully created news items for "%s"' % options['event_name']))