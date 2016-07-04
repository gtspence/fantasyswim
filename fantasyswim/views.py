from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def home(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('user', args=(request.user.id,)))
	else:
		return HttpResponseRedirect('/rio/')
