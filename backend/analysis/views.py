from rest_framework import viewsets, permissions
from .models import Insight, ChatMessage
from .serializers import InsightSerializer, ChatMessageSerializer

class InsightViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = InsightSerializer
    
    def get_queryset(self):
        return Insight.objects.filter(user=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
