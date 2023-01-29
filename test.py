import pandas as pd
import openpyxl
import os
import json

input_file_path = r"C:\Users\sahar\OneDrive\Personal\Documents"

recipe_file = pd.ExcelFile(os.path.join(input_file_path, "mealplan.xlsx"))
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

file_out = open("test_out.json", "w", encoding='utf-8')
file_out.write(json.dumps(content_list))
file_out.close()
