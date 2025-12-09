
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from core.models import Client, AccountType, Branch, Account, TransactionType, Transaction
import random
from decimal import Decimal
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Populate database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clients',
            type=int,
            default=10000,
            help='Number of clients to create (default: 10000)'
        )
        parser.add_argument(
            '--accounts',
            type=int,
            default=10000,
            help='Number of accounts to create (default: 10000)'
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=10000,
            help='Number of transactions to create (default: 10000)'
        )
        parser.add_argument(
            '--branches',
            type=int,
            default=100,
            help='Number of branches to create (default: 100)'
        )
        parser.add_argument(
            '--no-reset',
            action='store_true',
            help='Do not reset database before populating'
        )

    def handle(self, *args, **options):
        start_time = datetime.now()

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('DATABASE POPULATION'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        if not options['no_reset']:
            self.reset_database()

        with transaction.atomic():
            self.generate_account_types()
            self.generate_transaction_types()
            self.generate_branches(options['branches'])
            self.generate_clients(options['clients'])
            self.generate_accounts(options['accounts'])
            self.generate_transactions(options['transactions'])

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.print_summary(duration)

    def reset_database(self):
        """Очищає всі таблиці та скидає послідовності"""
        self.stdout.write(self.style.WARNING('\n🔄 Resetting database...'))

        with connection.cursor() as cursor:
            tables = [
                'core_transaction',
                'core_account',
                'core_client',
                'core_accounttype',
                'core_branch',
                'core_transactiontype'
            ]

            cursor.execute('SET CONSTRAINTS ALL DEFERRED;')

            for table in tables:
                cursor.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;')

        self.stdout.write(self.style.SUCCESS('✅ Database reset complete!\n'))

    def generate_clients(self, count):
        """Генерує клієнтів"""
        self.stdout.write(f'📝 Generating {count} clients...')

        first_names = ['John', 'Jane', 'Mike', 'Emily', 'David', 'Sarah', 'Chris', 'Anna',
                       'Tom', 'Lisa', 'Alex', 'Maria', 'Peter', 'Laura', 'James', 'Emma',
                       'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                      'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
                      'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']

        clients = []
        for i in range(1, count + 1):
            first = random.choice(first_names)
            last = random.choice(last_names)
            clients.append(Client(
                full_name=f"{first} {last} {i}",
                email=f"client{i}@bank.com",
                phone=f"+1{random.randint(2000000000, 9999999999)}",
            ))

            if i % 2000 == 0:
                self.stdout.write(f'  Progress: {i}/{count}')

        Client.objects.bulk_create(clients, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {count} clients\n'))

    def generate_account_types(self):
        """Генерує типи акаунтів"""
        self.stdout.write('📝 Generating account types...')

        types = [
            ('Checking', 'Standard checking account'),
            ('Savings', 'High-interest savings account'),
            ('Business', 'Business checking account'),
            ('Premium', 'Premium account with benefits'),
            ('Student', 'Student account with low fees'),
            ('Investment', 'Investment account'),
            ('Retirement', 'Retirement savings account'),
        ]

        account_types = [
            AccountType(type_name=name, description=desc)
            for name, desc in types
        ]

        AccountType.objects.bulk_create(account_types)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(types)} account types\n'))

    def generate_branches(self, count):
        """Генерує відділення"""
        self.stdout.write(f'📝 Generating {count} branches...')

        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
                  'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
                  'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'San Francisco',
                  'Charlotte', 'Indianapolis', 'Seattle', 'Denver', 'Washington',
                  'Boston', 'Nashville', 'El Paso', 'Detroit', 'Memphis']

        branches = []
        for i in range(1, count + 1):
            city = random.choice(cities)
            branches.append(Branch(
                branch_name=f"{city} Branch {i}",
                city=city,
                country='USA'
            ))

        Branch.objects.bulk_create(branches, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {count} branches\n'))

    def generate_transaction_types(self):
        """Генерує типи транзакцій"""
        self.stdout.write('📝 Generating transaction types...')

        types = ['Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Fee',
                 'Refund', 'Interest', 'Cashback']

        transaction_types = [TransactionType(type_name=name) for name in types]
        TransactionType.objects.bulk_create(transaction_types)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(types)} transaction types\n'))

    def generate_accounts(self, count):
        """Генерує акаунти"""
        self.stdout.write(f'📝 Generating {count} accounts...')

        client_ids = list(Client.objects.values_list('id', flat=True))
        account_type_ids = list(AccountType.objects.values_list('id', flat=True))
        branch_ids = list(Branch.objects.values_list('id', flat=True))

        accounts = []
        for i in range(count):
            accounts.append(Account(
                client_id=random.choice(client_ids),
                account_type_id=random.choice(account_type_ids),
                branch_id=random.choice(branch_ids),
                balance=Decimal(random.uniform(100, 50000)).quantize(Decimal('0.01'))
            ))

            if (i + 1) % 2000 == 0:
                self.stdout.write(f'  Progress: {i + 1}/{count}')

        Account.objects.bulk_create(accounts, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {count} accounts\n'))

    def generate_transactions(self, count):
        """Генерує транзакції"""
        self.stdout.write(f'📝 Generating {count} transactions...')

        account_ids = list(Account.objects.values_list('id', flat=True))
        transaction_type_ids = list(TransactionType.objects.values_list('id', flat=True))

        transactions = []
        base_date = datetime.now() - timedelta(days=365)

        for i in range(count):
            sender_id = random.choice(account_ids)
            receiver_id = random.choice(account_ids) if random.random() > 0.2 else None

            if receiver_id == sender_id:
                receiver_id = None

            transactions.append(Transaction(
                sender_account_id=sender_id,
                receiver_account_id=receiver_id,
                transaction_type_id=random.choice(transaction_type_ids),
                amount=Decimal(random.uniform(10, 5000)).quantize(Decimal('0.01')),
                description=f"Transaction {i + 1}",
                timestamp=base_date + timedelta(
                    days=random.randint(0, 365),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            ))

            if (i + 1) % 2000 == 0:
                self.stdout.write(f'  Progress: {i + 1}/{count}')

        Transaction.objects.bulk_create(transactions, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {count} transactions\n'))

    def print_summary(self, duration):
        """Виводить підсумок"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('DATABASE POPULATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(f'  • Clients: {Client.objects.count()}')
        self.stdout.write(f'  • Account Types: {AccountType.objects.count()}')
        self.stdout.write(f'  • Branches: {Branch.objects.count()}')
        self.stdout.write(f'  • Transaction Types: {TransactionType.objects.count()}')
        self.stdout.write(f'  • Accounts: {Account.objects.count()}')
        self.stdout.write(f'  • Transactions: {Transaction.objects.count()}')
        self.stdout.write(self.style.SUCCESS(f'\n⏱️  Total time: {duration:.2f} seconds'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))