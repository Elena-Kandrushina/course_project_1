import json
from unittest.mock import patch

import pytest

from src.views import main_func


@pytest.fixture
def date_str():
    return "2021-12-29 22:32:24"


@patch("src.views.time_greeting_func")
@patch("src.views.get_datetime")
@patch("src.views.get_slice_by_period")
@patch("src.views.get_number_card_total_spent_cashback")
@patch("src.views.get_top_n_transactions")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_func(
    mock_get_stock_prices,
    mock_get_currency_rates,
    mock_get_top_n_transactions,
    mock_get_number_card_total_spent_cashback,
    mock_get_slice_by_period,
    mock_get_datetime,
    mock_time_greeting_func,
    date_str,
):

    mock_time_greeting_func.return_value = "Добрый день"
    mock_get_datetime.return_value = "2021.12.28 18:24:02"
    mock_get_slice_by_period.return_value = "filtered_data"
    mock_get_number_card_total_spent_cashback.return_value = {
        "card1": {"last_digits": "7197", "total_spent": 296.8, "cashback": 2.968}
    }
    mock_get_top_n_transactions.return_value = [
        {"date": "09.05.2018", "amount": 500, "category": "Пополнения", "description": "Перевод с карты"},
        {"date": "09.05.2018", "amount": 12006.4, "category": "Пополнения", "description": "Перевод с карты"},
    ]
    mock_get_currency_rates.return_value = {"USD": 60.5, "EUR": 70.2}
    mock_get_stock_prices.return_value = {"AAPL": 150, "MSFT": 280}

    result_json = main_func(date_str)

    result = json.loads(result_json)

    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result

    assert result["greeting"] == "Добрый день"
    assert isinstance(result["cards"], dict)
    assert isinstance(result["top_transactions"], list)
    assert isinstance(result["currency_rates"], dict)
    assert isinstance(result["stock_prices"], dict)

    mock_time_greeting_func.assert_called_once()
    mock_get_datetime.assert_called_once_with(date_str)
    mock_get_slice_by_period.assert_called_once()
    mock_get_number_card_total_spent_cashback.assert_called_once()
    mock_get_top_n_transactions.assert_called_once()
    mock_get_currency_rates.assert_called_once()
    mock_get_stock_prices.assert_called_once()
