from helpers.common_functions import read_csv_list
import os

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

names = read_csv_list(os.path.join(data_path, "firstnames-list.csv"))
profanity = read_csv_list(os.path.join(data_path, "profanity-list.csv"))
