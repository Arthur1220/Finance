from rest_framework import serializers
from .models import Category, Transaction, Goal

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','type']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id','category','amount','timestamp','raw_text','metadata']

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id','name','target_amount','start_date','end_date','frequency','metadata']
