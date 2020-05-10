from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse

from healthcare.views import (list_sessions, add_download_links, 
                              replace_current_and_order_desc)

TEST_USER = 'test'
TEST_PASSWORD = 'Password-1'
TEST_SESSION = '79038230252081'

User = get_user_model()


@tag('end_to_end')
class SessionsEndToEndTestCase(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            username=TEST_USER, password=TEST_PASSWORD)

    def test_get_ongoing_sessions(self):
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.get(reverse('sessions_index'))
        self.assertEqual(response.status_code, 200)

    def test_get_scheduled_sessions(self):
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.get(reverse('scheduled'))
        self.assertEqual(response.status_code, 200)

    def test_patient_session(self):
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.get('/sessions/patient/%s' % TEST_SESSION)
        self.assertEqual(response.status_code, 200)

@tag('unit')
class SessionsUnitTestCase(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            username=TEST_USER, password=TEST_PASSWORD)
    
    def test_update_data(self):
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.post(reverse('update'),
                                    {'order': 'desc'})
        self.assertEqual(response.status_code, 200)
    
    def test_sharing(self):
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        session = {
            'session_id': '00812668162133',
            'session_shared': 1
        }
        response = self.client.post(reverse('sharing'), session)
        self.assertEqual(response.status_code, 200)

    def test_create_session(self):
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        session ={
            'session_id': TEST_SESSION,
            'new_session_date': '2020-06-10',
            'new_session_time': '10:00'
        }
        response = self.client.post(reverse('create_session'), session, 
                                    HTTP_REFERER='/sessions/patien/%s' % TEST_SESSION)
        self.assertEqual(response.status_code, 302)

    def test_list_sessions(self):
        sessions = list_sessions()
        self.assertEqual(type(sessions), list)
    
    def test_add_download_links(self):
        sessions = list_sessions()
        add_download_links(sessions)
        for session in sessions:
            for document in session.get('session_documents'):
                if document.get('document_name') == 'Session Record':
                    continue
                self.assertEqual(type(document.get('download_link')), str)
    
    def test_replace_current_and_order_desc(self):
        sessions = [
            {'session_id': 5},
            {'session_id': 4},
            {'session_id': 3},
            {'session_id': 2},
            {'session_id': 1},
            ]
        validate_sessions = [
            {'session_id': 1},
            {'session_id': 2},
            {'session_id': 3},
            {'session_id': 4},
            {'session_id': 5},
            ]
        user_session = {'session_id': 3}
        reordered_sessions = replace_current_and_order_desc(sessions, 
                                                            user_session)
        self.assertEqual(reordered_sessions, validate_sessions)