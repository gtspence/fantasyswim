from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm, TeamCreateForm, ChoiceCreateForm
from django.contrib.auth.decorators import login_required
from .models import Team, Event, Swimmer, Participant, Choice


def index(request):
	template = loader.get_template('rio/index.html')
	context = {
	}
	return HttpResponse(template.render(context, request))
	


def register(request):
	context = RequestContext(request)
	
	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		user_form = UserCreateForm(request.POST)
		
		# If the two forms are valid...
		if user_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()
			user = authenticate(username=user_form.cleaned_data.get('username'), password=user_form.cleaned_data.get('password1'))
			login(request, user)
			return HttpResponseRedirect('/rio/')
		
		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print user_form.errors

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserCreateForm()
		
	return render_to_response(
		'rio/register.html',
		{'user_form':user_form, 'title': 'Register'},
		context)
		

@login_required
def team_create(request):
	event_list = Event.objects.all() 
	if request.method == "POST":
		create_form = TeamCreateForm(request.POST)
		choice_form_list = [ChoiceCreateForm(event, request.POST) for event in event_list]
		if create_form.is_valid() and all([choice_form.is_valid() for choice_form in choice_form_list]):
			team = create_form.save(commit=False)
			team.user = request.user
			team.save()
			for choice_form in choice_form_list:
				choice = choice_form.save(commit=False)
				choice.team = team
				choice.event = choice_form.event
				choice.save()
			return HttpResponseRedirect('/rio/')
	else:
		create_form = TeamCreateForm()
		choice_form_list = [ChoiceCreateForm(event) for event in event_list]
		
	return render(request, 'rio/create_team.html', 
					{'create_form': create_form, 
					'choice_form_list': choice_form_list,
					'event_list': event_list})