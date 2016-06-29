from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice

class Command(BaseCommand):
	help = 'Imports event schedule and order from csv file'

	def handle(self, *arg, **options):
		import pandas as pd

		try:
			schedule = pd.read_csv('schedule.csv', error_bad_lines=False)
		except IOError:
			raise CommandError('File schedule.csv does not exist')

		from datetime import datetime

		#Manipulate Event column
		schedule = schedule[schedule['Event'].apply(lambda(x): 'Final' in x)]
		schedule['Event'] = schedule['Event'].apply(lambda(x): x.split(" ")[0:-2])
		for i in schedule.index:
			if schedule['Event'][i][0] == 'Men\xd5s':
				schedule['Event'][i][0] = "Men's"
			if schedule['Event'][i][0] == 'Women\xd5s':
				schedule['Event'][i][0] = "Women's"
			if 'x' in schedule['Event'][i]:
				schedule['Event'][i].insert(4, "Metres")
				schedule['Event'][i][3] = schedule['Event'][i][3][0:-1]
				schedule['Event'][i] = [schedule['Event'][i][0], "".join(schedule['Event'][i][1:4]), 
										schedule['Event'][i][4], schedule['Event'][i][5], 
										schedule['Event'][i][6]]
			else:
				schedule['Event'][i][1] = schedule['Event'][i][1][0:-1]  
		schedule['Event'] = schedule['Event'].apply(lambda(x): " ".join(x))
		# Formalise stroke names
		for i in schedule.index:
			if '4x200' in schedule['Event'][i]:
				continue
			schedule['Event'][i] = schedule['Event'][i].replace("s Free", "s Freestyle")
			schedule['Event'][i] = schedule['Event'][i].replace("0 Free", "0 Freestyle")
			schedule['Event'][i] = schedule['Event'][i].replace("Fly", "Butterfly")
			schedule['Event'][i] = schedule['Event'][i].replace("Back", "Backstroke")
			schedule['Event'][i] = schedule['Event'][i].replace("Breast", "Breaststroke")
			schedule['Event'][i] = schedule['Event'][i].replace("IM", "Individual Medley")
		# Convert Date column into datetime.date objects
		for i in schedule.index:
			schedule['Date'][i] = datetime.strptime(schedule['Date'][i], '%d/%m/%Y').date()
		# Add order column
		schedule['Order'] = range(1, len(schedule.index)+1)


		# Get event
		for row in schedule.index:
			event = Event.objects.get(name = schedule.ix[row]['Event'])
			print event
			event.date = schedule.ix[row]['Date']
			event.order = schedule.ix[row]['Order']
			event.save()
			print event
			
		self.stdout.write(self.style.SUCCESS('Successfully updated event schedule'))