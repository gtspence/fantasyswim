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
def team_edit(request, id=None):
	if id:
		team = get_object_or_404(Team, pk=id)
		if team.user != request.user:
			return HttpResponseForbidden()
	else:
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
			return HttpResponseRedirect(reverse('team', args=(team.id,)))
		
	return render(request, 'rio/team_edit.html', 
					{'edit_form': edit_form, 
					'choice_form_list': choice_form_list,
					'event_list': event_list,
					'title': 'Create/edit team'},
					context_instance=RequestContext(request))
