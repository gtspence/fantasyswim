from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News

from datetime import datetime

class Command(BaseCommand):
	help = 'Creates event result news items for all users with teams'

	def add_arguments(self, parser):
		parser.add_argument('event_name')

	def handle(self, *arg, **options):
	
		event = Event.objects.get(name=options['event_name'])

		if event.scored == False:
			self.stdout.write(self.style.ERROR('**"%s" HAS NOT BEEN SCORED**' % options['event_name']))
		elif News.objects.filter(event=event, type='result').exists():
			self.stdout.write(self.style.ERROR('**RESULT NEWS ITEMS ALREADY EXIST FOR "%s"**' % options['event_name']))
		elif len(event.gold()) == 0:
			self.stdout.write(self.style.ERROR('**"%s" HAS NO GOLD MEDALIST?!?**' % options['event_name']))
		else:
			for team in Team.objects.all().select_related('user').prefetch_related('choice_set__participant'):
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
				News.objects.create(
					text=text,
					date_time=datetime.now(),
					event=event,
					user=team.user,
					team=team,
					type='result',
					)
			self.stdout.write(self.style.SUCCESS('Successfully created result news items for "%s"' % options['event_name']))