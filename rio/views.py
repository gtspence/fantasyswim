from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamEditForm, TeamEditFormWR, ChoiceEditForm, ContactForm
from django.contrib.auth.decorators import login_required
from .models import Team, Event, Swimmer, Participant, Choice
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

def rules(request):
	return render(request, 'rio/rules.html', context={'title':'Rules'})

@login_required
def contact(request):
	form_class = ContactForm
	context = RequestContext(request)
	
	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			form_message = request.POST.get('message', '')
			send_mail('Fantasy Swimming - Message from: ' + str(request.user), 
					message=form_message,
					from_email=request.user.email, 
					recipient_list=['fantasyswimming@gmail.com'])
			send_mail('Fantasy Swimming - Your Sent Message', 
					message=form_message,
					from_email='fantasyswimming@gmail.com', 
					recipient_list=[request.user.email])
			messages.info(request, 'Message sent to Fantasy Swimming Admin.')
			return HttpResponseRedirect('/rio/')
	
	return render(request, 'rio/contact.html', {'form': form_class, 'title':'Contact Us'}, context)


class EventsView(generic.ListView):
	template_name = 'rio/events.html'
	context_object_name = 'w_event_list'
	def get_queryset(self):
		"""Return all the teams."""
		return Event.objects.filter(name__startswith='W').order_by('id')
	def get_context_data(self, *args, **kwargs):
		context = super(EventsView, self).get_context_data(*args, **kwargs)
		context['m_event_list'] = Event.objects.filter(name__startswith='M').order_by('id')
		context['title'] = 'Events'
		return context

class IndexView(generic.ListView):
	template_name = 'rio/index.html'
	context_object_name = 'team_list'

	def get_queryset(self):
		"""Return all the teams."""
		return Team.objects.all().order_by('name')
	
	def get_context_data(self, *args, **kwargs):
		context = super(IndexView, self).get_context_data(*args, **kwargs)
		context['entries_open'] = settings.ENTRIES_OPEN
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
		context['entries_open'] = settings.ENTRIES_OPEN
		context['title'] = context['event'].name
		return context

def register(request):
	if not settings.ENTRIES_OPEN:
		return HttpResponseRedirect('/rio/')
	context = RequestContext(request)
	if request.method == 'POST':
		user_form = UserCreateForm(request.POST)
		if user_form.is_valid():
			user = user_form.save()
			user = authenticate(username=user_form.cleaned_data.get('username'), password=user_form.cleaned_data.get('password1'))
			login(request, user)
			send_mail('Welcome to Fantasy Swimming!', 
					message='Welcome to Fantasy Swimming', #Try welcome.html??
					from_email='fantasyswimming@gmail.com', 
					recipient_list=[user.email])
			messages.info(request, 'Thanks for registering. Now create a team!')
			return HttpResponseRedirect('/rio/')
	else:
		user_form = UserCreateForm()
	return render(request,
		'rio/register.html',
		{'user_form':user_form, 'title': 'Register'},
		context)
		

@login_required
def team_edit(request, id=None):

	if id:
		team = get_object_or_404(Team, pk=id)
		title = 'Edit team'
		if team.user != request.user:
			return HttpResponseForbidden()
	else:
		if Team.objects.filter(user=request.user).exists():
			return HttpResponseRedirect(request.user.team.get_absolute_url())
		team = Team(user=request.user)
		title = 'Create team'
	
	if not settings.ENTRIES_OPEN:
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
					'title': title},
					context_instance=RequestContext(request))