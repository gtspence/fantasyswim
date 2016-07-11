from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamEditForm, TeamEditFormWR, ChoiceEditForm, ContactForm, LeagueCreateForm
from django.contrib.auth.decorators import login_required
from .models import User, Team, Event, Swimmer, Participant, Choice, League
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import send_mass_mail, EmailMultiAlternatives
from django.contrib import messages
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from operator import attrgetter
from django.db.models import Count
from datetime import datetime

events_scored = float(sum([event.scored() for event in Event.objects.all()]))
progress = int(round(events_scored / Event.objects.all().count() * 100))


@login_required
def rules(request):
	return render(request, 'rio/rules.html', context={'title':'Rules', 'update_date': settings.UPDATE_DATE})

@login_required
def contact(request):
	form_class = ContactForm
	context = RequestContext(request)
	
	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			form_message = request.POST.get('message', '')
			message1 = ('Fantasy Swimming - Message from: ' + str(request.user), 
						form_message, request.user.email, ['fantasyswimming@gmail.com'])
			message2 = ('Fantasy Swimming - Your Sent Message', 
						form_message, 'fantasyswimming@gmail.com', [request.user.email])
			send_mass_mail((message1, message2))
			messages.info(request, 'Message sent to Fantasy Swimming Admin.')
			return HttpResponseRedirect('/rio/')
	
	return render(request, 'rio/contact.html', {'form': form_class, 'title':'Contact Us'}, context)

@method_decorator(login_required, name='dispatch')
class EventsView(generic.ListView):
	template_name = 'rio/events.html'
	context_object_name = 'w_event_list'
	def get_queryset(self):
		"""Return all the Women's events."""
		return Event.objects.filter(name__startswith='W').order_by('id')
	def get_context_data(self, *args, **kwargs):
		context = super(EventsView, self).get_context_data(*args, **kwargs)
		context['m_event_list'] = Event.objects.filter(name__startswith='M').order_by('id')
		context['title'] = 'Events'
		return context

@method_decorator(login_required, name='dispatch')
class ScheduleView(generic.ListView):
	template_name = 'rio/schedule.html'
	context_object_name = 'schedule'
	def get_queryset(self):
		"""Return all the events in order order."""
		return Event.objects.all().order_by('order')
	def get_context_data(self, *args, **kwargs):
		context = super(ScheduleView, self).get_context_data(*args, **kwargs)
		context['title'] = 'Schedule'
		return context


def index(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('user', args=(request.user.id,)))
	else:
		return render(request, 'rio/index.html', {'entries_open': settings.ENTRIES_OPEN})

@login_required
def user(request, pk):
	page_user = get_object_or_404(User, id=pk)
	if page_user.id != request.user.id and not request.user.is_superuser:
		messages.warning(request, "You just tried to access the wrong user page")
		return HttpResponseRedirect('/rio/')

	number_teams = Team.objects.all().count()
	start_date = datetime.strptime(settings.CLOSING_DATETIME, '%d/%m/%Y %H:%M %Z')
	
	return render(request, 'rio/user.html', 
				{'page_user': page_user, 
				'entries_open': settings.ENTRIES_OPEN,
				'progress': progress,
				'number_teams': number_teams,
				'start_date': start_date,
				'team_list': sorted(Team.objects.order_by('name'), key=lambda a: (a.points(), a.correct_golds()), reverse=True),
				})

@method_decorator(login_required, name='dispatch')
class LeaguesView(generic.ListView):
	template_name = 'rio/leagues.html'
	context_object_name = 'leagues'
	def get_queryset(self):
		"""Return all the leagues."""
		return League.objects.all()
	def get_context_data(self, *args, **kwargs):
		context = super(LeaguesView, self).get_context_data(*args, **kwargs)
		context['title'] = 'Leagues'
		return context

@method_decorator(login_required, name='dispatch')
class OverallView(generic.ListView):
	template_name = 'rio/overall.html'
	context_object_name = 'team_list'
	def get_queryset(self):
		"""Return all the teams."""
		return sorted(Team.objects.all().order_by('name'), key=lambda a: (a.points(), a.correct_golds()), reverse=True)
	def get_context_data(self, *args, **kwargs):
		context = super(OverallView, self).get_context_data(*args, **kwargs)
		context['entries_open'] = settings.ENTRIES_OPEN
		context['progress'] = progress
		context['title'] = 'Overall League'
		return context


@method_decorator(login_required, name='dispatch')
class LeagueView(generic.DetailView):
	model = League
	template_name = 'rio/league.html'
				
	def get_context_data(self, **kwargs):
		context = super(LeagueView, self).get_context_data(**kwargs)
		context['league_teams'] = Team.objects.filter(league=context['league']).order_by('name')
		context['entries_open'] = settings.ENTRIES_OPEN
		context['progress'] = progress
		context['title'] = context['league'].name
		return context


@method_decorator(login_required, name='dispatch')
class TeamView(generic.DetailView):
	model = Team
	template_name = 'rio/team.html'
				
	def get_context_data(self, **kwargs):
		context = super(TeamView, self).get_context_data(**kwargs)
		context['team_choices'] = Choice.objects.filter(team=context['team']).order_by('event_id')
		context['entries_open'] = settings.ENTRIES_OPEN
		context['title'] = context['team'].name
		return context


