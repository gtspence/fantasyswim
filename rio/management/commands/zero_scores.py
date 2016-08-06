from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News

class Command(BaseCommand):
	help = 'Sets all non-scoring participants in an event to zero points'

	def add_arguments(self, parser):
		parser.add_argument('event_name')

	def handle(self, *arg, **options):
	
		event = Event.objects.get(name=options['event_name'])
		
		if event.scored == True:
			self.stdout.write(self.style.ERROR('**"%s" HAS ALREADY BEEN SCORED**' % options['event_name']))
		elif len(event.gold()) == 0:
			self.stdout.write(self.style.ERROR('**"%s" HAS NO GOLD MEDALIST?!?**' % options['event_name']))
		else:
			zero_participants = Participant.objects.filter(event=event, points=None)

			for part in zero_participants:
				part.points = 0
				part.save()
			event.scored = True
			event.save()
			self.stdout.write(self.style.SUCCESS('Successfully updated zero scores and event.scored for "%s"' % options['event_name']))