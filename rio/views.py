from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamEditForm, TeamEditFormWR, ChoiceEditForm
from django.contrib.auth.decorators import login_required
from .models import Team, Event, Swimmer, Participant, Choice
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.conf import settings

class IndexView(generic.ListView):
	template_name = 'rio/index.html'
	context_object_name = 'team_list'

	def get_queryset(self):
		"""Return all the teams."""
		return Team.objects.all()
	
	def get_context_data(self, *args, **kwargs):
		context = super(IndexView, self).get_context_data(*args, **kwargs)
		context['event_list'] = Event.objects.all()
		context['entries_open'] = settings.ENTRIES_OPEN
		if self.request.user.is_authenticated():
			try:
				context['user_team'] = Team.objects.get(user=self.request.user)
			except Team.DoesNotExist:
				context['user_team'] = None
		return context


@method_decorator(login_required, name='dispatch')
class TeamView(generic.DetailView):
	model = Team
	template_name = 'rio/team.html'
				
	def get_context_data(self, **kwargs):
		context = super(TeamView, self).get_context_data(**kwargs)
		context['team_choices'] = Choice.objects.filter(team=context['team'])
		context['entries_open'] = settings.ENTRIES_OPEN
		return context
		

@method_decorator(login_required, name='dispatch')
class EventView(generic.DetailView):
	model = Event
	template_name = 'rio/event.html'
	
	def get_context_data(self, *args, **kwargs):
		context = super(EventView, self).get_context_data(*args, **kwargs)
		context['entries_open'] = settings.ENTRIES_OPEN
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
		if team.user != request.user:
			return HttpResponseForbidden()
	else:
		if Team.objects.filter(user=request.user).exists():
			return HttpResponseRedirect(request.user.team.get_absolute_url())
		team = Team(user=request.user)
	
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
			return HttpResponseRedirect(team.get_absolute_url())
		
	return render(request, 'rio/team_edit.html', 
					{'edit_form': edit_form, 
					'edit_formWR': edit_formWR, 
					'choice_form_list': choice_form_list,
					'title': 'Create/edit team'},
					context_instance=RequestContext(request))