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



from django.shortcuts import render
from django.views import View
from core.api.analytics import (
    TopClientsByTransactionSum, AccountsByBranch, BalanceByAccountType,
    TransactionTypeStats, AvgTransactionPerClient, RichClients
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from core.models import Client

class AnalyticsDashBoardView(View):
    def get(self, request):
        print("="*80)
        print("STARTING ANALYTICS DASHBOARD")
        print("="*80)

        # --- Отримуємо дані з API ---
        top_clients = TopClientsByTransactionSum().get(request).data
        accounts_by_branch = AccountsByBranch().get(request).data
        balance_by_type = BalanceByAccountType().get(request).data
        transaction_stats = TransactionTypeStats().get(request).data
        avg_transaction = AvgTransactionPerClient().get(request).data
        rich_clients = RichClients().get(request).data

        print(f"Top clients data: {len(top_clients)} records")
        print(f"First top client: {top_clients[0] if top_clients else 'NONE'}")

        # --- Конвертуємо в pandas DataFrame ---
        df_top_clients = pd.DataFrame(top_clients)
        df_accounts_by_branch = pd.DataFrame(accounts_by_branch)
        df_balance_by_type = pd.DataFrame(balance_by_type)
        df_transaction_stats = pd.DataFrame(transaction_stats)
        df_avg_transaction = pd.DataFrame(avg_transaction)
        df_rich_clients = pd.DataFrame(rich_clients)

        # --- Функція для безпечного створення графіка ---
        first_plot = True

        def safe_plot(df, chart_type, **kwargs):
            nonlocal first_plot

            if df.empty:
                return "<div style='padding: 20px; text-align: center; color: #999;'>No data available</div>"

            try:
                if chart_type == "bar":
                    fig = px.bar(df, **kwargs)
                elif chart_type == "pie":
                    fig = px.pie(df, **kwargs)
                elif chart_type == "line":
                    fig = px.line(df, **kwargs)
                else:
                    return "<div style='padding: 20px; text-align: center; color: red;'>Invalid chart type</div>"

                # Налаштування графіка
                fig.update_layout(
                    height=400,
                    margin=dict(l=50, r=50, t=50, b=50),
                    paper_bgcolor='white',
                    plot_bgcolor='rgba(240,240,240,0.5)'
                )

                # ВАЖЛИВО: Перший графік включає plotly.js, решта - ні
                if first_plot:
                    result = plot(fig, output_type='div', include_plotlyjs='cdn')
                    first_plot = False
                else:
                    result = plot(fig, output_type='div', include_plotlyjs=False)

                return result
            except Exception as e:
                print(f"❌ Error creating {chart_type} chart: {e}")
                import traceback
                traceback.print_exc()
                return f"<div style='padding: 20px; text-align: center; color: red;'>Error creating chart: {e}</div>"

        # --- Основні графіки ---
        fig1 = safe_plot(df_top_clients, "bar", x='full_name', y='total_sent', title='Top Clients')
        fig2 = safe_plot(df_accounts_by_branch, "pie", values='account_count', names='branch_name', title='Accounts by Branch')
        fig3 = safe_plot(df_balance_by_type, "bar", x='type_name', y='total_balance', title='Balance by Account Type')
        fig4 = safe_plot(df_transaction_stats, "line", x='type_name', y='cnt', title='Transaction Type Stats')
        fig5 = safe_plot(df_avg_transaction, "bar", x='full_name', y='avg_amount', title='Avg Transaction per Client')
        fig6 = safe_plot(df_rich_clients, "bar", x='full_name', y='total_balance', title='Rich Clients')

        print("\n" + "="*80)
        print("STARTING PARALLEL DB TEST")
        print("="*80)

        # --- Паралельні запити до БД ---
        def run_test(client_id):
            """Виконання тестового запиту для одного клієнта"""
            start = time.time()
            try:
                client = Client.objects.get(pk=client_id)
                _ = list(client.accounts.all())
                for acc in client.accounts.all():
                    _ = list(acc.sent_transactions.all())
                elapsed = time.time() - start
                return elapsed
            except Client.DoesNotExist:
                print(f"⚠️  Client with id {client_id} does not exist")
                return time.time() - start
            except Exception as e:
                print(f"❌ Error processing client {client_id}: {e}")
                return time.time() - start

        thread_counts = [1, 2, 4, 8]
        results = []

        # Отримуємо реальні ID клієнтів з БД
        all_client_ids = list(Client.objects.values_list('id', flat=True))
        print(f"\n📊 Total clients in DB: {len(all_client_ids)}")

        # Беремо перших 20 або всі якщо менше
        client_ids = all_client_ids[:20]
        print(f"📊 Using {len(client_ids)} clients for test")
        print(f"📊 Client IDs: {client_ids[:5]}..." if len(client_ids) > 5 else f"📊 Client IDs: {client_ids}")

        if client_ids:
            for threads in thread_counts:
                print(f"\n🔄 Testing with {threads} thread(s)...")
                start_batch = time.time()

                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = [executor.submit(run_test, cid) for cid in client_ids]
                    times = []

                    for i, future in enumerate(as_completed(futures)):
                        result_time = future.result()
                        times.append(result_time)
                        if i < 3:  # Показуємо перші 3 результати
                            print(f"  Task {i+1} completed in {result_time:.4f}s")

                    avg_time = sum(times) / len(times) if times else 0
                    batch_time = time.time() - start_batch

                    print(f"✅ Threads: {threads} | Avg time: {avg_time:.4f}s | Total batch time: {batch_time:.4f}s")

                    results.append({
                        "threads": threads,
                        "avg_time": avg_time
                    })
        else:
            print("❌ No clients found in database for parallel test")

        print(f"\n📈 Results collected: {len(results)}")
        print(f"Results data: {results}")

        # Створюємо DataFrame та графік
        if results:
            df_parallel = pd.DataFrame(results)
            print(f"\n📊 Parallel DataFrame shape: {df_parallel.shape}")
            print(f"Parallel DataFrame:\n{df_parallel}")

            # Перевіряємо чи є дані для графіка
            if not df_parallel.empty and 'threads' in df_parallel.columns and 'avg_time' in df_parallel.columns:
                print("✅ Creating parallel performance chart...")

                try:
                    # Створюємо графік напряму через graph_objects для більшого контролю
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_parallel['threads'],
                        y=df_parallel['avg_time'],
                        mode='lines+markers',
                        name='Average Time',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=10)
                    ))

                    fig.update_layout(
                        title='Parallel DB Query Performance',
                        xaxis_title='Number of Threads',
                        yaxis_title='Average Time (seconds)',
                        height=400,
                        margin=dict(l=50, r=50, t=50, b=50),
                        paper_bgcolor='white',
                        plot_bgcolor='rgba(240,240,240,0.5)',
                        showlegend=True,
                        xaxis=dict(
                            tickmode='array',
                            tickvals=df_parallel['threads'].tolist()
                        )
                    )

                    fig_parallel = plot(fig, output_type='div', include_plotlyjs=False)
                    print("✅ Chart created successfully")
                except Exception as e:
                    print(f"❌ Error creating parallel chart: {e}")
                    import traceback
                    traceback.print_exc()
                    fig_parallel = f"<div style='padding: 20px; text-align: center; color: red;'>Error: {e}</div>"
            else:
                print("❌ DataFrame is empty or missing required columns")
                fig_parallel = "<div style='padding: 20px; text-align: center; color: red;'>Error: DataFrame is empty or invalid</div>"
        else:
            print("❌ No results collected")
            fig_parallel = "<div style='padding: 20px; text-align: center; color: #999;'>No data available for parallel test. Please add clients to the database.</div>"

        print("\n" + "="*80)
        print("DASHBOARD COMPLETE")
        print("="*80 + "\n")

        # --- Передаємо графіки в шаблон ---
        context = {
            'fig1': fig1,
            'fig2': fig2,
            'fig3': fig3,
            'fig4': fig4,
            'fig5': fig5,
            'fig6': fig6,
            'fig_parallel': fig_parallel,
            'debug_info': {
                'client_count': len(client_ids) if client_ids else 0,
                'results_count': len(results),
                'has_data': bool(results),
            }
        }

        return render(request, 'dashboard.html', context)

from rest_framework.views import APIView
from rest_framework.response import Response
from core.utils.db_parallel import run_parallel_test
from core.models import Client

class DBParallelTestView(APIView):

    def get(self, request):
        client_ids = list(Client.objects.values_list('id', flat=True))
        max_workers_list = [1, 5, 10, 20]
        results_summary = []

        for workers in max_workers_list:
            results, exec_time = run_parallel_test(client_ids, max_workers=workers, use_threads=True)
            results_summary.append({'workers': workers, 'time': exec_time, 'results_count': len(results)})

        return Response(results_summary)
