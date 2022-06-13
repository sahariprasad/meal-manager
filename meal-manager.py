import os, json
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hey there!'


@app.route('/find_food/<item_list_string>')
def find_food(item_list_string=None):
    item_list_string = item_list_string.replace('\n',',').lower()
    print(item_list_string)
    available_items = item_list_string.split(',')
    # get available items list
    # available_items = ["bread", "cheese", "chocos", "semiya", "onion", "chilli"]

    # read all recipes
    recipe_path = "recipes"
    recipe_files = [pos_json for pos_json in os.listdir(recipe_path) if pos_json.endswith('.json')]

    recipe_dict = {}
    for item in recipe_files:
        recipe_name = item.replace(".json", "")
        file = open(recipe_path + '/' + item, 'r', encoding='utf-8')
        file_dict = json.load(file)
        recipe_dict[recipe_name] = file_dict

    # Check for possible dishes
    possible_dishes = []
    for item in recipe_dict:
        if set(recipe_dict[item]["ingredients"]["mandatory"]).issubset(available_items):
            possible_dishes.append(recipe_dict[item]["pretty-name"])

    # print(possible_dishes)
    return str(possible_dishes)


if __name__ == '__main__':
    app.run(host='192.168.0.106')