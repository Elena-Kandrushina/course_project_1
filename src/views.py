import json
from typing import Any, Dict

from src.utils import (get_currency_rates, get_datetime, get_number_card_total_spent_cashback, get_slice_by_period,
                       get_stock_prices, get_top_n_transactions, time_greeting_func)

file_path = "./data/operations.xlsx"
file_path_json = "./user_settings.json"


def main_func(date_str: str) -> Dict[str, Any]:
    """Функция принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ с приветствием,
    информацией по каждой карте, топ-5 транзакций по сумме платежа,
    курс валют и стоимость акций из S&P500"""

    # Страница «Главная» - Приветствие
    greeting = time_greeting_func()
    # Выборка по временному периоду с начала месяца по заданную дату
    period_datetime = get_datetime(date_str)
    filtered_table = get_slice_by_period(file_path, period_datetime)
    # Страница «Главная» - По каждой карте
    cards = get_number_card_total_spent_cashback(filtered_table)
    # Страница «Главная» - Топ-5 транзакций по сумме платежа
    top_transactions = get_top_n_transactions(filtered_table, n=5)
    # Страница «Главная» - Курс валют
    currency_rates = get_currency_rates(file_path_json)  # пока отключила, чтобы случайно
    # при запусках не тратить лимит запросов

    # Страница «Главная» - Стоимость акций из S&P500
    stock_prices = get_stock_prices(file_path_json)

    data_main = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    json_result = json.dumps(data_main, ensure_ascii=False, indent=2)

    return json_result
