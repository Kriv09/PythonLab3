from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views import (
    ClientViewSet, AccountTypeViewSet, BranchViewSet, AccountViewSet,
    TransactionTypeViewSet, TransactionViewSet, ReportView
)
from core import views

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'account-types', AccountTypeViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transaction-types', TransactionTypeViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # REST API
    path('api/', include(router.urls)),
    path('api/report/', ReportView.as_view(), name='report'),

    # Clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Account Types
    path('account-types/', views.AccountTypeListView.as_view(), name='accounttype_list'),
    path('account-types/add/', views.AccountTypeCreateView.as_view(), name='accounttype_add'),
    path('account-types/<int:pk>/', views.AccountTypeDetailView.as_view(), name='accounttype_detail'),
    path('account-types/<int:pk>/edit/', views.AccountTypeUpdateView.as_view(), name='accounttype_edit'),
    path('account-types/<int:pk>/delete/', views.AccountTypeDeleteView.as_view(), name='accounttype_delete'),

    # Branches
    path('branches/', views.BranchListView.as_view(), name='branch_list'),
    path('branches/add/', views.BranchCreateView.as_view(), name='branch_add'),
    path('branches/<int:pk>/', views.BranchDetailView.as_view(), name='branch_detail'),
    path('branches/<int:pk>/edit/', views.BranchUpdateView.as_view(), name='branch_edit'),
    path('branches/<int:pk>/delete/', views.BranchDeleteView.as_view(), name='branch_delete'),

    # Accounts
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/add/', views.AccountCreateView.as_view(), name='account_add'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_edit'),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),

    # Transaction Types
    path('transaction-types/', views.TransactionTypeListView.as_view(), name='transactiontype_list'),
    path('transaction-types/add/', views.TransactionTypeCreateView.as_view(), name='transactiontype_add'),
    path('transaction-types/<int:pk>/', views.TransactionTypeDetailView.as_view(), name='transactiontype_detail'),
    path('transaction-types/<int:pk>/edit/', views.TransactionTypeUpdateView.as_view(), name='transactiontype_edit'),
    path('transaction-types/<int:pk>/delete/', views.TransactionTypeDeleteView.as_view(), name='transactiontype_delete'),

    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction_add'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),


    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

]

