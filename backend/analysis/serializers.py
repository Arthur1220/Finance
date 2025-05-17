from rest_framework import serializers
from .models import Insight, ChatMessage

class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'role',
            'message',
            'metadata',
            'timestamp',
        ]
        read_only_fields = [
            'id',
            'timestamp',
        ]