from core.models import Transaction
from .base import BaseRepository

class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Transaction)