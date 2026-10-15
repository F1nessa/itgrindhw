from clients import Client
from accounts import Account
from utils import AccountStatus

'''

2. Класс Bank
Методы:
- add_client()
- open_account()
- close_account()
- freeze_account()
- unfreeze_account()
- authenticate_client()
- search_accounts()

'''

class Bank:
    def __init__(self):
        self.clients = {}
        self.accounts = {}
        self.login_attempts = {}
        self.suspicious_activity_log = []

    def add_client(self, client):
        """Добавляет клиента в банк."""
        if not isinstance(client, Client):
            raise TypeError("Expected a Client instance")
        self.clients[client.client_id] = client

    def add_account(self, account):
        """Добавляет счет в банк."""
        if not isinstance(account, Account):
            raise TypeError("Expected an Account instance")
        self.accounts[account.account_id] = account

    def close_account(self, account_id):
        """Закрывает счет по его идентификатору."""
        account = self.accounts.get(account_id)
        if account:
            account.status = AccountStatus.CLOSED
            # del self.accounts[account_id]

    def freeze_account(self, account_id):
        """Замораживает счет по его идентификатору."""
        account = self.accounts.get(account_id)
        if account:
            account.status = AccountStatus.FROZEN

    def unfreeze_account(self, account_id):
        """Размораживает счет по его идентификатору. 
        Размораживать можно только замороженный счёт, 
        а закрытый счёт нельзя просто вернуть в активное состояние."""
        account = self.accounts.get(account_id)
        if account and account.status == AccountStatus.FROZEN:
            account.status = AccountStatus.ACTIVE
        else:
            raise ValueError("Account must be frozen to unfreeze it.")

    def search_accounts(self, owner_name=None, account_id=None):
        """Ищет счета по имени владельца"""
        return [
            account
            for account in self.accounts.values()
            if account.owner_name == owner_name
        ]


    def authenticate_client(self, client_id):
        """Проверяет, существует ли клиент с данным идентификатором."""
        return client_id in self.clients