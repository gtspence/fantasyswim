from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice

class Command(BaseCommand):
	help = 'Imports data from fina csv file'

	def handle(self, *arg, **options):
		import pandas as pd
		
		try:
			data1 = pd.read_csv('relays.csv', sep=",")
		except IOError:
			raise CommandError('File relays.csv does not exist')

		# Removes any non-Olympic relays
		data1['olympic'] = data1['full_desc'].apply(lambda(x): x[:1]!='2')
		data1 = data1[data1['olympic']]

		# Create better event column
		event = []
		for i in data1.index:
			if data1['gender'][i] == "M":
				gender = "Men's"
			if data1['gender'][i] == "F":
				gender = "Women's"
			better_event = data1['full_desc_intl'][i].split(" ")
			better_event = [gender] + better_event[:4]
			better_event = ' '.join(better_event)
			event.append(better_event)

		data1['event'] = pd.Series(event, index=data1.index)

		# Create column of time_hundredths
		from datetime import timedelta
		def swim_time_into_hundredths(x):
			minute_broken = str(x).split(":")
			if len(minute_broken) == 2:
				return int(minute_broken[0])*6000+int(float(minute_broken[1])*100)
			else:
				return int(float(minute_broken[0])*100)

		data1['time_hundredths'] = pd.Series(data1['swim_time_relay'].apply(swim_time_into_hundredths), index=data1.index)

		# Get or create event
		for row in data1.index:
			_, created = Event.objects.get_or_create(
				name = data1.ix[row]['event'],
				relay = True,
				)
			print(_, created)

		# Get or create swimmers
		for row in data1.index:
			_, created = Swimmer.objects.get_or_create(
				name = data1.ix[row]['team_short_name'],
				country = data1.ix[row]['team_code'],
				)
			print(_, created)

		# Add participants
		for row in data1.index:
			_, created = Participant.objects.update_or_create(
				event = Event.objects.get(name=data1.ix[row]['event']),
				swimmer = Swimmer.objects.get(name=data1.ix[row]['team_short_name'], country=data1.ix[row]['team_code']),
				defaults={'time': data1.ix[row]['time_hundredths']},
				)
			print(_, created)
		
		self.stdout.write(self.style.SUCCESS('Successfully closed uploaded data'))