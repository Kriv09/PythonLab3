from rest_framework import serializers
from core.models import Client, AccountType, Branch, Account, TransactionType, Transaction

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'full_name', 'email', 'phone', 'created_at']

class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ['id', 'type_name', 'description']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'branch_name', 'city', 'country']

class AccountSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    account_type = serializers.PrimaryKeyRelatedField(queryset=AccountType.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Account
        fields = ['id', 'client', 'account_type', 'branch', 'balance', 'created_at']

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ['id', 'type_name']

class TransactionSerializer(serializers.ModelSerializer):
    sender_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    receiver_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), allow_null=True, required=False)
    transaction_type = serializers.PrimaryKeyRelatedField(queryset=TransactionType.objects.all())

    class Meta:
        model = Transaction
        fields = ['id', 'sender_account', 'receiver_account', 'transaction_type', 'amount', 'timestamp', 'description']
        read_only_fields = ['timestamp']