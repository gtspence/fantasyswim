from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Team, Event, Swimmer, Participant, Choice
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class ContactForm(forms.Form):
	message = forms.CharField(
		required=True,
		widget=forms.Textarea,
	)


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
		self.fields['WR_event'].queryset = Event.objects.filter()
		self.fields['WR_event2'].queryset = Event.objects.filter(relay=False)
		self.fields['WR_event3'].queryset = Event.objects.filter(relay=False)
	class Meta:
		model = Team
		fields = ('WR_event', 'WR_event2', 'WR_event3')	
	def clean(self):
		cleaned_data=super(TeamEditFormWR, self).clean()
		wr1 = cleaned_data.get("WR_event")
		wr2 = cleaned_data.get("WR_event2")
		wr3 = cleaned_data.get("WR_event3")
		wrs = filter(None, [wr1, wr2, wr3])
		for event in wrs:
			if event.relay == True:
				raise forms.ValidationError("Can't select relay event!")
		if len(wrs) > len(set(wrs)):
			raise forms.ValidationError("Select different events!")
		return cleaned_data
	
class ChoiceEditForm(forms.ModelForm):
	def __init__(self, event, *args, **kwargs):
		super (ChoiceEditForm, self ).__init__(*args, **kwargs)
		self.fields['participant'].queryset = event.participant_set.select_related('swimmer')
		self.event = event
	class Meta:
		model = Choice
		fields = ['participant']
		labels = {'participant':''}
	def clean(self):
		cleaned_data=super(ChoiceEditForm, self).clean()
		participant = cleaned_data.get('participant')
		if participant:
			if participant not in Participant.objects.filter(event=self.event):
				raise forms.ValidationError("Choice must be from this event!")
		return cleaned_data
	


