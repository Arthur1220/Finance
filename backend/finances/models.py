from django.db import models
from django.conf import settings

class Category(models.Model):
    EXPENSE = 'expense'
    INCOME = 'income'
    TYPE_CHOICES = [(EXPENSE, 'Despesa'), (INCOME, 'Receita')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ('user','name','type')

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    raw_text = models.TextField()
    metadata = models.JSONField(default=dict)  # {amount:, date:, location:, type:}

class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    FREQUENCY_CHOICES = [
        ('one-time','Única'),
        ('monthly','Mensal'),
        ('yearly','Anual'),
    ]
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    metadata = models.JSONField(default=dict)
