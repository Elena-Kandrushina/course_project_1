import json

import pandas as pd
import pytest

from src.services import search_by_string, search_phone_number


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        [
            {"Описание": "Тинькофф Мобайл +7 995 555-55-55", "Категория": "Мобильная связь"},
            {"Описание": "Перекрёсток", "Категория": "Супермаркеты"},
            {"Описание": "Почта России", "Категория": "Госуслуги"},
        ]
    )


def test_search_by_string_found_some(sample_df):
    result_json = search_by_string(sample_df, "Почта")
    result = json.loads(result_json)
    assert isinstance(result, list)


def test_search_phone_number_found_some(sample_df):
    result_json = search_phone_number(sample_df)
    result = json.loads(result_json)
    assert isinstance(result, list)
