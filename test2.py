import json
dict1 = json.load(open(r'C:\Code repositories\meal-manager\food-no-id.json', 'r', encoding='utf-8'))
for item in dict1:
    sub_item = ','
    pretty_name = item["pretty_name"]
    mandatory_ingredients = sub_item.join(item["mandatory_ingredients"])
    optional_ingredients = sub_item.join(item["optional_ingredients"])
    meal_time = sub_item.join(item["meal_time"])
    

    print("{}|{}|{}|{}".format(pretty_name, mandatory_ingredients, optional_ingredients, meal_time))