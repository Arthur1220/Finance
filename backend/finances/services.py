import os, json
from google import genai
from google.genai import types
import csv
from io import StringIO
from .models import Transaction
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

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
    
def generate_transactions_csv(user):
    """
    Retorna um buffer CSV com todas as transações do usuário.
    """
    qs = Transaction.objects.filter(user=user).order_by('-timestamp')
    buffer = StringIO()
    writer = csv.writer(buffer)
    # Cabeçalho
    writer.writerow(['ID','Data','Categoria','Valor','Tipo','Local','Descrição'])
    # Linhas
    for t in qs:
        writer.writerow([
            t.id,
            t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            t.category.name if t.category else '',
            f"{t.amount:.2f}",
            t.metadata.get('type',''),
            t.metadata.get('location',''),
            t.raw_text
        ])
    buffer.seek(0)
    return buffer

def generate_30day_report(user):
    """
    Retorna um dict com totais de receitas, despesas e por categoria nos últimos 30 dias.
    """
    now = timezone.now()
    since = now - timedelta(days=30)
    qs = Transaction.objects.filter(user=user, timestamp__gte=since)

    total_expense = qs.filter(metadata__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_income  = qs.filter(metadata__type='income').aggregate(Sum('amount'))['amount__sum'] or 0

    by_category = (
        qs
        .values('category__name')
        .annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        .order_by('-total')
    )

    return {
        'period_start': since.date().isoformat(),
        'period_end': now.date().isoformat(),
        'total_expense': float(total_expense),
        'total_income': float(total_income),
        'by_category': [
            {
                'category': entry['category__name'],
                'total': float(entry['total']),
                'count': entry['count']
            }
            for entry in by_category
        ]
    }


def generate_transactions_pdf(user):
    """
    Gera um PDF com uma tabela das transações do usuário.
    """
    qs = Transaction.objects.filter(user=user).order_by('-timestamp')
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    data = [['Data','Categoria','Valor','Tipo','Local','Descrição']]
    for t in qs:
        data.append([
            t.timestamp.strftime('%Y-%m-%d'),
            t.category.name if t.category else '',
            f"{t.amount:.2f}",
            t.metadata.get('type',''),
            t.metadata.get('location',''),
            t.raw_text[:30] + ('...' if len(t.raw_text)>30 else '')
        ])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    doc.build([table])
    buffer.seek(0)
    return buffer