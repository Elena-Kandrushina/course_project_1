import json
import logging
import re
from typing import Any, Dict

from src.utils import get_path_return_dataframe

# настраиваю логер
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

# Сервисы - Простой поиск
transactions_df = get_path_return_dataframe("../data/operations.xlsx")


def search_by_string(transactions_df, search_string: str) -> Dict[str, Any]:
    """Функция принимает таблицу с данными и строку/слово для поиска и возвращает JSON-ответ со всеми
    транзакциями, содержащими запрос в описании или категории"""

    # создаю пустой список с транзакциями, куда будут записываться операции,
    transactions = []

    logger.info("Поиск по заданной строке/слову - выборка")

    for index, row in transactions_df.iterrows():
        if isinstance(row["Описание"], str):
            description = row["Описание"]
        else:
            description = ""
        if isinstance(row["Категория"], str):
            category = row["Категория"]
        else:
            category = ""

        if search_string in category or search_string in description:
            transactions.append(row.to_dict())

    logger.info("Запись результата выборки в json")
    json_result = json.dumps(transactions, ensure_ascii=False, indent=2)
    return json_result


# Сервисы - Поиск по телефонным номерам
def search_phone_number(transactions_df) -> Dict[str, Any]:
    """Функция таблицу с данными и возвращает JSON-ответ со всеми транзакциями,
    содержащими в описании мобильные номера"""

    transactions = []

    logger.info("Поиск в столбце описание мобильных номеров - выборка")

    for index, row in transactions_df.iterrows():
        if isinstance(row["Описание"], str):
            description = row["Описание"]
        else:
            description = ""
        pattern = r"(?:\+7|8)?\s*\d{3}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}"
        numbers = re.findall(pattern, description)

        if numbers:
            transactions.append(row.to_dict())
    # получаю в виде json-ответа
    logger.info("Запись результата выборки в json")
    json_result = json.dumps(transactions, ensure_ascii=False, indent=2)
    return json_result


# print(search_by_string(transactions_df, search_string=input("Введите строку/слово для поиска: ").capitalize()))
# print(search_phone_number(transactions_df))
