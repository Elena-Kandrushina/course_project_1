import json
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional

import pandas as pd

from src.utils import get_path_return_dataframe

# настраиваю логер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler("reports.log", encoding="utf-8")
log_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
logger.addHandler(log_handler)


# Отчеты - Траты по категории
# Декоратор без параметра - записывает данные в файл
def report_decorator(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        filename = f"{func.__name__}_report_{datetime.now().strftime('%Y.%m%d %H%M%S')}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Отчет '{filename}' сохранен.")
        return result

    return wrapper


transactions = get_path_return_dataframe("../data/operations.xlsx")


@report_decorator
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние 3 месяца
    от заданной даты или текущей даты.
    """

    if date:
        current_date = datetime.strptime(date, "%d.%m.%Y")
    else:
        current_date = datetime.now()
    # определяю начало периода из расчета, что 3 месяца это 91 день
    start_date = current_date - timedelta(days=91)

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True
    )

    filtered_transactions = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= current_date)
    ]

    expenses = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    total_spending = expenses["Сумма операции"].sum()
    total_spending = -1 * total_spending

    report_df = pd.DataFrame(
        {
            "Категория": [category],
            "Начало периода": [start_date.strftime("%d.%m.%Y")],
            "Конец периода": [current_date.strftime("%d.%m.%Y")],
            "Сумма расходов": [total_spending],
        }
    )

    return report_df


# print(spending_by_category(transactions, "Супермаркеты", "21.12.2021"))
