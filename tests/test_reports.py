import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": ["10.07.2025 12:00:00", "15.08.2025 14:30:00", "01.08.2025 15:00:00"],
        "Категория": ["Супермаркеты", "Супермаркеты", "Транспорт"],
        "Сумма операции": [-1500, -2000, -500],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category_result(sample_transactions):
    result = spending_by_category(sample_transactions, category="Супермаркеты", date="01.09.2025")
    assert isinstance(result, pd.DataFrame)
    assert result["Категория"][0] == "Супермаркеты"
    assert result["Сумма расходов"][0] == 3500
