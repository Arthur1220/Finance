from rest_framework import serializers
from .models import Category, Transaction, Goal

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','type']

class TransactionSerializer(serializers.ModelSerializer):
    metadata = serializers.JSONField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id','raw_text','amount','timestamp','category','metadata']
        read_only_fields = ['id','timestamp','category','metadata']

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id','name','target_amount','start_date','end_date','frequency','metadata']
        read_only_fields = ['id','metadata']
