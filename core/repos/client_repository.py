from core.models import Client
from .base import BaseRepository

class ClientRepository(BaseRepository):
    def __init__(self):
        super().__init__(Client)

    # Add domain-specific methods if needed
    def find_by_email(self, email):
        return Client.objects.filter(email=email).first()
