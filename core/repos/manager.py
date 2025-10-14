from core.repos.account_repository import AccountRepository
from core.repos.client_repository import ClientRepository
from core.repos.transaction_repository import TransactionRepository


class RepositoryManager:
    def __init__(self):
        self.clients = ClientRepository()
        self.accounts = AccountRepository()
        self.transactions = TransactionRepository()