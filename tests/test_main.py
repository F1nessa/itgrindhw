import pytest

from models import (
    AccountFrozenError,
    AccountStatus,
    BankAccount,
    InsufficientFundsError,
    InvalidOperationError,
    InvestmentAccount,
    PremiumAccount,
    SavingsAccount,
)


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


def test_savings_monthly_interest():
    """Начисление процентов увеличивает баланс вклада."""
    account = SavingsAccount(owner="Anna Smirnova", balance=1000, monthly_interest_rate=0.10)

    account.apply_monthly_interest()

    assert account._balance == pytest.approx(1100)


def test_savings_min_balance():
    """Нельзя снять средства ниже минимального остатка."""
    account = SavingsAccount(owner="Boris Volkov", balance=1000, min_balance=500)

    with pytest.raises(InvalidOperationError):
        account.withdraw(600)

    account.withdraw(400)
    assert account._balance == pytest.approx(600)


def test_savings_frozen_account():
    """Начисление процентов недоступно на замороженном счёте."""
    account = SavingsAccount(
        owner="Anna Smirnova",
        balance=1000,
        status=AccountStatus.FROZEN,
    )

    with pytest.raises(AccountFrozenError):
        account.apply_monthly_interest()


def test_premium_overdraft():
    """Премиум-счёт позволяет уходить в овердрафт с учётом комиссии."""
    account = PremiumAccount(owner="Vera Orlova", balance=100, overdraft_limit=1000)

    account.withdraw(500)
    assert account._balance == pytest.approx(-405)

    with pytest.raises(InsufficientFundsError):
        account.withdraw(2000)


def test_premium_transaction_fee():
    """С каждой транзакции списывается фиксированная комиссия."""
    account = PremiumAccount(owner="Gleb Sobolev", balance=100)

    account.withdraw(100)
    assert account._balance == pytest.approx(-5)


def test_investment_add_and_growth():
    """Вложения списываются с баланса и дают ожидаемый прирост."""
    account = InvestmentAccount(owner="Daria Belova", balance=10_000)

    account.add_investment("stocks", 1_000)
    account.add_investment("bonds", 2_000)

    assert account._balance == pytest.approx(7_000)
    assert account.investment_portfolio == {"stocks": 1_000, "bonds": 2_000}

    growth = account.project_yearly_growth({"stocks": 0.10, "bonds": 0.04})
    assert growth == pytest.approx(180)


def test_investment_checks():
    """Проверки допустимости актива и достаточности средств."""
    account = InvestmentAccount(owner="Egor Titov", balance=1_000)

    with pytest.raises(InvalidOperationError):
        account.add_investment("gold", 100)

    with pytest.raises(InsufficientFundsError):
        account.add_investment("stocks", 5_000)


def test_investment_withdraw():
    """Снятие из актива возвращает средства на баланс."""
    account = InvestmentAccount(owner="Daria Belova", balance=10_000)
    account.add_investment("etf", 2_000)

    account.withdraw("etf", 1_500)

    assert account._balance == pytest.approx(9_500)
    assert account.investment_portfolio == {"etf": 500}

    with pytest.raises(InvalidOperationError):
        account.withdraw("etf", 1_000)
