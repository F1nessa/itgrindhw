"""Вспомогательные функции для валидации и форматирования данных."""

import math

ALLOWED_CURRENCIES = {"RUB", "USD", "EUR", "KZT", "CNY"}


def is_number(value):
    """True, если value — число (bool не считается числом)."""
    return not isinstance(value, bool) and isinstance(value, (int, float))


def is_finite(value):
    """True, если value — конечное число (не NaN/inf)."""
    return is_number(value) and math.isfinite(value)


def is_valid_balance(balance):
    """Баланс должен быть конечным неотрицательным числом."""
    return is_finite(balance) and balance >= 0


def is_valid_amount(amount):
    """Сумма операции должна быть конечным положительным числом."""
    return is_finite(amount) and amount > 0


def is_valid_currency(currency):
    """True, если валюта входит в список допустимых."""
    return isinstance(currency, str) and currency in ALLOWED_CURRENCIES


def mask_account_id(account_id):
    """Маскирует идентификатор счёта, оставляя последние 4 символа."""
    return f"****{account_id[-4:]}"
