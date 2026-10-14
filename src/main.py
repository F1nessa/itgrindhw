"""Точка входа: демонстрация работы банковских счетов.

Показываем три специализированных типа счетов:
SavingsAccount, PremiumAccount и InvestmentAccount.
"""

from models import (
    InsufficientFundsError,
    InvalidOperationError,
    InvestmentAccount,
    PremiumAccount,
    SavingsAccount,
)

GROWTH_RATES = {"stocks": 0.10, "bonds": 0.04, "etf": 0.07}


def _section(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def _try(label, action):
    try:
        result = action()
        if result is not None:
            print(f"{label}: {result}")
    except (ValueError, TypeError, InvalidOperationError, InsufficientFundsError) as exc:
        print(f"{label}: отказано — {exc}")


def demo_savings_accounts():
    _section("SavingsAccount")

    accounts = [
        SavingsAccount(owner="Anna Smirnova", balance=10_000, monthly_interest_rate=0.01),
        SavingsAccount(
            owner="Boris Volkov",
            balance=50_000,
            monthly_interest_rate=0.02,
            min_balance=20_000,
        ),
    ]

    for account in accounts:
        print(account)
        before = account.balance
        account.apply_monthly_interest()
        print(f"  Начислены проценты: {before:.2f} -> {account.balance:.2f}")

    _try("Снятие 35 000 (ниже min_balance)", lambda: accounts[1].withdraw(35_000))
    _try("Снятие 10 000 (в пределах min_balance)", lambda: accounts[1].withdraw(10_000))
    print(accounts[1])


def demo_premium_accounts():
    _section("PremiumAccount")

    accounts = [
        PremiumAccount(owner="Vera Orlova", balance=5_000, overdraft_limit=2_000),
        PremiumAccount(owner="Gleb Sobolev", balance=500, overdraft_limit=1_000),
    ]

    for account in accounts:
        print(account)

    _try("Снятие 6 000 (в овердрафт)", lambda: accounts[0].withdraw(6_000))
    print(accounts[0])

    _try("Снятие 5 000 (сверх овердрафта)", lambda: accounts[0].withdraw(5_000))
    print(accounts[0])


def demo_investment_accounts():
    _section("InvestmentAccount")

    accounts = [
        InvestmentAccount(owner="Daria Belova", balance=100_000),
        InvestmentAccount(owner="Egor Titov", balance=10_000),
    ]

    portfolio_account, poor_account = accounts
    print(portfolio_account)

    _try("Вложение 40 000 в stocks", lambda: portfolio_account.add_investment("stocks", 40_000))
    _try("Вложение 30 000 в bonds", lambda: portfolio_account.add_investment("bonds", 30_000))
    _try("Вложение 20 000 в etf", lambda: portfolio_account.add_investment("etf", 20_000))
    _try("Вложение 1 000 в gold (недопустимый актив)", lambda: portfolio_account.add_investment("gold", 1_000))
    print(portfolio_account)

    growth = portfolio_account.project_yearly_growth(GROWTH_RATES)
    print(f"Ожидаемый годовой прирост портфеля: {growth:.2f} {portfolio_account.currency}")

    _try("Снятие 5 000 из etf", lambda: portfolio_account.withdraw("etf", 5_000))
    print(portfolio_account)

    _try("Вложение 50 000 при балансе 10 000", lambda: poor_account.add_investment("stocks", 50_000))
    print(poor_account)


def run_demo():
    """Запускает сценарии для всех специализированных типов счетов."""
    demo_savings_accounts()
    demo_premium_accounts()
    demo_investment_accounts()


if __name__ == "__main__":
    run_demo()
