from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import User, Event, Team, Swimmer, Participant, Choice
from .forms import UserCreateForm, TeamEditForm, TeamEditFormWR, ChoiceEditForm, ContactForm



class TeamEditTest(TestCase):

	fixtures = ['test_data.json']
	
	def setUp(self):
		team = Team.objects.all()[0]
		user = team.user
		force_login(user)
		correct_event = Event.objects.all()[0]
		incorrect_event = Event.objects.all()[1]
		participant = Participant.objects.filter(event=correct_event)[0]

	def test_choice_edit_form_correct(self):
		resp = self.client.post(reverse('team_edit/', kwargs={'id':user.id}))
		self.assert

# 	def test_choice_edit_form_true(self):
# 		form = ChoiceEditForm(event, {'participant': participant}, instance=Choice.objects.get(event=event, team=team))
# 		self.assertTrue(form.is_valid())
# 
# 	def test_choice_edit_form_false(self):
# 		form = ChoiceEditForm(incorrect_event, {'participant': participant}, instance=Choice.objects.get(event=correct_event, team=team))
# 		self.assertFalse(form.is_valid())
	
# 	def test_WR_event_form(self):
# 		form = TeamEditFormWR({'WR_event': Event.objects.all()[0],
# 								'WR_event2': Event.objects.all()[0],
# 								'WR_event3': Event.objects.all()[1]})
# 		self.assertFalse(form.is_valid())
# 		
# 	def test_WR_event_form_can_leave_blank(self):
# 		form = TeamEditFormWR({'WR_event': Event.objects.all()[0],
# 								'WR_event2': None,
# 								'WR_event3': None})
# 		self.assertTrue(form.is_valid())
# 		
# 	def test_WR_event_form_cant_select_relay(self):
# 		relay = Event.objects.filter(relay=True)[0]
# 		form = TeamEditFormWR({'WR_event': relay,
# 								'WR_event2': None,
# 								'WR_event3': None})
# 		self.assertFalse(form.is_valid())


# class TeamEditViewTest(TestCase):
# 	fixtures = ['data.json']
# 	
# 	def test_only_valid_participants_listed(self):
# 	"""
# 	Only participants in that event should be listed
# 	"""
# 	response = self.client.get(reverse('polls:index'))

# def create_event(name, relay=False):
# 	return Event.objects.create(name=name, relay=relay)
# 
# def create_swimmer(name="Joe Bloggs", country="USA"):
# 	return Swimmer.objects.create(name=name, country=country)
# 
# def create_participant(event_name, swimmer_name="Joe Bloggs"):
# 	event = Event.objects.get(name=event_name)
# 	swimmer = Swimmer.objects.get(name=swimmer_name)
# 	return Participant.objects.create(event=event, swimmer=swimmer)
# 


# 
# 
# def test_valid_form(self):
#     w = Whatever.objects.create(title='Foo', body='Bar')
#     data = {'title': w.title, 'body': w.body,}
#     form = WhateverForm(data=data)
#     self.assertTrue(form.is_valid())
# 
# def test_invalid_form(self):
#     w = Whatever.objects.create(title='Foo', body='')
#     data = {'title': w.title, 'body': w.body,}
#     form = WhateverForm(data=data)
#     self.assertFalse(form.is_valid())
# 
# class MyTests(TestCase):
#     def test_forms(self):
#         form_data = {'something': 'something'}
#         form = MyForm(data=form_data)
#         self.assertTrue(form.is_valid())
# 
# class MyTests(TestCase):
#     def test_forms(self):
#         response = self.client.post("/my/form/", {'something':'something'})
#         self.assertFormError(response, 'form', 'something', 'This field is required.')