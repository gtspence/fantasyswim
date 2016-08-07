from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamEditForm, TeamEditFormWR, ChoiceEditForm, ContactForm, LeagueCreateForm
from django.contrib.auth.decorators import login_required
from .models import User, Team, Event, Swimmer, Participant, Choice, League, News
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import send_mass_mail, EmailMultiAlternatives
from django.contrib import messages
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from operator import attrgetter
from django.db import models
from django.db.models import Count, Q, Sum, Case, When, F, Value
from django.db.models.functions import Coalesce
from datetime import datetime

def get_progress():
	return int(round(float(Event.objects.filter(scored=True).count()) / Event.objects.all().count() * 100))

def get_all_teams():
	return Team.objects.annotate(
		total_points=Coalesce(Sum('choice__participant__points'), Value(0)) +
			Case(
				When(WR_event__wr=True, then=5),
				default=0,
				output_field=models.IntegerField()
				) + 
			Case(
				When(WR_event2__wr=True, then=5),
				default=0,
				output_field=models.IntegerField()
				) +
			Case(
				When(WR_event3__wr=True, then=5),
				default=0,
				output_field=models.IntegerField()
				),
		correct_golds=Sum(
			Case(
				When(choice__participant__points=5, then=1),
				default=0,
				output_field=models.IntegerField()
				)
			),
		).annotate(std_points=F('total_points')*100+F('correct_golds')).order_by('-std_points', 'name')

def rank_teams(teams):
	places = []
	prev_score = None
	for i, team in enumerate(teams):
		if team.std_points == prev_score:
			places.append(places[-1])
		else:
			places.append(i+1)
			prev_score = team.std_points
	return zip(places, teams)

def league_position(team, teams):
	position = sum([t.std_points > team.std_points for t in teams]) + 1
	joint = sum([t.std_points == team.std_points for t in teams]) > 1
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
	number_teams = Team.objects.all().count()
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('user', args=(request.user.id,)))
	else:
		return render(request, 'rio/index.html', 
					{'entries_open': settings.ENTRIES_OPEN,
					'number_teams': number_teams,
					})

@login_required
def user(request, pk):
	page_user = get_object_or_404(User, id=pk)
	if page_user.id != request.user.id and not request.user.is_superuser:
		messages.warning(request, "You just tried to access the wrong user page")
		return HttpResponseRedirect('/rio/')

	number_teams = Team.objects.all().count()
	start_date = datetime.strptime(settings.CLOSING_DATETIME, '%d/%m/%Y %H:%M %Z')
	
	team_stats = {}
	
	if settings.ENTRIES_OPEN == False:
		if get_all_teams().filter(user=page_user).select_related('league', 'user').exists():
			team = get_all_teams().get(user=page_user)
			teams = get_all_teams()
			team_stats['team'] = team
			overall_position = league_position(team, teams)
			team_stats['number_overall_teams'] = len(teams)
			team_stats['overall_position'] = ordinal(overall_position['position'])
			team_stats['overall_joint'] = overall_position['joint']
			if team.league:
				league_teams = teams.filter(league=team.league)
				minileague_position = league_position(team, league_teams)
				team_stats['number_league_teams'] = len(league_teams)
				team_stats['league_position'] = ordinal(minileague_position['position'])
				team_stats['league_joint'] = minileague_position['joint']
		else:
			team_stats['team'] = None
	
	user_news = News.objects.filter(Q(user=page_user) | Q(all_users=True)).select_related('event')
	
	return render(request, 'rio/user.html', 
				{'page_user': page_user, 
				'entries_open': settings.ENTRIES_OPEN,
				'progress': get_progress(),
				'number_teams': number_teams,
				'start_date': start_date,
				'team_list': Team.objects.order_by('name').select_related('league').select_related('user'),
				'user_news': user_news,
				'team_stats': team_stats
				})

@method_decorator(login_required, name='dispatch')
class LeaguesView(generic.ListView):
	template_name = 'rio/leagues.html'
	context_object_name = 'leagues'
	def get_queryset(self):
		"""Return all the leagues."""
		return League.objects.select_related('creator').prefetch_related('team_set')
	def get_context_data(self, *args, **kwargs):
		context = super(LeaguesView, self).get_context_data(*args, **kwargs)
		context['title'] = 'Leagues'
		context['entries_open'] = settings.ENTRIES_OPEN
		context['user_team_league'] = League.objects.filter(team__user=self.request.user)
		return context

