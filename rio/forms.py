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

class TeamCreateForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ['name']
	
class ChoiceCreateForm(forms.ModelForm):
	def __init__(self, event, *args, **kwargs):
		super (ChoiceCreateForm, self ).__init__(*args, **kwargs)
		self.fields['participant'].queryset = Participant.objects.filter(event=event)
		self.event = event
		
	class Meta:
		model = Choice
		fields = ['participant']