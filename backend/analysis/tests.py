import json
from django.test import TestCase
from unittest.mock import patch, MagicMock

from finances.services import (
    parse_transaction_text,
    parse_goal_text
)

class ParseServicesTestCase(TestCase):
    def test_parse_transaction_no_api_key(self):
        # Sem GOOGLE_API_KEY -> retorna dict com None
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
        # Com API_KEY e resposta JSON válida
        dummy = {
            'amount': 23.5,
            'date': '2025-05-17',
            'category': 'Padaria',
            'location': 'Padaria Central',
            'type': 'expense'
        }
        # mock os.getenv para retornar uma chave qualquer
        with patch('finances.services.os.getenv', return_value='fake-key'):
            # configura o client e o chat
            inst = MagicMock()
            chat = MagicMock()
            chat.send_message.return_value = type('R', (), {'text': json.dumps(dummy)})()
            inst.chats.create.return_value = chat
            mock_Client.return_value = inst

            result = parse_transaction_text("gastei 23.5 na padaria")
        self.assertEqual(result, dummy)

    @patch('finances.services.genai.Client')
    def test_parse_transaction_invalid_json(self, mock_Client):
        # Com API_KEY mas resposta inválida (JSONDecodeError)
        with patch('finances.services.os.getenv', return_value='fake-key'):
            inst = MagicMock()
            chat = MagicMock()
            chat.send_message.return_value = type('R', (), {'text': 'não é JSON'})()
            inst.chats.create.return_value = chat
            mock_Client.return_value = inst

            result = parse_transaction_text("algo estranho")
        self.assertEqual(result, {
            'amount': None,
            'date': None,
            'category': None,
            'location': None,
            'type': None
        })

    def test_parse_goal_no_api_key(self):
        # Sem API_KEY -> dict de None
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
        # Com API_KEY e JSON válido
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
