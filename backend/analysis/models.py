from django.db import models
from django.conf import settings

class Insight(models.Model):
    SUMMARY = 'summary'
    FORECAST = 'forecast'
    ANOMALY = 'anomaly'
    TYPE_CHOICES = [(SUMMARY,'Resumo'), (FORECAST,'Previsão'), (ANOMALY,'Anomalia')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    insight_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.TextField()
    data = models.JSONField(default=dict)  # detalhes estruturados

class ChatMessage(models.Model):
    USER = 'user'
    AGENT = 'agent'
    ROLE_CHOICES = [(USER,'Usuário'), (AGENT,'Agente')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES)
    message = models.TextField()
    metadata = models.JSONField(default=dict)