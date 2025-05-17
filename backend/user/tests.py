from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        base = '/user/users/'
        self.register_url = base + 'register/'
        self.login_url    = base + 'login/'
        self.refresh_url  = base + 'refresh/'
        self.logout_url   = base + 'logout/'
        self.profile_url  = base + 'profile/'
        self.update_url   = base + 'update/'

        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'strong-pass-123',
            'phone': '1234567890',
            'timezone': 'America/Sao_Paulo',
            'currency': 'BRL'
        }

    def test_register(self):
        resp = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', resp.data)
        self.assertEqual(resp.data['user']['email'], self.user_data['email'])

    def test_login_and_profile(self):
        # register
        self.client.post(self.register_url, self.user_data, format='json')

        # login
        resp = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.cookies)
        self.assertIn('refresh', resp.cookies)

        access_token = resp.cookies['access'].value
        # access profile with Bearer token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        prof = self.client.get(self.profile_url)
        self.assertEqual(prof.status_code, status.HTTP_200_OK)
        self.assertEqual(prof.data['username'], self.user_data['username'])

    def test_update_profile(self):
        # register & login
        self.client.post(self.register_url, self.user_data, format='json')
        login = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }, format='json')
        access_token = login.cookies['access'].value
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        # perform update
        resp = self.client.put(self.update_url, {'first_name': 'Changed'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['first_name'], 'Changed')

    def test_refresh_and_logout(self):
        # register & login
        self.client.post(self.register_url, self.user_data, format='json')
        login = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }, format='json')
        refresh_token = login.cookies['refresh'].value

        # refresh
        resp = self.client.post(self.refresh_url, {},
                                **{'HTTP_COOKIE': f'refresh={refresh_token}'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.cookies)

        # logout
        resp2 = self.client.post(self.logout_url, {},
                                 **{'HTTP_COOKIE': f'refresh={refresh_token}'})
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        # cookies should be deleted (value empty)
        self.assertEqual(resp2.cookies['access'].value, '')
        self.assertEqual(resp2.cookies['refresh'].value, '')

    def test_invalid_login(self):
        resp = self.client.post(self.login_url, {
            'username': 'wrong',
            'password': 'nope'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', resp.data)
