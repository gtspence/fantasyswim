from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Team, Event, Swimmer, Participant, Choice

class UserCreateForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(UserCreateForm, self).save(commit=False)
		user.email = self.cleaned_data["email"]
		if commit:
			user.save()
		return user

class TeamEditForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ['name']

class TeamEditFormWR(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super (TeamEditFormWR, self ).__init__(*args, **kwargs)
		self.fields['WR_event'].queryset = Event.objects.filter(relay=False)
		self.fields['WR_event2'].queryset = Event.objects.filter(relay=False)
		self.fields['WR_event3'].queryset = Event.objects.filter(relay=False)
	class Meta:
		model = Team
		fields = ('WR_event', 'WR_event2', 'WR_event3')	
	def clean(self):
		#run the standard clean method first
		cleaned_data=super(TeamEditFormWR, self).clean()
		wr1 = cleaned_data.get("WR_event")
		wr2 = cleaned_data.get("WR_event2")
		wr3 = cleaned_data.get("WR_event3")
		wrs = filter(None, [wr1, wr2, wr3])
		#check if passwords are entered and match
		if len(wrs) > len(set(wrs)):
			raise forms.ValidationError("Select different events!")
		#always return the cleaned data
		return cleaned_data
	
class ChoiceEditForm(forms.ModelForm):
	def __init__(self, event, *args, **kwargs):
		super (ChoiceEditForm, self ).__init__(*args, **kwargs)
		self.fields['participant'].queryset = Participant.objects.filter(event=event)
# 		self.fields['participant'].required = False
		self.event = event
	class Meta:
		model = Choice
		fields = ['participant']