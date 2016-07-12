from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from .models import User, Event, Team, Swimmer, Participant, Choice
from .forms import UserCreateForm, TeamEditForm, TeamEditFormWR, ChoiceEditForm, ContactForm

# import pdb; pdb.set_trace()

class FormTests(TestCase):

	fixtures = ['test_data.json']
	
	def setUp(self):
		self.team = Team.objects.all()[0]
		self.user = self.team.user
		self.correct_event = Event.objects.all()[0]
		self.incorrect_event = Event.objects.all()[1]
		self.participant = self.correct_event.participant_set.all()[0]
		self.participant2 = self.correct_event.participant_set.all()[1]

	def test_choice_edit_form_true(self):
		form = ChoiceEditForm(self.correct_event, {'participant': self.participant.id}, instance=Choice.objects.get(event=self.correct_event, team=self.team))
		self.assertTrue(form.is_valid())

	def test_choice_edit_form_false(self):
		form = ChoiceEditForm(self.incorrect_event, {'participant': self.participant.id}, instance=Choice.objects.get(event=self.correct_event, team=self.team))
		self.assertEqual(form.errors, {'participant': [u'Select a valid choice. That choice is not one of the available choices.']})


	def test_WR_event_form_correct(self):
		form = TeamEditFormWR({'WR_event': Event.objects.all()[0].id,
								'WR_event2': Event.objects.all()[1].id,
								'WR_event3': Event.objects.all()[2].id}, instance=self.team)
		self.assertTrue(form.is_valid())

	def test_WR_event_form_two_same(self):
		form = TeamEditFormWR({'WR_event': Event.objects.all()[0].id,
								'WR_event2': Event.objects.all()[0].id,
								'WR_event3': Event.objects.all()[1].id})
		self.assertEqual(form.errors, {'__all__': [u'Select different events!']})
		
	def test_WR_event_form_can_leave_blank(self):
		form = TeamEditFormWR({'WR_event': Event.objects.all()[0].id,
								'WR_event2': None,
								'WR_event3': None})
		self.assertTrue(form.is_valid())
		
	def test_WR_event_form_cant_select_relay(self):
		form = TeamEditFormWR({'WR_event': Event.objects.filter(relay=True)[0].id,
								'WR_event2': None,
								'WR_event3': None})
		self.assertEqual(form.errors, {'WR_event': [u'Select a valid choice. That choice is not one of the available choices.']})

	def test_repeated_choices(self):
		form = ChoiceEditForm(self.correct_event, {'participant': self.participant.id}, instance=Choice.objects.get(event=self.correct_event, team=self.team))
		form.save()
		form = ChoiceEditForm(self.correct_event, {'participant': self.participant2.id}, instance=Choice.objects.get(event=self.correct_event, team=self.team))
		form.save()
		self.assertEqual(Choice.objects.get(event=self.correct_event, team=self.team).participant.id, self.participant2.id)


class TeamEditEntriesClosedTests(TestCase):

	fixtures = ['test_data.json']
	
	@override_settings(ENTRIES_OPEN=False)
	def test_cant_access_registration(self):
		rsp = self.client.get('/rio/register/')
		self.assertRedirects(rsp, '/rio/')
	
	@override_settings(ENTRIES_OPEN=False)
	def test_cant_access_team_edit(self):
		user = Team.objects.all()[0].user
		self.client.force_login(user)
		team_edit_url = '/rio/team_edit/%s/' % user.team.id
		rsp = self.client.get(team_edit_url)
		self.assertRedirects(rsp, user.team.get_absolute_url())
	
	@override_settings(ENTRIES_OPEN=False)
	def test_cant_access_team_create(self):
		user = User.objects.create_user(username='asdfs', email='asdf@example.com', password='xxxx')
		self.client.force_login(user)
		rsp = self.client.get('/rio/team_new/')
		self.assertRedirects(rsp, '/rio/', target_status_code=302)


# class LeagueTests(TestCase):
# 	
# 	fixtures = ['test_data2.json']

class TeamEditEntriesOpenTests(TestCase):
	
	fixtures = ['test_data.json']
		
	@override_settings(ENTRIES_OPEN=True)
	def test_can_access_own_team_edit(self):
		user = Team.objects.all()[0].user
		right_team = Team.objects.all()[0]
		self.client.force_login(user)
		right_team_edit_url = '/rio/team_edit/%s/' % user.team.id
		rsp = self.client.get(right_team_edit_url)
		self.assertEqual(rsp.status_code, 200)
	
	
	@override_settings(ENTRIES_OPEN=True)
	def test_cant_access_other_users_team_edit(self):
		user = Team.objects.all()[0].user
		wrong_team = Team.objects.all()[1]
		self.client.force_login(user)
		wrong_team_edit_url = '/rio/team_edit/%s/' % wrong_team.id
		rsp = self.client.get(wrong_team_edit_url)
		self.assertRedirects(rsp, '/rio/', target_status_code=302)

	@override_settings(ENTRIES_OPEN=True)
	def test_cant_create_second_team(self):
		user = Team.objects.all()[0].user
		right_team = Team.objects.all()[0]
		self.client.force_login(user)
		rsp = self.client.get('/rio/team_new/')
		self.assertRedirects(rsp, user.team.get_absolute_url())
	
# 	def test_can_see_own_team(self):
# 		user = Team.objects.all()[0].user
# 		self.client.force_login(user)
# 		rsp = self.client.get(user.team.get_absolute_url())
# 		self.assertNotContains(rsp, "<p>Other people's choices will be shown when entries close!</p>")
# # 		self.assertContains(rsp, )
# 	
# 	def test_cant_see_other_users_team(self):
# 		user = Team.objects.all()[0].user
# 		wrong_team = Team.objects.all()[1]
# 		self.client.force_login(user)
# 		rsp = self.client.get(wrong_team.get_absolute_url())
# 		self.assertContains(rsp, "<p>Other people's choices will be shown when entries close!</p>")
# # 		self.assertNotContains(rsp, )
# # 		
# 		
		# 	
# 	def league_table_correct_ordering(self):
	
	
	
# 		resp = self.client.post(reverse('team_edit/', kwargs={'id':user.id}))
# 		self.assert
	



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
# class MyTests(TestCase):
#     def test_forms(self):
#         response = self.client.post("/my/form/", {'something':'something'})
#         self.assertFormError(response, 'form', 'something', 'This field is required.')