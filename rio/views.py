from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamEditForm, ChoiceEditForm
from django.contrib.auth.decorators import login_required
from .models import Team, Event, Swimmer, Participant, Choice
from django.views import generic
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
#from django.db.models import Count

class IndexView(generic.ListView):
	template_name = 'rio/index.html'
	context_object_name = 'team_list'

	def get_queryset(self):
		"""Return all the teams."""
		return Team.objects.all() #switch to order_by('score')
	
	def get_context_data(self, *args, **kwargs):
		context = super(IndexView, self).get_context_data(*args, **kwargs)
		context['event_list'] = Event.objects.all()
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


@method_decorator(login_required, name='dispatch')
class EventView(generic.DetailView):
	model = Event
	template_name = 'rio/event.html'
	
# 	def get_context_data(self, *args, **kwargs):
# 		context = super(EventView, self).get_context_data(*args, **kwargs)
# 		context['common_choice'] = Participant.objects.filter(event=self.event).annotate(c=Count('choice')).order_by('-c')[0] 
# 		return context
## Doesn't work with self.event.... https://docs.djangoproject.com/en/1.9/topics/class-based-views/generic-display/#dynamic-filtering
## What about ties? https://docs.djangoproject.com/en/1.9/topics/db/aggregation/

def register(request):
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
	
	event_list = Event.objects.all()

	edit_form = TeamEditForm(request.POST or None, instance=team)
	
	choice_form_list = []
	for idx, event in enumerate(event_list):
		if Choice.objects.filter(event=event, team=team).exists():
			choice_form_list.append(ChoiceEditForm(event, request.POST or None, 
									instance=Choice.objects.get(event=event, team=team), prefix=str(idx)))
		else:
			choice_form_list.append(ChoiceEditForm(event, request.POST or None, prefix=str(idx)))	

	if request.method == "POST":
		if edit_form.is_valid(): # and all([choice_form.is_valid() for choice_form in choice_form_list]):
			edit_form.save()
			for choice_form in choice_form_list:
				if choice_form.is_valid(): # and delete above if you want optional
					choice = choice_form.save(commit=False)
					choice.team = team
					choice.event = choice_form.event
					choice.save()
			return HttpResponseRedirect(team.get_absolute_url())
		
	return render(request, 'rio/team_edit.html', 
					{'edit_form': edit_form, 
					'choice_form_list': choice_form_list,
					'event_list': event_list,
					'title': 'Create/edit team'},
					context_instance=RequestContext(request))