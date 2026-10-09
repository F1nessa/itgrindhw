import pytest
from accounts import (AccountStatus, BankAccount, InvalidOperationError, InsufficientFundsError, AccountFrozenError, AccountClosedError)

def test_account_creation():
    account = BankAccount(owner="Ivan Ivanov")

    assert account.owner == "Ivan Ivanov"
    assert account._balance == 0
    assert account.currency == "RUB"
    assert account.status == AccountStatus.ACTIVE
    assert len(account.account_id) == 8


def test_create_active_and_frozen_accounts():
    """Создание активного и замороженного счетов."""
    active_account = BankAccount(owner="Ivan Ivanov", balance=1000)
    frozen_account = BankAccount(
        owner="Petr Petrov",
        balance=500,
        status=AccountStatus.FROZEN,
    )

    assert active_account.status == AccountStatus.ACTIVE
    assert frozen_account.status == AccountStatus.FROZEN

    print(active_account)
    print(frozen_account)

def test_operations_on_frozen_account():
    """Попытки пополнения и снятия с замороженного счёта."""
    account = BankAccount(
        owner="Petr Petrov",
        balance=500,
        status=AccountStatus.FROZEN,
    )

    with pytest.raises(AccountFrozenError):
        account.deposit(100)

    with pytest.raises(AccountFrozenError):
        account.withdraw(100)

    assert account._balance == 500

def test_valid_deposit_and_withdraw():
    """Успешное пополнение и снятие средств."""
    account = BankAccount(owner="Ivan Ivanov", balance=1000)

    account.deposit(500)
    assert account._balance == 1500

    account.withdraw(300)
    assert account._balance == 1200

    print(account)

