import json
import os
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (get_currency_rates, get_datetime, get_number_card_total_spent_cashback,
                       get_path_return_dataframe, get_slice_by_period, get_stock_prices, get_top_n_transactions,
                       time_greeting_func)


def test_time_greeting_func() -> str:
    result = time_greeting_func()
    assert result in ("Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи")


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2025-09-17 08:08:00", ["01.09.2025 08:08:00", "17.09.2025 08:08:00"]),
        ("2024-02-10 12:30:45", ["01.02.2024 12:30:45", "10.02.2024 12:30:45"]),
    ],
)
def test_get_datetime(date_str: str, expected: list[str]) -> list[str]:
    result = get_datetime(date_str)
    assert result == expected


@pytest.fixture
def test_data_df():
    """Фикстура возвращает DataFrame с тестовыми данными"""
    data = {
        "Дата операции": ["01.09.2025 10:00:00", "15.09.2025 12:00:00", "20.09.2025 14:00:00"],
        "Описание": ["Перевод между счетами", "Магнит", "Метро Санкт-Петербург"],
        "Сумма операции": [100, 200, 150],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def test_get_slice_by_period(tmp_path, test_data_df):
    file_path = tmp_path / "operations_test.xlsx"
    # Записываю DataFrame из фикстуры в Excel
    with pd.ExcelWriter(file_path) as writer:
        test_data_df.to_excel(writer, index=False, sheet_name="Отчет по операциям")
    period = ["01.09.2025 00:00:00", "17.09.2025 23:59:59"]

    result_df = get_slice_by_period(str(file_path), period)
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 2

    begin_date = datetime.strptime(period[0], "%d.%m.%Y %H:%M:%S")
    finish_date = datetime.strptime(period[1], "%d.%m.%Y %H:%M:%S")

    for dt in result_df["Дата операции"]:
        assert begin_date <= dt <= finish_date


@pytest.fixture
def excel_table():
    data = {
        "Номер карты": ["*5678", "*8765", "*2222"],
        "Сумма операции с округлением": [1000, 500, 250],
        "Кэшбэк": [10, 5, 2.5],
        "Сумма операции": [-1000, 500, -250],
    }
    return pd.DataFrame(data)


def test_get_number_card_total_spent_cashback(excel_table):
    result = get_number_card_total_spent_cashback(excel_table)

    # Только расходы "Сумма операции" отрицательная
    assert isinstance(result, list)
    assert len(result) == 2
    first = result[0]
    assert "last_digits" in first
    assert "total_spent" in first
    assert "cashback" in first
    assert first["last_digits"] == "5678"
    assert first["total_spent"] == 1000
    assert first["cashback"] == 10


@pytest.fixture
def sample_sorted_slice():
    data = {
        "Дата платежа": ["10.09.2025", "11.09.2025", "12.09.2025", "13.09.2025"],
        "Сумма операции": [1000, 2000, 500, 1500],
        "Категория": ["Госуслуги", "Фастфуд", "Супермаркеты", "Транспорт"],
        "Описание": ["Почта России", "Suptaun", "Семишагофф", "СПб ГУП 'Пассажиравтотранс'"],
    }
    df = pd.DataFrame(data)

    return df


def test_get_top_n_transactions(sample_sorted_slice):
    n = 3
    transactions = get_top_n_transactions(sample_sorted_slice, n)

    assert isinstance(transactions, list)
    assert len(transactions) == n
    first = transactions[0]
    expected_keys = {"date", "amount", "category", "description"}
    assert set(first.keys()) == expected_keys
    assert first["amount"] == 2000
    assert first["category"] == "Фастфуд"
    assert first["description"] == "Suptaun"


@patch("pandas.read_excel")
def test_get_path_return_dataframe_general_exception(mock_read_excel):
    mock_read_excel.side_effect = FileNotFoundError("Файл не найден: path.xlsx")
    result = get_path_return_dataframe("path.xlsx")
    assert result


def test_get_currency_rates_simple():
    file_path = "test_user_settings.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"user_currencies": ["USD", "EUR"]}, f)

    os.environ["API_KEY"] = "test_key"

    def mock_get(url, headers):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        if "from=USD" in url:
            mock_response.json = Mock(return_value={"result": 70.1234, "query": {"from": "USD"}})
        elif "from=EUR" in url:
            mock_response.json = Mock(return_value={"result": 85.9876, "query": {"from": "EUR"}})
        else:
            mock_response.json = Mock(return_value={})
        return mock_response

    with patch("requests.get", mock_get):
        result = get_currency_rates(file_path)

    expected = [{"currency": "USD", "rate": 70.12}, {"currency": "EUR", "rate": 85.99}]

    assert result == expected


def test_get_stock_prices_simple():
    file_path = "test_user_settings.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"user_stocks": ["AAPL", "MSFT"]}, f)

    os.environ["API_KEY_FOR_STOCKS"] = "dummy_key_stock"

    def mock_get(url):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        if "symbol=AAPL" in url:
            mock_response.json = Mock(return_value={"price": "145.67"})
        elif "symbol=MSFT" in url:
            mock_response.json = Mock(return_value={"price": "299.12"})
        else:
            mock_response.json = Mock(return_value={})
        return mock_response

    with patch("requests.get", mock_get):
        result = get_stock_prices(file_path)

    expected = [{"stock": "AAPL", "price": 145.67}, {"stock": "MSFT", "price": 299.12}]

    assert result == expected
