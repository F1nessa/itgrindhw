import datetime

from accounts import BankAccount

from clients import Client
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
        self.blocked_clients = set()

    def add_client(self, client):
        """Добавляет клиента в банк."""
        self.check_operation_time()
        if not isinstance(client, Client):
            raise TypeError("Expected a Client instance")
        if client.client_id in self.clients:
            raise ValueError("Client already exists")
        self.clients[client.client_id] = client

    def add_account(self, account):
        """Добавляет счет в банк."""
        self.check_operation_time()
        if not isinstance(account, BankAccount):
            raise TypeError("Expected a BankAccount instance")
        if account.account_id in self.accounts:
            raise ValueError("Account already exists")
        self.accounts[account.account_id] = account

    def close_account(self, account_id):
        """Закрывает счет по его идентификатору."""
        self.check_operation_time()
        account = self.accounts.get(account_id)
        if account:
            account.status = AccountStatus.CLOSED
            # del self.accounts[account_id]

    def freeze_account(self, account_id):
        """Замораживает счет по его идентификатору."""
        self.check_operation_time()
        account = self.accounts.get(account_id)
        if account:
            account.status = AccountStatus.FROZEN

    def unfreeze_account(self, account_id):
        """Размораживает счет по его идентификатору. 
        Размораживать можно только замороженный счёт, 
        а закрытый счёт нельзя просто вернуть в активное состояние."""
        self.check_operation_time()
        account = self.accounts.get(account_id)
        if account and account.status == AccountStatus.FROZEN:
            account.status = AccountStatus.ACTIVE
        else:
            raise ValueError("Account must be frozen to unfreeze it.")

    def search_accounts(self, owner_name=None, account_id=None):
        """Ищет счета по имени владельца"""
        self.check_operation_time()
        return [
            account
            for account in self.accounts.values()
            if account.owner_name == owner_name
        ]

    def authenticate_client(self, client_id, is_valid=True):
        """Проверяет, существует ли клиент с данным идентификатором."""
        self.check_operation_time()
        if client_id in self.blocked_clients:
            self._log_suspicious_activity(
                client_id, "Login attempt by blocked client"
            )
            return False

        if client_id not in self.clients:
            self.login_attempts[client_id] = (
                self.login_attempts.get(client_id, 0) + 1
            )
            self._log_suspicious_activity(
                client_id, "Login attempt with unknown client ID"
            )
            return False
        if not is_valid:
            attempts = self.login_attempts.get(client_id, 0) + 1
            self.login_attempts[client_id] = attempts

            self._log_suspicious_activity(
                client_id, f"Failed login attempt: {attempts}"
            )

            if attempts >= self.MAX_LOGIN_ATTEMPTS:
                self.blocked_clients.add(client_id)
                self.clients[client_id].status = "blocked"
                self._log_suspicious_activity(
                    client_id, "Client blocked after failed logins"
                )
            return False

        self.login_attempts[client_id] = 0
        return True

    def _log_suspicious_activity(self, client_id, reason):
        """Записывает подозрительное действие."""
        self.suspicious_activity_log.append({
            "client_id": client_id,
            "reason": reason,
            "timestamp": datetime.datetime.now(),
        })

    def check_operation_time(self, current_time=None):
        """Запрещает операции с 00:00 до 05:00."""
        if current_time is None:
            current_time = datetime.datetime.now().time()

        if self.NIGHT_START <= current_time.hour < self.NIGHT_END:
            raise PermissionError(
                "Bank operations are prohibited from 00:00 to 05:00"
            )

    def get_total_balance(self):
        """Возвращает сумму балансов всех счетов."""
        return sum(
            account.balance
            for account in self.accounts.values()
        )

    def get_clients_ranking(self):
        """Возвращает клиентов по убыванию суммы на их счетах."""
        balances = {
            client_id: 0
            for client_id in self.clients
        }

        for account in self.accounts.values():
            client_id = getattr(account, "client_id", None)

            if client_id in balances:
                balances[client_id] += account.balance

        return sorted(
            self.clients.values(),
            key=lambda client: balances[client.client_id],
            reverse=True,
        )