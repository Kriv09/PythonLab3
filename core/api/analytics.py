import pandas as pd
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg, F

from core.models import Client, Account, Branch, Transaction, AccountType


class TopClientsByTransactionSum(APIView):
    """
    Запит 1:
    Топ клієнтів за сумою всіх відправлених транзакцій.
    (Group By + Sum + Order By DESC LIMIT 10)
    """
    def get(self, request):
        queryset = (
            Client.objects
            .annotate(total_sent=Sum('accounts__sent_transactions__amount'))
            .order_by('-total_sent')
            .values('full_name', 'total_sent')[:10]
        )
        df = pd.DataFrame(list(queryset))
        return Response(df.to_dict(orient='records'))


class AccountsByBranch(APIView):
    """
    Запит 2:
    Кількість акаунтів у кожному відділенні (Group By + Count).
    """
    def get(self, request):
        queryset = (
            Branch.objects
            .annotate(account_count=Count('account'))
            .values('branch_name', 'city', 'account_count')
        )
        df = pd.DataFrame(list(queryset))
        return Response(df.to_dict(orient='records'))


class BalanceByAccountType(APIView):
    """
    Запит 3:
    Загальна сума балансу по типах акаунтів (Group By + Sum).
    """
    def get(self, request):
        queryset = (
            AccountType.objects
            .annotate(total_balance=Sum('account__balance'))
            .values('type_name', 'total_balance')
            .order_by('-total_balance')
        )
        df = pd.DataFrame(list(queryset))
        return Response(df.to_dict(orient='records'))


class TransactionTypeStats(APIView):
    """
    Запит 4:
    Кількість транзакцій кожного типу (Group By + HAVING count > 5).
    """
    def get(self, request):
        queryset = (
            Transaction.objects
            .values(type_name=F('transaction_type__type_name'))
            .annotate(cnt=Count('id'))
            # .filter(cnt__gt=5)
            .order_by('-cnt')
        )

        df = pd.DataFrame(list(queryset))
        return Response(df.to_dict(orient='records'))


class AvgTransactionPerClient(APIView):
    """
    Запит 5:
    Середня сума транзакцій, відправлених клієнтом (Avg).
    """
    def get(self, request):
        queryset = (
            Client.objects
            .annotate(avg_amount=Avg('accounts__sent_transactions__amount'))
            .values('full_name', 'avg_amount')
            .order_by('-avg_amount')
        )
        df = pd.DataFrame(list(queryset))
        return Response(df.to_dict(orient='records'))


class RichClients(APIView):
    """
    Запит 6:
    Клієнти, у яких сумарний баланс на всіх акаунтах > 5000.
    (Group By + Sum + HAVING)
    """
    def get(self, request):
        queryset = (
            Client.objects
            .annotate(total_balance=Sum('accounts__balance'))
            .filter(total_balance__gt=5000)
            .values('full_name', 'total_balance')
            .order_by('-total_balance')
        )
        df = pd.DataFrame(list(queryset))
        return Response(df.to_dict(orient='records'))
