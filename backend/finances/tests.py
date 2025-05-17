import json
from io import StringIO, BytesIO
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from finances.models import Category, Transaction, Goal
from finances.services import (
    parse_transaction_text,
    parse_goal_text,
    generate_30day_report
)

User = get_user_model()

class ParseServicesTestCase(TestCase):
    def test_parse_transaction_no_api_key(self):
        with patch('finances.services.os.getenv', return_value=None):
            result = parse_transaction_text("gastei 15 reais na padaria")
        self.assertEqual(result, {
            'amount': None,
            'date': None,
            'category': None,
            'location': None,
            'type': None
        })

    @patch('finances.services.genai.Client')
    def test_parse_transaction_success(self, mock_Client):
        dummy = {
            'amount': 23.5,
            'date': '2025-05-17',
            'category': 'Padaria',
            'location': 'Padaria Central',
            'type': 'expense'
        }
        with patch('finances.services.os.getenv', return_value='fake-key'):
            inst = MagicMock()
            chat = MagicMock()
            chat.send_message.return_value = type('R', (), {'text': json.dumps(dummy)})()
            inst.chats.create.return_value = chat
            mock_Client.return_value = inst

            result = parse_transaction_text("gastei 23.5 na padaria")
        self.assertEqual(result, dummy)

    @patch('finances.services.genai.Client')
    def test_parse_transaction_invalid_json(self, mock_Client):
        with patch('finances.services.os.getenv', return_value='fake-key'):
            inst = MagicMock()
            chat = MagicMock()
            chat.send_message.return_value = type('R', (), {'text': 'não é JSON'})()
            inst.chats.create.return_value = chat
            mock_Client.return_value = inst

            result = parse_transaction_text("texto irreconhecível")
        self.assertEqual(result, {
            'amount': None,
            'date': None,
            'category': None,
            'location': None,
            'type': None
        })

    def test_parse_goal_no_api_key(self):
        with patch('finances.services.os.getenv', return_value=None):
            result = parse_goal_text("quero poupar 1000 até fim do ano mensalmente")
        self.assertEqual(result, {
            'target_amount': None,
            'start_date': None,
            'end_date': None,
            'frequency': None,
            'name': None
        })

    @patch('finances.services.genai.Client')
    def test_parse_goal_success(self, mock_Client):
        dummy = {
            'target_amount': 1000.0,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'frequency': 'monthly',
            'name': 'Poupança Anual'
        }
        with patch('finances.services.os.getenv', return_value='fake-key'):
            inst = MagicMock()
            chat = MagicMock()
            chat.send_message.return_value = type('R', (), {'text': json.dumps(dummy)})()
            inst.chats.create.return_value = chat
            mock_Client.return_value = inst

            result = parse_goal_text("quero poupar 1000 até dezembro de forma mensal")
        self.assertEqual(result, dummy)

    @patch('finances.services.genai.Client')
    def test_parse_goal_invalid_json(self, mock_Client):
        with patch('finances.services.os.getenv', return_value='fake-key'):
            inst = MagicMock()
            chat = MagicMock()
            chat.send_message.return_value = type('R', (), {'text': 'oops'})()
            inst.chats.create.return_value = chat
            mock_Client.return_value = inst

            result = parse_goal_text("texto irreconhecível")
        self.assertEqual(result, {
            'target_amount': None,
            'start_date': None,
            'end_date': None,
            'frequency': None,
            'name': None
        })


class ReportServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u', 'u@u.com', 'pass')
        cat = Category.objects.create(user=self.user, name='Test', type='expense')
        # dentro dos últimos 30 dias
        Transaction.objects.create(
            user=self.user, category=cat, amount=100,
            raw_text='r', metadata={'type':'expense'},
            timestamp=timezone.now() - timedelta(days=10)
        )
        # fora do período (40 dias atrás)
        Transaction.objects.create(
            user=self.user, category=cat, amount=200,
            raw_text='r', metadata={'type':'expense'},
            timestamp=timezone.now() - timedelta(days=40)
        )

    def test_generate_30day_report(self):
        report = generate_30day_report(self.user)
        self.assertEqual(report['total_expense'], 100.0)
        self.assertEqual(report['total_income'], 0.0)
        self.assertEqual(len(report['by_category']), 1)
        entry = report['by_category'][0]
        self.assertEqual(entry['category'], 'Test')
        self.assertEqual(entry['total'], 100.0)
        self.assertEqual(entry['count'], 1)


class FinancesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('fin', 'fin@x.com', 'pass')
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

    @patch('finances.views.parse_transaction_text')
    def test_transaction_parsing_endpoint(self, mock_parse):
        mock_parse.return_value = {
            'amount': 15.0,
            'date': '2025-05-17',
            'category': 'Padaria',
            'location': 'Padaria Central',
            'type': 'expense'
        }
        payload = {'raw_text': 'gastei 15 reais na padaria', 'amount':'0'}
        resp = self.client.post(self.trans_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        mock_parse.assert_called_once_with('gastei 15 reais na padaria')
        self.assertEqual(resp.data['metadata'], mock_parse.return_value)
        self.assertEqual(resp.data['amount'], '15.00')
        cat = Category.objects.get(user=self.user, name='Padaria', type='expense')
        self.assertEqual(resp.data['category'], cat.id)

    def test_export_csv_endpoint(self):
        resp = self.client.get(f'{self.trans_url}export_csv/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')

    def test_export_pdf_endpoint(self):
        resp = self.client.get(f'{self.trans_url}export_pdf/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')

    def test_report_30days_endpoint(self):
        resp = self.client.get(f'{self.trans_url}report_30days/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('total_expense', data)
        self.assertIn('by_category', data)
