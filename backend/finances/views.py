from rest_framework import viewsets, permissions
from django.http import StreamingHttpResponse
from rest_framework.decorators import action
from .models import Category, Transaction, Goal
from .serializers import CategorySerializer, TransactionSerializer, GoalSerializer
from .services import parse_transaction_text, parse_goal_text, generate_transactions_csv, generate_30day_report, generate_transactions_pdf
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse


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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_csv(self, request):
        """
        GET /finances/transactions/export_csv/
        Retorna todas as transações do usuário em CSV.
        """
        buffer = generate_transactions_csv(request.user)
        resp = StreamingHttpResponse(
            buffer,
            content_type='text/csv'
        )
        resp['Content-Disposition'] = (
            f'attachment; filename="transactions_{request.user.id}.csv"'
        )
        return resp
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_pdf(self, request):
        """
        GET /finances/transactions/export_pdf/
        Retorna um PDF com tabela de transações.
        """
        buffer = generate_transactions_pdf(request.user)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"transactions_{request.user.id}.pdf",
            content_type='application/pdf'
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def report_30days(self, request):
        """
        GET /finances/transactions/report_30days/
        Retorna JSON com resumo do mês passado.
        """
        data = generate_30day_report(request.user)
        return Response(data)

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