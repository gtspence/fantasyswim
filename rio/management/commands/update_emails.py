from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice, News
from django.db.models import Count, Sum, Case, When, F
from django.db import models
from django.template import loader
from django.core.mail import send_mass_mail, EmailMultiAlternatives
from rio.views import get_all_teams, league_position, SUFFIXES, ordinal

class Command(BaseCommand):
	help = 'Sends email to all users with their summary performance'

	def add_arguments(self, parser):
		parser.add_argument('time')

	def handle(self, *arg, **options):
		
		messages = ()
		
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
			
			text = "%s: Your team %s has %s and %s." % (options['time'], team.name, points, golds)
			
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
		
			subject='Fantasy Swimming Rio: %s Update!' % options['time']
			body = loader.render_to_string('rio/update.html', {'text':text, 'user':team.user})
			from_email='fantasyswimming@gmail.com'
			to_email=team.user.email
			email_message = ((subject, body, from_email, [to_email]),)
			messages += email_message

		send_mass_mail(messages, fail_silently=False)
		
		self.stdout.write(self.style.SUCCESS('Successfully sent all users an email'))
