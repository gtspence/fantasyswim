from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News
from django.db.models import Q

from datetime import datetime

class Command(BaseCommand):
	help = 'Creates WR news items for all users with teams that have nominated that event'

	def add_arguments(self, parser):
		parser.add_argument('event_name')

	def handle(self, *arg, **options):
	
		event = Event.objects.get(name=options['event_name'])
		
		if event.wr == False:
			self.stdout.write(self.style.ERROR('**"%s" HAS NOT BEEN MARKED AS WR**' % options['event_name']))
		elif News.objects.filter(event=event, type='wr').exists():
			self.stdout.write(self.style.ERROR('**WR NEWS ITEMS ALREADY EXIST FOR "%s"**' % options['event_name']))
		else:
			for team in Team.objects.filter(Q(WR_event=event) | Q(WR_event2=event) | Q(WR_event3=event)).select_related('user'):
				text = "World record in %s, you scored 5 points!" % event.name
				News.objects.create(
					text=text,
					date_time=datetime.now(),
					event=event,
					user=team.user,
					team=team,
					type='wr',
					)
			self.stdout.write(self.style.SUCCESS('Successfully created WR news items for "%s" WR' % options['event_name']))