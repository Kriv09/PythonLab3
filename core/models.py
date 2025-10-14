from django.db import models

class Client(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class AccountType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.type_name

class Branch(models.Model):
    branch_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.branch_name

class Account(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Account {self.pk} ({self.client})'

class TransactionType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type_name

class Transaction(models.Model):
    sender_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='sent_transactions')
    receiver_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='received_transactions', null=True, blank=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Transaction {self.pk} - {self.amount}'
