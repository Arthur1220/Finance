import os, json
from google import genai
from google.genai import types

MODEL_ID = 'gemini-2.0-flash'

def parse_transaction_text(raw_text: str) -> dict:
    """
    Envia raw_text para o Gemini e espera um JSON com:
      - amount, date, category, location, type
    Se não estiver configurado (sem API_KEY), devolve todos os campos None.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Em ambiente de testes ou sem configuração, não tenta instanciar o client
        return {
            'amount': None,
            'date': None,
            'category': None,
            'location': None,
            'type': None
        }

    client = genai.Client(api_key=api_key)
    system_instruction = (
        "Você é um parser financeiro. "
        "Retorne apenas um JSON com amount, date, category, location, type."
    )
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=256,
        temperature=0
    )
    chat = client.chats.create(model=MODEL_ID, config=config)
    resposta = chat.send_message(f"Texto: \"{raw_text}\"").text

    try:
        return json.loads(resposta)
    except json.JSONDecodeError:
        return {
            'amount': None,
            'date': None,
            'category': None,
            'location': None,
            'type': None
        }

def parse_goal_text(raw_text: str) -> dict:
    """
    Recebe algo como "quero poupar 1000 até 31/12 criando mensalmente"
    e retorna um dict com chaves:
      - target_amount: float
      - start_date: 'YYYY-MM-DD'
      - end_date:   'YYYY-MM-DD'
      - frequency:  'one-time'|'monthly'|'yearly'
      - name:       string resumida da meta
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return {
            'target_amount': None,
            'start_date': None,
            'end_date': None,
            'frequency': None,
            'name': None
        }

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é um parser de metas financeiras. "
            "Extraia do texto um JSON com as chaves: "
            "target_amount, start_date, end_date, frequency, name."
        ),
        max_output_tokens=256,
        temperature=0
    )
    chat = client.chats.create(model=MODEL_ID, config=config)
    prompt = f"Meta: \"{raw_text}\""
    resposta = chat.send_message(prompt).text

    try:
        return json.loads(resposta)
    except json.JSONDecodeError:
        return {
            'target_amount': None,
            'start_date': None,
            'end_date': None,
            'frequency': None,
            'name': None
        }