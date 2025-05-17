from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from analysis.models import Insight, ChatMessage

User = get_user_model()

class AnalysisAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='ana_user', password='pass123')
        self.client.force_authenticate(user=self.user)

        self.insight_url = '/analysis/insights/'
        self.chat_url    = '/analysis/chats/'

    def test_insight_list(self):
        # vazio inicialmente
        resp = self.client.get(self.insight_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

        # criar insights diretamente
        Insight.objects.create(
            user=self.user, insight_type='summary',
            content='Resumo X', data={}
        )
        Insight.objects.create(
            user=self.user, insight_type='forecast',
            content='Previsão Y', data={}
        )
        resp = self.client.get(self.insight_url)
        types = {i['insight_type'] for i in resp.data}
        self.assertSetEqual(types, {'summary','forecast'})

    def test_chat_crud(self):
        payload = {'role': 'user', 'message': 'Oi', 'metadata': {}}
        # CREATE
        resp = self.client.post(self.chat_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        chat_id = resp.data['id']

        # LIST
        resp = self.client.get(self.chat_url)
        self.assertEqual(len(resp.data), 1)

        # RETRIEVE
        resp = self.client.get(f'{self.chat_url}{chat_id}/')
        self.assertEqual(resp.data['message'], 'Oi')

        # UPDATE
        update = {'role': 'agent', 'message': 'Olá', 'metadata': {}}
        resp = self.client.put(f'{self.chat_url}{chat_id}/', update, format='json')
        self.assertEqual(resp.data['role'], 'agent')

        # DELETE
        resp = self.client.delete(f'{self.chat_url}{chat_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
