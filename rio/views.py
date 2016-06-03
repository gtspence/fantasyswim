from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from .forms import UserCreateForm
from django.contrib.auth.decorators import login_required



def index(request):
	template = loader.get_template('rio/index.html')
	context = {
	}
	return HttpResponse(template.render(context, request))
    

    
def register(request):
	context = RequestContext(request)
	
	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
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
		
