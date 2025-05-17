from rest_framework import viewsets, permissions
from .models import Category, Transaction, Goal
from .serializers import CategorySerializer, TransactionSerializer, GoalSerializer
from .services import parse_transaction_text, parse_goal_text

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        raw = serializer.validated_data.get('raw_text')
        parsed = parse_transaction_text(raw)

        # Trata categoria (cria se não existir)
        cat_name = parsed.get('category') or 'Outros'
        cat_type = parsed.get('type') or Category.EXPENSE
        category, _ = Category.objects.get_or_create(
            user=self.request.user,
            name=cat_name,
            type=cat_type
        )

        # Salva a transação com os dados parseados
        serializer.save(
            user=self.request.user,
            category=category,
            amount=parsed.get('amount') or serializer.validated_data['amount'],
            metadata=parsed
        )

class GoalViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = GoalSerializer
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        raw = serializer.validated_data.get('name')  # ou outro campo que você use para descrever
        parsed = parse_goal_text(raw)

        # Salva a Goal usando os campos parseados
        serializer.save(
            user=self.request.user,
            target_amount=parsed.get('target_amount') or serializer.validated_data['target_amount'],
            start_date=parsed.get('start_date') or serializer.validated_data['start_date'],
            end_date=parsed.get('end_date')     or serializer.validated_data['end_date'],
            frequency=parsed.get('frequency')   or serializer.validated_data['frequency'],
            name=parsed.get('name')             or serializer.validated_data['name'],
            metadata=parsed
        )