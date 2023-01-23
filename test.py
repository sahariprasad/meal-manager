import pandas as pd
import openpyxl
import os

input_file_path = r'C:\Code repositories\meal-manager'

recipe_file = pd.ExcelFile(os.path.join(input_file_path, "test.xlsx"))
recipe_dfs = {sheet_name: recipe_file.parse(sheet_name) for sheet_name in recipe_file.sheet_names}
first_sheet = list(recipe_dfs.keys())[0]

def clean_ingredient_list(some_string):
    ingredient_list = some_string.split(',')
    ingredient_list = [item.strip().lower() for item in ingredient_list]
    return ingredient_list

recipe_dfs[first_sheet] = recipe_dfs[first_sheet].fillna('')
content_list = recipe_dfs[first_sheet].to_dict('records')

for item in content_list:
    item["mandatory_ingredients"] = clean_ingredient_list(item["mandatory_ingredients"])
    item["optional_ingredients"] = clean_ingredient_list(item["optional_ingredients"])
    item["meal_time"] = clean_ingredient_list(item["meal_time"])

for item in content_list:
    print(item)
    