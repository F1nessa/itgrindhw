"""Модели данных банковских счетов."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar
from uuid import uuid4

from utils import is_finite, is_number, is_valid_currency, mask_account_id


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
    def __init__(self, account_id, owner, balance=0, status=AccountStatus.ACTIVE):
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

        if not is_valid_currency(currency):
            raise ValueError("Currency must be one of the allowed currencies")

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
            status=status,
        )
        self.currency = currency

    @staticmethod
    def _validate_balance(balance):
        if not is_number(balance):
            raise TypeError("Balance must be a number")
        if not is_finite(balance) or balance < 0:
            raise ValueError("Balance must be finite and non-negative")

    @staticmethod
    def _validate_amount(amount):
        if not is_number(amount):
            raise InvalidOperationError("Amount must be a number")
        if not is_finite(amount) or amount <= 0:
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
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self._balance,
            "currency": self.currency,
            "status": self.status.value,
        }

    def __str__(self):
        return (
            f"{type(self).__name__}("
            f"owner={self.owner}, "
            f"account_id={mask_account_id(self.account_id)}, "
            f"status={self.status.value}, "
            f"balance={self._balance:.2f} {self.currency})"
        )


class SavingsAccount(BankAccount):
    '''
    # - 🔒 min_balance — минимальный остаток
    # - 📈 месячная ставка доходности
    # - 💰 метод apply_monthly_interest()
    '''
    def __init__(self, account_id=None, owner=None, balance=0, status=AccountStatus.ACTIVE, currency="RUB", monthly_interest_rate=0.01, min_balance=0):
        self._validate_balance(min_balance)
        super().__init__(account_id, owner, balance, status, currency)
        self.monthly_interest_rate = monthly_interest_rate # 📈 месячная ставка доходности
        self.min_balance = min_balance # 🔒 минимальный остаток

    def apply_monthly_interest(self):
        self._ensure_active()
        interest = self._balance * self.monthly_interest_rate
        self._balance += interest

    def withdraw(self, amount):
        self._ensure_active()
        self._validate_amount(amount)

        if self._balance - amount < self.min_balance:
            raise InvalidOperationError(
                "Cannot withdraw below minimum balance"
            )

        self._balance -= amount

    def get_account_info(self):
        info = super().get_account_info()

        info["min_balance"] = self.min_balance
        info["monthly_interest_rate"] = self.monthly_interest_rate

        return info

    def __str__(self):
        return (
            f"SavingsAccount(owner={self.owner}, "
            f"balance={self._balance:.2f} {self.currency}, "
            f"min_balance={self.min_balance:.2f}, "
            f"status={self.status.value})"
        )


class PremiumAccount(BankAccount):
    '''
    # - ⬆️ увеличенные лимиты
    # - 💳 возможность овердрафта
    # - 📊 фиксированная комиссия
        - withdraw()
        - get_account_info()
        - __str__()
    '''
    def __init__(self, account_id=None, owner=None, balance=0, status=AccountStatus.ACTIVE, currency="RUB", overdraft_limit=1000):
        super().__init__(account_id, owner, balance, status, currency)
        self.overdraft_limit = overdraft_limit
        self.transaction_fee = 5  # Фиксированная комиссия за каждую транзакцию

    def withdraw(self, amount):
        self._ensure_active()
        self._validate_amount(amount)
        total_amount = amount + self.transaction_fee
        if total_amount > self._balance + self.overdraft_limit:
            raise InsufficientFundsError("Insufficient funds including overdraft limit and transaction fee")
        self._balance -= total_amount

    def get_account_info(self):
        info = super().get_account_info()
        info["overdraft_limit"] = self.overdraft_limit
        info["transaction_fee"] = self.transaction_fee
        return info

    def __str__(self):
        return (
            f"PremiumAccount(owner={self.owner}, "
            f"balance={self._balance:.2f} {self.currency}, "
            f"overdraft_limit={self.overdraft_limit:.2f}, "
            f"transaction_fee={self.transaction_fee:.2f}, "
            f"status={self.status.value})"
        )


class InvestmentAccount(BankAccount):
    '''
    - 📊 инвестиционный портфель хранит сумму, распределённую между типами активов
    - 💼 допустимые виртуальные типы активов: stocks, bonds, etf
    - 📈 метод project_yearly_growth(growth_rates) рассчитывает ожидаемый годовой прирост портфеля
    - 🧮 growth_rates передаётся в метод как словарь «тип актива → годовая ставка»
    - 🧪 для демонстрации использовать условные ставки: stocks — 10%, bonds — 4%, etf — 7%
    - ✅ проверять допустимость типа актива, положительность суммы и достаточность средств
        - withdraw()
        - get_account_info()
        - __str__()
    '''
    ALLOWED_ASSETS = {"stocks", "bonds", "etf"}

    def __init__(self, account_id=None, owner=None, balance=0, status=AccountStatus.ACTIVE, currency="RUB", investment_portfolio=None):
        super().__init__(account_id, owner, balance, status, currency)
        self.investment_portfolio = investment_portfolio or {}

    def add_investment(self, investment_name, amount):
        self._ensure_active()
        self._validate_amount(amount)
        if investment_name not in self.ALLOWED_ASSETS:
            raise InvalidOperationError(
                f"Asset type must be one of {self.ALLOWED_ASSETS}"
            )
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient funds to invest")
        if investment_name in self.investment_portfolio:
            self.investment_portfolio[investment_name] += amount
        else:
            self.investment_portfolio[investment_name] = amount
        self._balance -= amount

    def withdraw(self, investment_name, amount):
        self._ensure_active()
        if investment_name not in self.investment_portfolio:
            raise InvalidOperationError("Investment not found")
        if amount > self.investment_portfolio[investment_name]:
            raise InvalidOperationError("Insufficient investment amount")
        self.investment_portfolio[investment_name] -= amount
        if self.investment_portfolio[investment_name] == 0:
            del self.investment_portfolio[investment_name]
        self._balance += amount

    def project_yearly_growth(self, growth_rates):
        projected_growth = 0
        for investment_name, amount in self.investment_portfolio.items():
            if investment_name not in growth_rates:
                raise InvalidOperationError(f"Growth rate for {investment_name} not provided")
            growth_rate = growth_rates[investment_name]
            if growth_rate < 0:
                raise InvalidOperationError("Growth rate must be non-negative")
            projected_growth += amount * growth_rate
        return projected_growth

    def get_account_info(self):
        info = super().get_account_info()
        info["investment_portfolio"] = self.investment_portfolio
        return info

    def __str__(self):
        return (
            f"InvestmentAccount(owner={self.owner}, "
            f"balance={self._balance:.2f} {self.currency}, "
            f"investment_portfolio={self.investment_portfolio}, "
            f"status={self.status.value})"
        )