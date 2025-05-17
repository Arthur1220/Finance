import os, json
from google import genai
from google.genai import types
from .models import Insight, ChatMessage
from finances.models import Transaction, Goal

MODEL_ID = 'gemini-2.0-flash'

def generate_insight_for_user(user, insight_type: str) -> Insight:
    """
    Lê transações e metas do usuário, pede ao Gemini um insight e salva no banco.
    insight_type: 'summary' | 'forecast' | 'anomaly'
    """
    # 1. Coleta dados
    txs   = list(Transaction.objects.filter(user=user).values(
                'amount', 'timestamp', 'category__name'))
    goals = list(Goal.objects.filter(user=user).values(
                'name', 'target_amount', 'start_date', 'end_date'))

    # 2. Monta prompt
    prompt = (
        f"Tipo de insight: {insight_type}\n\n"
        f"Transações:\n{json.dumps(txs, default=str)}\n\n"
        f"Metas:\n{json.dumps(goals, default=str)}\n\n"
        "Gere um JSON com chaves 'content' (string) e 'data' (objeto com valores)."
    )

    # 3. Chama Gemini
    api_key = os.getenv('GOOGLE_API_KEY')
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction="Você é um analista financeiro.",
        max_output_tokens=512,
        temperature=0.5
    )
    chat = client.chats.create(model=MODEL_ID, config=config)
    raw = chat.send_message(prompt).text

    # 4. Parseia e salva
    try:
        result = json.loads(raw)
        content = result.get('content', '')
        data    = result.get('data', {})
    except json.JSONDecodeError:
        content, data = raw, {}

    insight = Insight.objects.create(
        user=user,
        insight_type=insight_type,
        content=content,
        data=data
    )
    return insight

def chat_with_agent(user, message_text: str) -> ChatMessage:
    """
    Registra user->agent e agent->user no ChatMessage.
    """
    # 1. Salva mensagem do usuário
    user_msg = ChatMessage.objects.create(
        user=user,
        role=ChatMessage.USER,
        message=message_text,
        metadata={}
    )

    # 2. Cria e envia ao Gemini
    api_key = os.getenv('GOOGLE_API_KEY')
    client = genai.Client(api_key=api_key)
    system = "Você é um assistente financeiro."
    config = types.GenerateContentConfig(system_instruction=system)
    chat = client.chats.create(model=MODEL_ID, config=config)
    response_text = chat.send_message(message_text).text

    # 3. Salva resposta do agente
    agent_msg = ChatMessage.objects.create(
        user=user,
        role=ChatMessage.AGENT,
        message=response_text,
        metadata={}
    )
    return agent_msg