@method_decorator(login_required, name='dispatch')
class EventView(generic.DetailView):
	model = Event
	template_name = 'rio/event.html'
	
	def get_context_data(self, *args, **kwargs):
		context = super(EventView, self).get_context_data(*args, **kwargs)
		context['gold'] = Participant.objects.filter(event=context['event'], points=5)
		context['silver'] = Participant.objects.filter(event=context['event'], points=2)
		context['bronze'] = Participant.objects.filter(event=context['event'], points=1)		
		context['entries_open'] = settings.ENTRIES_OPEN
		context['title'] = context['event'].name
		context['participant_list'] = sorted(context['event'].participant_set.all(), key=lambda a: a.choice_count(), reverse=True)
		context['user_pick'] = Participant.objects.filter(event=context['event'], choice__team__user=self.request.user)
		return context

def register(request):
	if not settings.ENTRIES_OPEN:
		messages.error(request, "Entries have closed!")
		return HttpResponseRedirect('/rio/')
	context = RequestContext(request)
	if request.method == 'POST':
		user_form = UserCreateForm(request.POST)
		if user_form.is_valid():
			user = user_form.save()
			user = authenticate(username=user_form.cleaned_data.get('username'), password=user_form.cleaned_data.get('password1'))
			login(request, user)
			
			context.update({'user': user, 'site_name': get_current_site(request)})
			subject='Welcome to Fantasy Swimming!'
			body = loader.render_to_string('rio/welcome.html', context)
			from_email='fantasyswimming@gmail.com'
			to_email=user.email
			email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
			email_message.send()
			
			messages.info(request, 'Thanks for registering. Now create your team!')
			return HttpResponseRedirect(reverse('user', args=(request.user.id,)))
	else:
		user_form = UserCreateForm()
	return render(request,
		'rio/register.html',
		{'user_form':user_form, 'title': 'Register'},
		context)


# context = RequestContext(request)
@login_required
def league_edit(request, id=None):
	
	user = request.user
	
	if id:
		league = get_object_or_404(League, pk=id)
		title = 'Edit league'
		if league.creator != user:
			messages.warning(request, "You are not the creator of that league!")
			return HttpResponseRedirect(league.get_absolute_url())
		if not settings.ENTRIES_OPEN:
			messages.warning(request, "Entries closed, you can't edit your league")
			return HttpResponseRedirect(league.get_absolute_url())
	
	else:
		if not Team.objects.filter(user=request.user).exists():
			messages.warning(request, 'Create a team before you create a league!')
			return HttpResponseRedirect(reverse('user', args=(user.id,)))	
		if League.objects.filter(creator=user).exists():
			league = League.objects.get(creator=user)
			messages.warning(request, 'You have already created this league!')
			return HttpResponseRedirect(reverse('league', args=(league.id,)))
		if not settings.ENTRIES_OPEN:
			messages.warning(request, "Entries closed, you can't create a league")
			return HttpResponseRedirect(league.get_absolute_url())
		title = 'Create a league'
		league = League(creator=user)
	
	form = LeagueCreateForm(request.POST or None, instance=league)
		
	if request.method == 'POST':
		if form.is_valid():
			league = form.save(commit=False)
			league.date_created = datetime.now()
			league.save()
			team = user.team
			team.league = league
			team.save()
			messages.success(request, 'League created!')
			return HttpResponseRedirect(reverse('league', args=(league.id,)))

	return render(request, 'rio/league_edit.html', {'form': form, 'title': title, 'league': league})



@login_required
def team_edit(request, id=None):

	if id:
		team = get_object_or_404(Team, pk=id)
		title = 'Edit team'
		if team.user != request.user:
			messages.warning(request, "You just tried to edit the wrong team")
			return HttpResponseRedirect('/rio/')
	else:
		if Team.objects.filter(user=request.user).exists():
			messages.warning(request, "You already have a team!")
			return HttpResponseRedirect(request.user.team.get_absolute_url())
		if not settings.ENTRIES_OPEN:
			messages.warning(request, "Entries closed!")
			return HttpResponseRedirect('/rio/')
		team = Team(user=request.user)
		title = 'Create team'
	
	if not settings.ENTRIES_OPEN:
		messages.warning(request, "Entries closed!")
		return HttpResponseRedirect(team.get_absolute_url())
		
	event_list = Event.objects.all()

	edit_form = TeamEditForm(request.POST or None, instance=team)
	edit_formWR = TeamEditFormWR(request.POST or None, instance=team)
	
	choice_form_list = []
	for idx, event in enumerate(event_list):
		if id:
			choice_form_list.append(ChoiceEditForm(event, request.POST or None, 
									instance=Choice.objects.get(event=event, team=team), prefix=str(idx)))
		else:
			choice_form_list.append(ChoiceEditForm(event, request.POST or None, prefix=str(idx)))

	if request.method == "POST":
		if edit_form.is_valid() and edit_formWR.is_valid() and all([choice_form.is_valid() for choice_form in choice_form_list]):
			edit_form.save()
			edit_formWR.save()
			for choice_form in choice_form_list:
				choice = choice_form.save(commit=False)
				choice.team = team
				choice.event = choice_form.event
				choice.save()
			messages.info(request, 'Team changes saved')
			return HttpResponseRedirect(team.get_absolute_url())
		else:
			messages.error(request, "There's a problem with your team selection - please correct below")
		
	return render(request, 'rio/team_edit.html', 
					{'edit_form': edit_form, 
					'edit_formWR': edit_formWR, 
					'choice_form_list': choice_form_list,
					'title': title})