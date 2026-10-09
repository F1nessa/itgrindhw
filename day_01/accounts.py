import math
from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4

ALLOWED_CURRENCIES = {"RUB", "USD", "EUR", "KZT", "CNY"}


class AccountFrozenError(Exception):
    """Raised when an operation is attempted on a frozen account."""

class AccountClosedError(Exception):
    """Raised when an operation is attempted on a closed account."""

class InvalidOperationError(Exception):
    """Raised when a banking operation is invalid."""

class InsufficientFundsError(Exception):
    """Raised when an account has insufficient funds."""

class AccountStatus(Enum):
    ACTIVE = "Account is active"
    FROZEN = "Account is frozen"
    CLOSED = "Account is closed"


class AbstractAccount(ABC):
    def __init__(self, account_id, owner,balance = 0, status=AccountStatus.ACTIVE):
        self._account_id = account_id
        self._owner = owner 
        self._balance = balance
        self._status = status

    @property
    def account_id(self):
        return self._account_id

    @property
    def owner(self):
        return self._owner

    @property
    def balance(self):
        return self._balance

    @property
    def status(self):
        return self._status

    @abstractmethod
    def get_account_info(self):
        pass

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass


class BankAccount(AbstractAccount):
    def __init__(self, account_id=None, owner=None, balance=0, status=AccountStatus.ACTIVE, currency="RUB"):

        if not isinstance(owner, str) or not owner.strip(): 
            raise ValueError("Owner must be a non-empty string")

        if not isinstance(currency, str) or currency not in ALLOWED_CURRENCIES:
            raise ValueError(f"Currency must be one of {ALLOWED_CURRENCIES}")

        self._validate_balance(balance)

        if not isinstance(status, AccountStatus): 
            raise ValueError("Invalid account status")

        if account_id is None: 
            account_id = uuid4().hex[:8] 
        elif not isinstance(account_id, str) or not account_id.strip(): 
            raise ValueError("Account ID must be a non-empty string")
        
        super().__init__( 
            account_id=account_id, 
            owner=owner.strip(), 
            balance=balance, 
            status=status, ) 
        self.currency = currency

    @staticmethod
    def _validate_balance(balance):
        if isinstance(balance, bool) or not isinstance(balance, (int, float)):
            raise TypeError("Balance must be a number")
        if not math.isfinite(balance) or balance < 0:
            raise ValueError("Balance must be finite and non-negative")

    @staticmethod
    def _validate_amount(amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise InvalidOperationError("Amount must be a number")

        if not math.isfinite(amount) or amount <= 0:
            raise InvalidOperationError("Amount must be finite and positive")

    def deposit(self, amount): 
        self._ensure_active() 
        self._validate_amount(amount) 
        self._balance += amount 

    def withdraw(self, amount): 
        self._ensure_active() 
        self._validate_amount(amount) 
        if amount > self._balance: 
            raise InsufficientFundsError("Insufficient funds") 
        
        self._balance -= amount 
    
    def _ensure_active(self):
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError("Account is frozen")
        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("Account is closed")

    
    def get_account_info(self): 
        return { "account_id": self.account_id, "owner": self.owner, "balance": self._balance, "currency": self.currency, "status": self.status.value, }

    def __str__(self):
        masked_id = f"****{self.account_id[-4:]}"
        return (
        f"{type(self).__name__}("
        f"owner={self.owner}, "
        f"account_id={masked_id}, "
        f"status={self.status.value}, "
        f"balance={self._balance:.2f} {self.currency})"
        )
