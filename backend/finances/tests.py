from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Category, Transaction, Goal

User = get_user_model()

class FinancesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='fin_user', password='pass123')
        self.client.force_authenticate(user=self.user)

        self.cat_url   = '/finances/categories/'
        self.trans_url = '/finances/transactions/'
        self.goal_url  = '/finances/goals/'

    def test_category_crud(self):
        # CREATE
        resp = self.client.post(self.cat_url,
                                {'name': 'Padaria', 'type': 'expense'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cat_id = resp.data['id']

        # LIST
        resp = self.client.get(self.cat_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

        # RETRIEVE
        resp = self.client.get(f'{self.cat_url}{cat_id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Padaria')

        # UPDATE
        resp = self.client.put(f'{self.cat_url}{cat_id}/',
                               {'name': 'Mercado', 'type': 'expense'},
                               format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Mercado')

        # DELETE
        resp = self.client.delete(f'{self.cat_url}{cat_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_transaction_crud(self):
        cat = Category.objects.create(user=self.user, name='Padaria', type='expense')
        payload = {
            'category': cat.id,
            'amount': '15.50',
            'raw_text': 'gastei 15.50 na padaria',
            'metadata': {}
        }
        # CREATE
        resp = self.client.post(self.trans_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        trans_id = resp.data['id']

        # LIST
        resp = self.client.get(self.trans_url)
        self.assertEqual(len(resp.data), 1)

        # RETRIEVE
        resp = self.client.get(f'{self.trans_url}{trans_id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['amount'], '15.50')

        # DELETE
        resp = self.client.delete(f'{self.trans_url}{trans_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_goal_crud(self):
        payload = {
            'name': 'Poupança',
            'target_amount': '1000.00',
            'start_date': '2025-01-01',
            'end_date': '2025-06-30',
            'frequency': 'one-time',
            'metadata': {}
        }
        # CREATE
        resp = self.client.post(self.goal_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        goal_id = resp.data['id']

        # LIST
        resp = self.client.get(self.goal_url)
        self.assertEqual(len(resp.data), 1)

        # RETRIEVE
        resp = self.client.get(f'{self.goal_url}{goal_id}/')
        self.assertEqual(resp.data['name'], 'Poupança')

        # UPDATE
        update_payload = {
            'name': 'Investimento',
            'target_amount': '2000.00',
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'frequency': 'monthly',
            'metadata': {}
        }
        resp = self.client.put(f'{self.goal_url}{goal_id}/', update_payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Investimento')

        # DELETE
        resp = self.client.delete(f'{self.goal_url}{goal_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
