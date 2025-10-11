import os

from src.reports import spending_by_category
from src.services import search_by_string, search_phone_number
from src.utils import get_path_return_dataframe
from src.views import main_func

transactions = get_path_return_dataframe(os.path.join("data/operations.xlsx"))
# забираю таблицу с данными для поиска
transactions_df = get_path_return_dataframe(os.path.join("data/operations.xlsx"))

if __name__ == "__main__":
    print(main_func("2018-05-20 15:30:00"))
    print(search_by_string(transactions_df, search_string=input("Введите строку/слово для поиска: ").capitalize()))
    print(search_phone_number(transactions_df))
    print(spending_by_category(transactions, "Супермаркеты", "21.12.2021"))
