from core.models import Account
from .base import BaseRepository

class AccountRepository(BaseRepository):
    def __init__(self):
        super().__init__(Account)

    def get_by_client(self, client_id):
        return self.model.objects.filter(client_id=client_id)