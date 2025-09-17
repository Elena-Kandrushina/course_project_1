import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

# настраиваю логер
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def time_greeting_func() -> str:
    """Функция возвращает приветствие в формате 'Доброе утро'/'Добрый день'/'Добрый вечер'/
    'Доброй ночи' в зависимости от текущего времени"""

    logger.info("Определение текущего времени")
    # время пользователя в часах на момент "сейчас"
    time_user = datetime.now().hour
    if 5 <= time_user < 12:
        return "Доброе утро"
    elif 12 <= time_user < 18:
        return "Добрый день"
    elif 18 <= time_user < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_datetime(date_str: str, datetime_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """Функция принимает строку с датой и возвращает список дат, первая соответствует
    началу периода, а вторая дате, переданной в функцию"""

    datetime_str = datetime.strptime(date_str, datetime_format)

    beginning_of_month = datetime_str.replace(day=1)
    logger.info("Вывод временного периода от начала месяца до указанной даты")
    return [beginning_of_month.strftime("%d.%m.%Y %H:%M:%S"), datetime_str.strftime("%d.%m.%Y %H:%M:%S")]


file_path = "../data/operations.xlsx"


def get_slice_by_period(file_path: str, period_datetime: list) -> DataFrame:
    """Функция принимает путь к файлу operations.xlsx и временной отрезок, возвращает
    таблицу соответствующую выбранному периоду"""
    logger.info("Чтение файла")
    read_file = pd.read_excel(file_path, sheet_name="Отчет по операциям")

    # преобразую строковый тип к времени
    read_file["Дата операции"] = pd.to_datetime(read_file["Дата операции"], dayfirst=True)
    begin_date = datetime.strptime(period_datetime[0], "%d.%m.%Y %H:%M:%S")
    finish_date = datetime.strptime(period_datetime[1], "%d.%m.%Y %H:%M:%S")
    logger.info("Выборка по временному периоду")

    slice_read_file = read_file[
        (read_file["Дата операции"] >= begin_date) & (read_file["Дата операции"] <= finish_date)
    ]

    sorted_slice_read_file = slice_read_file.sort_values(by="Дата операции", ascending=True)
    return sorted_slice_read_file


def get_number_card_total_spent_cashback(filtered_table: DataFrame) -> list[dict]:
    """Функция принимает таблицу с выборкой по временному периоду и возвращает список словарей
    с ключами 'last_digits', 'total_spent', 'cashback'"""

    cards_list_with_transactions = []

    filtered_cards = filtered_table[["Номер карты", "Сумма операции с округлением", "Кэшбэк", "Сумма операции"]]
    logger.info("Формирование выборки для отображения на главной странице")

    for index, row in filtered_cards.iterrows():

        if row["Сумма операции"] < 0:
            last_digits = str(row["Номер карты"]).replace("*", "")
            total_spent = row["Сумма операции с округлением"]
            cashback = total_spent / 100
            rows = {"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback}
            cards_list_with_transactions.append(rows)

    return cards_list_with_transactions


def get_top_n_transactions(sorted_slice_read_file: DataFrame, n: int) -> list[dict]:
    """Функция принимает таблицу с выборкой по временному периоду и число, определяющее
     количество словарей в списке (топ транзакций по сумме платежа) и возвращает список
    словарей с обозначенным количеством транзакций"""

    top_transactions = []

    sorted_slice_read_file_amount = sorted_slice_read_file.sort_values(by="Сумма операции", ascending=False)
    top_transactions_n = sorted_slice_read_file_amount.head(n)

    top_transactions_n_filtered = top_transactions_n[["Дата платежа", "Сумма операции", "Категория", "Описание"]]
    logger.info("Формирование выборки топа транзакций")

    for index, row in top_transactions_n_filtered.iterrows():
        rows = {
            "date": row["Дата платежа"],
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"],
        }

        top_transactions.append(rows)

    return top_transactions


load_dotenv()
file_path_json = "../user_settings.json"


# пока отключаю функцию, чтобы не расходовать лимит запросов
def get_currency_rates(file_path_json: str) -> list[dict]:
    """Функция принимает путь к файлу user_settings.json и возвращает
    курс валют"""

    currency_rates_apilayer = []
    # безопасно открываю файл user_settings.json
    with open(file_path_json, "r", encoding="utf-8") as file_json:
        data_in_json = json.load(file_json)
        currency_list = data_in_json.get("user_currencies", [])
        # print(currency_list) # проверяю для себя что в списке USD и EUR

    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise ValueError("API_KEY не найден!")

    for currency in currency_list:
        try:
            logger.info("Запрос")
            url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
            headers = {"apikey": API_KEY}
            response = requests.get(url, headers=headers)
            # print(response.text) # проверяю для себя ответ
            response.raise_for_status()
            data = response.json()
            rate = round(float(data["result"]), 2)
            from_currency = data["query"]["from"]
            currency_rates_apilayer.append({"currency": from_currency, "rate": rate})

        except Exception as e:
            print(f"Ошибка конвертации для {currency}: {e}")

    return currency_rates_apilayer


def get_stock_prices(file_path_json: str) -> list[dict]:
    """Функция принимает путь к файлу user_settings.json и возвращает
    стоимость акций из S&P500"""

    stock_prices = []

    with open(file_path_json, "r", encoding="utf-8") as file_json:
        data_in_json = json.load(file_json)
        stocks = data_in_json.get("user_stocks", [])
        API_KEY_for_stocks = os.getenv("API_KEY_FOR_STOCKS")

        for stock in stocks:
            logger.info("Запрос")
            url = f"https://api.twelvedata.com/price?symbol={stock}&apikey={API_KEY_for_stocks}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            # print(response.text) # проверяю для себя ответ
            price = float(data["price"])
            stock_name = stock
            stock_prices.append({"stock": stock_name, "price": price})
        return stock_prices


def get_path_return_dataframe(file_path: str) -> pd.DataFrame:
    """Функция принимает путь к файлу operations.xlsx
    и возвращает DataFrame со всеми транзакциями"""

    try:
        logger.info("Чтение файла и запись Df")
        read_file_df = pd.read_excel(file_path, sheet_name="Отчет по операциям")
        return read_file_df
    except FileNotFoundError:

        return f"Файл не найден: {file_path}"

    except Exception as e:
        logger.error("Ошибка")
        return f"Ошибка: {e}"


# print(get_path_return_dataframe("../data/operations.xlsx"))
