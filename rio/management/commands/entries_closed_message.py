from django.core.management.base import BaseCommand, CommandError
from rio.models import User, Team, Swimmer, Participant, Event, Choice
from django.template import loader
from django.core.mail import send_mass_mail, EmailMultiAlternatives

class Command(BaseCommand):
	help = 'Sends email to all users saying entries have closed'

	def handle(self, *arg, **options):
		
		messages = ()

		for user in User.objects.all():
			subject='Fantasy Swimming: Entries Closed!'
			body = loader.render_to_string('rio/entries_closed.html')
			from_email='fantasyswimming@gmail.com'
			to_email=user.email
			email_message = ((subject, body, from_email, [to_email]),)
			messages += email_message

		send_mass_mail(messages, fail_silently=False)
		
		self.stdout.write(self.style.SUCCESS('Successfully sent all users an email'))
			

