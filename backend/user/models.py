from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True, default='America/Sao_Paulo')
    currency = models.CharField(max_length=3, blank=True, null=True, default='BRL')

    history = HistoricalRecords()

    def __str__(self):
        return self.username