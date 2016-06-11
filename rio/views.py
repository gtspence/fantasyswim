from django.http import HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamCreateForm, ChoiceCreateForm
from django.contrib.auth.decorators import login_required
from .models import Team, Event, Swimmer, Participant, Choice
from django.views import generic
from django.utils.decorators import method_decorator

class IndexView(generic.ListView):
	template_name = 'rio/index.html'
	context_object_name = 'team_list'

	def get_queryset(self):
		"""Return all the teams."""
		return Team.objects.all() #switch to order_by('score')


@method_decorator(login_required, name='dispatch')
class TeamView(generic.DetailView):
    model = Team
    template_name = 'rio/team.html'


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
def team_create(request):
	event_list = Event.objects.all() 
	if request.method == "POST":
		create_form = TeamCreateForm(request.POST)
		choice_form_list = [ChoiceCreateForm(event, request.POST, prefix=str(idx)) for idx, event in enumerate(event_list)]
		if create_form.is_valid() and all([choice_form.is_valid() for choice_form in choice_form_list]):
			team = create_form.save(commit=False)
			team.user = request.user
			team.save()
			for choice_form in choice_form_list:
			#	if choice_form.is_valid(): # and delete above if you want optional
				choice = choice_form.save(commit=False)
				choice.team = team
				choice.event = choice_form.event
				choice.save()
			return HttpResponseRedirect('/rio/')
	else:
		create_form = TeamCreateForm()
		choice_form_list = [ChoiceCreateForm(event, prefix=str(idx)) for idx, event in enumerate(event_list)]
		
	return render(request, 'rio/team_create.html', 
					{'create_form': create_form, 
					'choice_form_list': choice_form_list,
					'event_list': event_list,
					'title': 'Create team'})
