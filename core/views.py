from django.views import generic, View
from django.urls import reverse_lazy
from django.shortcuts import render
from django.db.models import ProtectedError

from .management.commands.NetworkHelper import NetworkHelper
from .models import Client, AccountType, Branch, Account, TransactionType, Transaction

class SafeDeleteView(generic.DeleteView):
    protected_related_name = None  # Optional, for error message

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            return render(request, "core/pages/error.html", {
                "message": f"Cannot delete '{self.object}' because it is used by other objects.",
                "back_url": self.get_success_url()
            })

# --- CLIENTS ---
class ClientListView(generic.ListView):
    model = Client
    template_name = "core/pages/client_list.html"

class ClientDetailView(generic.DetailView):
    model = Client
    template_name = "core/pages/client_detail.html"

class ClientCreateView(generic.CreateView):
    model = Client
    fields = ["full_name", "email", "phone"]
    template_name = "core/pages/client_form.html"
    success_url = reverse_lazy("client_list")

class ClientUpdateView(ClientCreateView, generic.UpdateView):
    pass

class ClientDeleteView(SafeDeleteView):
    model = Client
    template_name = "core/pages/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")


# --- ACCOUNT TYPES ---
class AccountTypeListView(generic.ListView):
    model = AccountType
    template_name = "core/pages/accounttype_list.html"

class AccountTypeDetailView(generic.DetailView):
    model = AccountType
    template_name = "core/pages/accounttype_detail.html"

class AccountTypeCreateView(generic.CreateView):
    model = AccountType
    fields = ["type_name", "description"]
    template_name = "core/pages/accounttype_form.html"
    success_url = reverse_lazy("accounttype_list")

class AccountTypeUpdateView(AccountTypeCreateView, generic.UpdateView):
    pass

class AccountTypeDeleteView(SafeDeleteView):
    model = AccountType
    template_name = "core/pages/accounttype_confirm_delete.html"
    success_url = reverse_lazy("accounttype_list")


# --- BRANCHES ---
class BranchListView(generic.ListView):
    model = Branch
    template_name = "core/pages/branch_list.html"

class BranchDetailView(generic.DetailView):
    model = Branch
    template_name = "core/pages/branch_detail.html"

class BranchCreateView(generic.CreateView):
    model = Branch
    fields = ["branch_name", "city", "country"]
    template_name = "core/pages/branch_form.html"
    success_url = reverse_lazy("branch_list")

class BranchUpdateView(BranchCreateView, generic.UpdateView):
    pass

class BranchDeleteView(SafeDeleteView):
    model = Branch
    template_name = "core/pages/branch_confirm_delete.html"
    success_url = reverse_lazy("branch_list")


# --- ACCOUNTS ---
class AccountListView(generic.ListView):
    model = Account
    template_name = "core/pages/account_list.html"

class AccountDetailView(generic.DetailView):
    model = Account
    template_name = "core/pages/account_detail.html"

class AccountCreateView(generic.CreateView):
    model = Account
    fields = ["client", "account_type", "branch", "balance"]
    template_name = "core/pages/account_form.html"
    success_url = reverse_lazy("account_list")

class AccountUpdateView(AccountCreateView, generic.UpdateView):
    pass

class AccountDeleteView(SafeDeleteView):
    model = Account
    template_name = "core/pages/account_confirm_delete.html"
    success_url = reverse_lazy("account_list")


# --- TRANSACTION TYPES ---
class TransactionTypeListView(generic.ListView):
    model = TransactionType
    template_name = "core/pages/transactiontype_list.html"

class TransactionTypeDetailView(generic.DetailView):
    model = TransactionType
    template_name = "core/pages/transactiontype_detail.html"

class TransactionTypeCreateView(generic.CreateView):
    model = TransactionType
    fields = ["type_name"]
    template_name = "core/pages/transactiontype_form.html"
    success_url = reverse_lazy("transactiontype_list")

class TransactionTypeUpdateView(TransactionTypeCreateView, generic.UpdateView):
    pass

class TransactionTypeDeleteView(SafeDeleteView):
    model = TransactionType
    template_name = "core/pages/transactiontype_confirm_delete.html"
    success_url = reverse_lazy("transactiontype_list")


# --- TRANSACTIONS ---
class TransactionListView(generic.ListView):
    model = Transaction
    template_name = "core/pages/transaction_list.html"

class TransactionDetailView(generic.DetailView):
    model = Transaction
    template_name = "core/pages/transaction_detail.html"

class TransactionCreateView(generic.CreateView):
    model = Transaction
    fields = ["sender_account", "receiver_account", "transaction_type", "amount", "description"]
    template_name = "core/pages/transaction_form.html"
    success_url = reverse_lazy("transaction_list")

class TransactionUpdateView(TransactionCreateView, generic.UpdateView):
    pass

class TransactionDeleteView(SafeDeleteView):
    model = Transaction
    template_name = "core/pages/transaction_confirm_delete.html"
    success_url = reverse_lazy("transaction_list")


# --- DASHBOARD ---
class DashboardView(generic.TemplateView):
    template_name = "core/pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clients"] = Client.objects.all()
        context["accounts"] = Account.objects.all()
        context["transactions"] = Transaction.objects.all()
        return context

from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .management.commands.NetworkHelper import NetworkHelper


class ExternalGenreBaseView(View):
    base_url = "http://127.0.0.1:3000/api/"
    helper = NetworkHelper(base_url=base_url, username="nazar", password="nazar")


class ExternalGenreListView(ExternalGenreBaseView):
    template_name = "core/pages/genre_list.html"

    def get(self, request):
        status, genres = self.helper.get("genres/")
        return render(request, self.template_name, {
            "genres": genres if status == 200 else [],
            "status": status
        })


class ExternalGenreDetailView(ExternalGenreBaseView):
    template_name = "core/pages/genre_detail.html"

    def get(self, request, pk):
        status, genre = self.helper.get(f"genres/{pk}/")
        return render(request, self.template_name, {
            "genre": genre,
            "status": status
        })


class ExternalGenreCreateView(ExternalGenreBaseView):
    template_name = "core/pages/genre_form.html"
    success_url = reverse_lazy("genre_list")

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        genrename = request.POST.get("genrename")
        status, response = self.helper.post("genres/", {"genrename": genrename})
        if status in (200, 201):
            return redirect(self.success_url)
        return render(request, self.template_name, {"response": response, "status": status})


class ExternalGenreUpdateView(ExternalGenreBaseView):
    template_name = "core/pages/genre_form.html"
    success_url = reverse_lazy("genre_list")

    def get(self, request, pk):
        status, genre = self.helper.get(f"genres/{pk}/")
        return render(request, self.template_name, {"genre": genre, "status": status})

    def post(self, request, pk):
        genrename = request.POST.get("genrename")
        status, response = self.helper.put(f"genres/{pk}/", {"genrename": genrename})
        if status in (200, 204):
            return redirect(self.success_url)
        return render(request, self.template_name, {"response": response, "status": status})


class ExternalGenreDeleteView(ExternalGenreBaseView):
    template_name = "core/pages/genre_confirm_delete.html"
    success_url = reverse_lazy("genre_list")

    def get(self, request, pk):
        status, genre = self.helper.get(f"genres/{pk}/")
        return render(request, self.template_name, {"genre": genre, "status": status})

    def post(self, request, pk):
        status, response = self.helper.delete(f"genres/{pk}/")
        if status in (200, 204):
            return redirect(self.success_url)
        return render(request, self.template_name, {"response": response, "status": status})
