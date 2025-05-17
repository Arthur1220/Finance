from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Insight, ChatMessage
from .serializers import InsightSerializer, ChatMessageSerializer
from .services import generate_insight_for_user, chat_with_agent

class InsightViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = InsightSerializer
    
    def get_queryset(self):
        return Insight.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='generate/(?P<insight_type>[^/.]+)')
    def generate(self, request, insight_type=None):
        insight = generate_insight_for_user(request.user, insight_type)
        return Response(InsightSerializer(insight).data, status=201)

class ChatMessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='chat')
    def chat(self, request):
        text = request.data.get('message')
        agent_msg = chat_with_agent(request.user, text)
        return Response(self.get_serializer(agent_msg).data, status=201)
