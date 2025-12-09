import time
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

from core import models
from core.models import Client, Account

def fetch_client_total_balance(client_id):
    """
    Функція для виконання запиту до БД.
    Наприклад, підрахунок сумарного балансу клієнта.
    """
    try:
        client = Client.objects.get(pk=client_id)
        total_balance = client.accounts.aggregate(total_balance_sum=models.Sum('balance'))['total_balance_sum'] or 0
        return client_id, total_balance
    except Client.DoesNotExist:
        return client_id, None

def run_parallel_test(client_ids, max_workers=5, use_threads=True):
    """
    Виконання паралельних запитів до БД.
    - client_ids: список ID клієнтів
    - max_workers: кількість потоків або процесів
    - use_threads: True для потоків, False для процесів
    Повертає список результатів та час виконання.
    """
    start_time = time.time()
    results = []

    Executor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor
    with Executor(max_workers=max_workers) as executor:
        future_to_client = {executor.submit(fetch_client_total_balance, cid): cid for cid in client_ids}
        for future in as_completed(future_to_client):
            results.append(future.result())

    total_time = time.time() - start_time
    return results, total_time