@method_decorator(login_required, name='dispatch')
class OverallView(generic.ListView):
	template_name = 'rio/overall.html'
	if settings.ENTRIES_OPEN:
		context_object_name = 'teams'
		def get_queryset(self):
			"""Return all the teams."""
			return get_all_teams().select_related('league').select_related('user')
	else:
		context_object_name = 'ranks_and_teams'
		def get_queryset(self):
			"""Return all the teams and their ranks."""
			return rank_teams(get_all_teams().exclude(std_points=None).select_related('user'))
	def get_context_data(self, *args, **kwargs):
		context = super(OverallView, self).get_context_data(*args, **kwargs)
		context['entries_open'] = settings.ENTRIES_OPEN
		context['progress'] = get_progress()
		context['title'] = 'Overall League'
		return context


@method_decorator(login_required, name='dispatch')
class LeagueView(generic.DetailView):
	model = League
	template_name = 'rio/league.html'
				
	def get_context_data(self, **kwargs):
		context = super(LeagueView, self).get_context_data(**kwargs)
		if settings.ENTRIES_OPEN:
			context['teams'] = get_all_teams().filter(league=context['league']).select_related('user')
		else:
			context['ranks_and_teams'] = rank_teams(get_all_teams().filter(league=context['league']).exclude(std_points=None).select_related('user'))
		context['entries_open'] = settings.ENTRIES_OPEN
		context['progress'] = get_progress()
		context['title'] = context['league'].name
		return context


@method_decorator(login_required, name='dispatch')
class TeamView(generic.DetailView):
	model = Team
	template_name = 'rio/team.html'
	
	def get_context_data(self, **kwargs):
		context = super(TeamView, self).get_context_data(**kwargs)
		context['team_choices'] = Choice.objects.filter(team=context['team']).select_related('participant__swimmer').select_related('event').order_by('event_id')
		context['entries_open'] = settings.ENTRIES_OPEN
		context['title'] = context['team'].name
		
		teams = get_all_teams()
		team = get_all_teams().select_related('league').get(id=context['team'].id)
		overall_position = league_position(team, teams)
		context['number_overall_teams'] = len(teams)
		context['overall_position'] = ordinal(overall_position['position'])
		context['overall_joint'] = overall_position['joint']
		
		if context['team'].league:
			league_teams = teams.filter(league=team.league)
			minileague_position = league_position(team, league_teams)
			context['number_league_teams'] = len(league_teams)
			context['league_position'] = ordinal(minileague_position['position'])
			context['league_joint'] = minileague_position['joint']
		
		return context


@method_decorator(login_required, name='dispatch')
class EventView(generic.DetailView):
	model = Event
	template_name = 'rio/event.html'
	
	def get_context_data(self, *args, **kwargs):
		context = super(EventView, self).get_context_data(*args, **kwargs)
		context['entries_open'] = settings.ENTRIES_OPEN
		context['title'] = context['event'].name
		context['wr_count'] = Team.objects.filter(Q(WR_event=context['event']) | Q(WR_event2=context['event']) | Q(WR_event3=context['event'])).count()
		context['participant_list'] = sorted(Participant.objects.filter(event=context['event']).prefetch_related('choice_set'), key=lambda a: a.choice_count(), reverse=True)
		context['total_teams'] = len(get_all_teams())
# 		context['total_picks'] = sum([pick.choice_count() for pick in context['participant_list']])
		context['picks_percent'] = [int(round(part.choice_count() / float(context['total_teams']) * 100)) for part in context['participant_list']]
		context['participant_list_percent_zip'] = zip(context['participant_list'], context['picks_percent'])
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


@login_required
def league_edit(request, id=None):
	
	user = request.user
	
	if id:
		league = get_object_or_404(League, pk=id)
		title = 'Edit league'
		if league.creator != user:
			messages.warning(request, "You are not the creator of this league!")
			return HttpResponseRedirect(league.get_absolute_url())
		if not settings.ENTRIES_OPEN:
			messages.warning(request, "Entries closed, you can't edit your league")
			return HttpResponseRedirect(league.get_absolute_url())
	
	else:
		if not settings.ENTRIES_OPEN:
			messages.warning(request, "Entries closed, you can't create a league")
			return HttpResponseRedirect(reverse('user', args=(user.id,)))
		if not Team.objects.filter(user=request.user).exists():
			messages.warning(request, 'Create a team before you create a league!')
			return HttpResponseRedirect(reverse('user', args=(user.id,)))	
		if League.objects.filter(creator=user).exists():
			league = League.objects.get(creator=user)
			messages.warning(request, 'You have already created this league!')
			return HttpResponseRedirect(reverse('league', args=(league.id,)))
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
			if id:
				messages.success(request, 'League edited!')
			else:
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