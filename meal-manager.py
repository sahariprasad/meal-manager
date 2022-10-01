from flask import Flask, render_template, request, flash, url_for, redirect
from db_man import get_database
import json

db1 = get_database()
food_collection = db1["food"]

class Recipe:
    def __init__(self, pretty_name, mandatory_ingredients, optional_ingredients, meal_time):
        self.pretty_name = pretty_name
        self.mandatory_ingredients = mandatory_ingredients
        self.optional_ingredients = optional_ingredients
        self.meal_time = meal_time
    
    def get_document(self):
        recipe_dict = {
            "pretty_name": self.pretty_name,
            "mandatory_ingredients": self.mandatory_ingredients,
            "optional_ingredients": self.optional_ingredients,
            "meal_time": self.meal_time
        }
        return recipe_dict


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hey there! Go to /fatboy to find food!'


@app.route('/meal_manager')
def meal_manager():
    return render_template("meal_manager.html")

@app.route('/meal_manager/add_recipe', methods = ["GET", "POST"])
def add_recipe():
    if request.method == 'POST':
        new_recipe = Recipe(
            request.form["pretty_name"],
            [item.strip() for item in request.form["mandatory_ingredients"].lower().split(',')],
            [item.strip() for item in request.form["optional_ingredients"].lower().split(',')],
            [item.strip() for item in request.form.getlist("meal_time")]
        )
        food_collection.insert_one(new_recipe.get_document())
        # return redirect(url_for("meal_manager"))
        return render_template("upload_success.html")
    return render_template("add_recipe.html")


@app.route('/meal_manager/find_food', methods = ["GET", "POST"])
def find_food():
    if request.method == "POST":
        content_type = request.headers.get('Content-Type')
        possible_recipes = []
        all_recipes = list(food_collection.find().sort('pretty_name'))
        print(request.data)
        if content_type == 'application/json':
            ingredient_list = request.json
            ingredient_list = [ingredient.lower() for ingredient in ingredient_list]
        elif content_type == 'application/x-www-form-urlencoded':
            ingredient_list = [ingredient.strip() for ingredient in request.form["available_ingredients"].lower().split(',')]

        for item in all_recipes:
            if set(item["mandatory_ingredients"]).issubset(ingredient_list):
                possible_recipes.append(item["pretty_name"])
        if len(possible_recipes) == 0:
            return "You don't have anything to cook."
        else:
            return str(possible_recipes)

    return render_template("find_food.html")


@app.route('/meal_manager/upload_json', methods = ["GET", "POST"])
def upload_json():
    if request.method == "POST":
        file = request.files["file"]
        file.save(file.filename)
        file_content = open(file.filename, "r", encoding="utf-8")
        recipes_list = json.load(file_content)
        food_collection.insert_many(recipes_list, ordered=False)
        # return "{} recipes added".format(len(recipes_list))
        return render_template("upload_success.html")
    return render_template("upload_json.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 9000)
 
