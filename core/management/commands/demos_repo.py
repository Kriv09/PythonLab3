from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
from core.repos.manager import RepositoryManager
from core.models import AccountType, Branch, TransactionType


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = RepositoryManager()

        at, _ = AccountType.objects.get_or_create(type_name='Checking', defaults={'description': 'Standard checking'})
        br, _ = Branch.objects.get_or_create(branch_name='Main Branch', city='Kyiv', country='Ukraine')
        tt, _ = TransactionType.objects.get_or_create(type_name='Transfer')

        c1 = r.clients.create(full_name='Client 1', email='exampledemo@example.com', phone='111111')
        c2 = r.clients.create(full_name='Client 2', email='demo2@example.com', phone='222222')
        a1 = r.accounts.create(client=c1, account_type=at, branch=br, balance=3000)
        a2 = r.accounts.create(client=c2, account_type=at, branch=br, balance=1000)

        self.stdout.write(self.style.SUCCESS(f'Clients: {c1.pk}, {c2.pk}'))
        self.stdout.write(self.style.SUCCESS(f'Accounts: {a1.pk}, {a2.pk}'))

        for c in r.clients.get_all():
            self.stdout.write(f'{c.pk}: {c.full_name}')

        c = r.clients.get_by_id(c1.pk)
        self.stdout.write(f'By ID: {c.pk} {c.full_name}')

        r.clients.update(c1.pk, phone='999999')

        with db_transaction.atomic():
            amt = 500
            if a1.balance >= amt:
                a1.balance -= amt
                a2.balance += amt
                a1.save(); a2.save()
                t = r.transactions.create(
                    sender_account=a1,
                    receiver_account=a2,
                    transaction_type=tt,
                    amount=amt,
                    description='Transfer demo'
                )
                self.stdout.write(self.style.SUCCESS(f'Transaction {t.pk}: {amt}'))
            else:
                self.stdout.write(self.style.ERROR('Insufficient balance'))

        for t in r.transactions.get_all():
            self.stdout.write(f'{t.pk}: {t.amount} {t.sender_account_id}->{t.receiver_account_id}')

        a1 = r.accounts.get_by_id(a1.pk)
        a2 = r.accounts.get_by_id(a2.pk)
        self.stdout.write(f'Balances: a1={a1.balance}, a2={a2.balance}')
