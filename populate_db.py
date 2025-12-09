import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_project.settings')
django.setup()

from django.db import connection, transaction
from core.models import Client, AccountType, Branch, Account, TransactionType, Transaction

def reset_database():
    """Очищає всі таблиці та скидає послідовності"""
    print("="*80)
    print("RESETTING DATABASE")
    print("="*80)

    with connection.cursor() as cursor:
        # Отримуємо список всіх таблиць
        tables = [
            'core_transaction',
            'core_account',
            'core_client',
            'core_accounttype',
            'core_branch',
            'core_transactiontype'
        ]

        # Вимикаємо перевірку foreign keys
        cursor.execute('SET CONSTRAINTS ALL DEFERRED;')

        # Видаляємо всі дані
        for table in tables:
            print(f"Truncating {table}...")
            cursor.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;')

        print("✅ Database reset complete!\n")

def generate_clients(count=10000):
    """Генерує клієнтів"""
    print(f"Generating {count} clients...")

    first_names = ['John', 'Jane', 'Mike', 'Emily', 'David', 'Sarah', 'Chris', 'Anna',
                   'Tom', 'Lisa', 'Alex', 'Maria', 'Peter', 'Laura', 'James', 'Emma']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson']

    clients = []
    for i in range(1, count + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)
        clients.append(Client(
            full_name=f"{first} {last} {i}",
            email=f"client{i}@bank.com",
            phone=f"+1{random.randint(2000000000, 9999999999)}",
        ))

        if i % 1000 == 0:
            print(f"  Generated {i} clients...")

    Client.objects.bulk_create(clients, batch_size=1000)
    print(f"✅ Created {count} clients\n")

def generate_account_types():
    """Генерує типи акаунтів"""
    print("Generating account types...")

    types = [
        ('Checking', 'Standard checking account'),
        ('Savings', 'High-interest savings account'),
        ('Business', 'Business checking account'),
        ('Premium', 'Premium account with benefits'),
        ('Student', 'Student account with low fees'),
    ]

    account_types = [
        AccountType(type_name=name, description=desc)
        for name, desc in types
    ]

    AccountType.objects.bulk_create(account_types)
    print(f"✅ Created {len(types)} account types\n")

def generate_branches(count=100):
    """Генерує відділення"""
    print(f"Generating {count} branches...")

    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
              'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
              'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'San Francisco',
              'Charlotte', 'Indianapolis', 'Seattle', 'Denver', 'Washington']

    branches = []
    for i in range(1, count + 1):
        city = random.choice(cities)
        branches.append(Branch(
            branch_name=f"{city} Branch {i}",
            city=city,
            country='USA'
        ))

    Branch.objects.bulk_create(branches, batch_size=1000)
    print(f"✅ Created {count} branches\n")

def generate_transaction_types():
    """Генерує типи транзакцій"""
    print("Generating transaction types...")

    types = ['Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Fee']

    transaction_types = [TransactionType(type_name=name) for name in types]
    TransactionType.objects.bulk_create(transaction_types)
    print(f"✅ Created {len(types)} transaction types\n")

def generate_accounts(count=10000):
    """Генерує акаунти"""
    print(f"Generating {count} accounts...")

    # Отримуємо всі ID
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

        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1} accounts...")

    Account.objects.bulk_create(accounts, batch_size=1000)
    print(f"✅ Created {count} accounts\n")

def generate_transactions(count=10000):
    """Генерує транзакції"""
    print(f"Generating {count} transactions...")

    # Отримуємо всі ID
    account_ids = list(Account.objects.values_list('id', flat=True))
    transaction_type_ids = list(TransactionType.objects.values_list('id', flat=True))

    transactions = []
    base_date = datetime.now() - timedelta(days=365)

    for i in range(count):
        sender_id = random.choice(account_ids)
        # 80% шанс що є receiver, 20% що None (withdraw/deposit)
        receiver_id = random.choice(account_ids) if random.random() > 0.2 else None

        # Переконуємось що sender != receiver
        if receiver_id == sender_id:
            receiver_id = None

        transactions.append(Transaction(
            sender_account_id=sender_id,
            receiver_account_id=receiver_id,
            transaction_type_id=random.choice(transaction_type_ids),
            amount=Decimal(random.uniform(10, 5000)).quantize(Decimal('0.01')),
            description=f"Transaction {i + 1}",
            # Випадкова дата за останній рік
            timestamp=base_date + timedelta(days=random.randint(0, 365))
        ))

        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1} transactions...")

    Transaction.objects.bulk_create(transactions, batch_size=1000)
    print(f"✅ Created {count} transactions\n")

@transaction.atomic
def populate_database():
    """Основна функція для заповнення БД"""
    print("\n" + "="*80)
    print("STARTING DATABASE POPULATION")
    print("="*80 + "\n")

    start_time = datetime.now()

    # 1. Скидаємо базу
    reset_database()

    # 2. Створюємо довідкові таблиці (малі)
    generate_account_types()
    generate_transaction_types()
    generate_branches(count=100)

    # 3. Створюємо клієнтів
    generate_clients(count=10000)

    # 4. Створюємо акаунти
    generate_accounts(count=10000)

    # 5. Створюємо транзакції
    generate_transactions(count=10000)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*80)
    print("DATABASE POPULATION COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"  • Clients: {Client.objects.count()}")
    print(f"  • Account Types: {AccountType.objects.count()}")
    print(f"  • Branches: {Branch.objects.count()}")
    print(f"  • Transaction Types: {TransactionType.objects.count()}")
    print(f"  • Accounts: {Account.objects.count()}")
    print(f"  • Transactions: {Transaction.objects.count()}")
    print(f"\n⏱️  Total time: {duration:.2f} seconds")
    print("="*80 + "\n")

if __name__ == '__main__':
    try:
        populate_database()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()