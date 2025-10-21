from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from core.models import Client, AccountType, Branch, Account, TransactionType, Transaction
from .serializers import (
    ClientSerializer, AccountTypeSerializer, BranchSerializer, AccountSerializer,
    TransactionTypeSerializer, TransactionSerializer
)
from core.repos.manager import RepositoryManager
from django.db.models import Sum, Count

r = RepositoryManager()

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

class AccountTypeViewSet(viewsets.ModelViewSet):
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    permission_classes = [IsAuthenticated]

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related('client','account_type','branch').all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

class TransactionTypeViewSet(viewsets.ModelViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer
    permission_classes = [IsAuthenticated]

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('sender_account','receiver_account','transaction_type').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='transfer')
    def transfer(self, request):
        data = request.data
        with transaction.atomic():
            sender = Account.objects.select_for_update().get(pk=data['sender_account'])
            receiver = Account.objects.select_for_update().get(pk=data['receiver_account'])
            amount = float(data['amount'])
            if sender.balance < amount:
                return Response({'detail': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            sender.balance -= amount
            receiver.balance += amount
            sender.save(); receiver.save()
            t = Transaction.objects.create(
                sender_account=sender,
                receiver_account=receiver,
                transaction_type_id=data['transaction_type'],
                amount=amount,
                description=data.get('description', '')
            )
        return Response(TransactionSerializer(t).data, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView

class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_clients = Client.objects.count()
        total_accounts = Account.objects.count()
        total_balance = Account.objects.aggregate(total=Sum('balance'))['total'] or 0
        total_transactions = Transaction.objects.count()
        sum_transactions = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0


        branch_summary = Account.objects.values('branch__branch_name').annotate(
            accounts=Count('id'),
            total_balance=Sum('balance')
        )

        report = {
            "total_clients": total_clients,
            "total_accounts": total_accounts,
            "total_balance": str(total_balance),
            "total_transactions": total_transactions,
            "sum_transactions": str(sum_transactions),
            "by_branch": list(branch_summary)
        }
        return Response(report)