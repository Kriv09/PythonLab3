"""
URL configuration for bank_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from core.api.views import ClientViewSet, AccountTypeViewSet, BranchViewSet, AccountViewSet, TransactionTypeViewSet, \
    TransactionViewSet, ReportView

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'account-types', AccountTypeViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transaction-types', TransactionTypeViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/report/', ReportView.as_view(), name='report'),
]
