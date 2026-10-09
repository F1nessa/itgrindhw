"""Точка входа: демонстрация работы банковских счетов."""

from models import AccountFrozenError, AccountStatus, BankAccount, InsufficientFundsError


def run_demo():
    """Небольшой сценарий, показывающий основные операции со счётом."""
    account = BankAccount(owner="Ivan Ivanov", balance=1000, currency="RUB")
    print(account)

    account.deposit(500)
    account.withdraw(300)
    print(account.get_account_info())

    frozen = BankAccount(owner="Petr Petrov", balance=500, status=AccountStatus.FROZEN)
    try:
        frozen.deposit(100)
    except AccountFrozenError as exc:
        print(f"Отказано: {exc}")

    try:
        account.withdraw(10_000)
    except InsufficientFundsError as exc:
        print(f"Отказано: {exc}")


if __name__ == "__main__":
    run_demo()
