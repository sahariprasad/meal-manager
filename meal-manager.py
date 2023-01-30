from flask import Flask, render_template, request, flash, url_for, redirect, session
from db_man import get_database
import json
import bcrypt
import pandas as pd
import openpyxl
import os

db1 = get_database()
records = db1.register
food_collection = db1["food"]

def beautify_list(list_to_convert):
    output_string = ""
    for item in list_to_convert:
        if item == list_to_convert[-1]:
            output_string += item.capitalize()
        else:
            output_string += item.capitalize() + ', '
    return output_string

class Recipe:
    def __init__(self, pretty_name, mandatory_ingredients, optional_ingredients, meal_time):
        self.pretty_name = pretty_name
        self.mandatory_ingredients = mandatory_ingredients
        self.mandatory_ingredients_pretty = beautify_list(mandatory_ingredients)
        self.optional_ingredients = optional_ingredients
        self.optional_ingredients_pretty = beautify_list(optional_ingredients)
        self.meal_time = meal_time
        self.meal_time_pretty = beautify_list(meal_time)
    
    def get_document(self):
        recipe_dict = {
            "pretty_name": self.pretty_name,
            "mandatory_ingredients": self.mandatory_ingredients,
            "optional_ingredients": self.optional_ingredients,
            "meal_time": self.meal_time
        }
        return recipe_dict


class Ingredient:
    def __init__(self, name):
        self.name = name
        self.pretty_name = name.capitalize()


def authenticate_rest(username, password):
    user_record = records.find_one({"email": username})
    user_record_email = user_record['email']
    user_record_password = user_record['password']

    if bcrypt.checkpw(password.encode('utf-8'), user_record_password):
        return True
    else:
        return False


def get_all_ingredients(username=''):
    if session:
        username = session["email"]

    filter = {"user": username}
    projection = {"mandatory_ingredients":1}
    all_mandatory_ingredients = list(food_collection.find(filter = filter, projection = projection))
    flat_list = list(set([element for innerList in [item["mandatory_ingredients"] for item in all_mandatory_ingredients] for element in innerList]))
    flat_list.sort()
    final_ingredient_list = [Ingredient(item) for item in flat_list]
    return final_ingredient_list

app = Flask(__name__)
app.secret_key = "testing"
@app.route('/', methods=["POST", "GET"])
def index():
    message = ''
    if "email" in session:
        # return render_template("find_food.html", email=session["email"])
        return redirect(url_for("find_food", user=session["email"]))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        # if user_found:
        #     message = 'There already is a user by that name'
        #     return render_template('index.html', message=message)
        if email_found:
            message = 'This username already exists, please choose another one'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']

            session["email"] = new_email
            return render_template("add_recipe.html", email=session["email"])
            return 
    return render_template('index.html')


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
    # message = 'Please login to your account'
    if "email" in session:
        return render_template("meal_manager.html", email=session["email"])

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

       
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                # return render_template("meal_manager.html", email=session["email"])
                # return render_template("find_food.html", email=session["email"])
                return redirect(url_for("find_food", user=session["email"]))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Incorrect password'
                return render_template('login.html', message=message)
        else:
            message = 'User not found'
            return render_template('login.html', message=message)
    return render_template('login.html')


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        # return render_template("login.html")
        return redirect(url_for("login"))
    else:
        return render_template('index.html')

@app.route('/meal_manager')
def meal_manager():
    return render_template("meal_manager.html", email = session["email"])

@app.route('/meal_manager/add_recipe', methods = ["GET", "POST"])
def add_recipe():
    if request.method == 'POST':
        new_recipe = Recipe(
            request.form["pretty_name"],
            [item.strip() for item in request.form["mandatory_ingredients"].lower().split(',')],
            [item.strip() for item in request.form["optional_ingredients"].lower().split(',')],
            [item.strip() for item in request.form.getlist("meal_time")]
        )
        food_collection.insert_one(dict(new_recipe.get_document(), user=session["email"]))
        # return render_template("find_food.html", user=session["email"])
        return redirect(url_for("find_food", user=session["email"]))
    return render_template("add_recipe.html")


@app.route('/meal_manager/find_food', methods = ["GET", "POST"])
def find_food():
    all_ingredients = get_all_ingredients()
    if request.method == "POST":
        content_type = request.headers.get('Content-Type')
        possible_recipes = []
        filter = {"user": session["email"]}
        all_recipes = list(food_collection.find(filter=filter).sort('pretty_name'))
        
        if content_type == 'application/json':
            ingredient_list = request.json
            ingredient_list = [ingredient.lower() for ingredient in ingredient_list]
        elif content_type == 'application/x-www-form-urlencoded':
            # ingredient_list = [ingredient.strip() for ingredient in request.form["available_ingredients"].lower().split(',')]
            ingredient_list = request.form.getlist("available_ingredients")

        for item in all_recipes:
            if set(item["mandatory_ingredients"]).issubset(ingredient_list):
                recipe_object = Recipe(item["pretty_name"], 
                                        item["mandatory_ingredients"],
                                        item["optional_ingredients"],
                                        item["meal_time"])
                possible_recipes.append(recipe_object)
        if len(possible_recipes) == 0:
            return render_template("find_food.html", no_food_alert = True, all_ingredients = all_ingredients)
        else:
            return render_template("find_food.html", recipe_list = possible_recipes, all_ingredients = all_ingredients)

    return render_template("find_food.html", all_ingredients = all_ingredients)


@app.route('/meal_manager/upload_json', methods = ["GET", "POST"])
def upload_json():
    if request.method == "POST":
        file = request.files["file"]
        file.save(file.filename)
        # file_content = open(file.filename, "r", encoding="utf-8")
        # recipes_list = json.load(file_content)
        recipe_file = pd.ExcelFile(file.filename)
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

        # for item in content_list:
        #     print(item)

        # file_out = open("test_out.json", "w", encoding='utf-8')
        # file_out.write(json.dumps(content_list))
        # file_out.close()
        recipes_list_updated = [dict(recipe, user=session["email"]) for recipe in content_list]
        food_collection.insert_many(recipes_list_updated, ordered=False)
        # return render_template("find_food.html", user=session["email"])
        return redirect(url_for("find_food", user=session["email"]))
    return render_template("upload_json.html")


@app.route('/meal_manager/rest_find_food', methods = ["GET", "POST"])
def rest_find_food():
    username = request.form.get("username")
    password = request.form.get("password")
    meal_time = request.form.get("meal_time")
    
    auth_result = authenticate_rest(username=username, password=password)

    if auth_result:
        # all_ingredients = get_all_ingredients(username=username)
        possible_recipes = []
        
        if meal_time != "":
            rest_filter = {"user": username, "meal_time": meal_time}
        else:
            rest_filter = {"user": username}

        all_recipes = list(food_collection.find(filter=rest_filter).sort('pretty_name'))
        ingredient_list_str = request.form.get("available_ingredients")
        ingredient_list = ingredient_list_str.lower().split('\r\n')
        for item in all_recipes:
            if set(item["mandatory_ingredients"]).issubset(ingredient_list):
                recipe_object = Recipe(item["pretty_name"], 
                                        item["mandatory_ingredients"],
                                        item["optional_ingredients"],
                                        item["meal_time"])
                possible_recipes.append(recipe_object)
        
        final_recipe_list = []
        for item in possible_recipes:
            final_recipe_list.append(item.pretty_name)
        return str(json.dumps(final_recipe_list))


@app.route('/meal_manager/rest_get_ingredients_to_buy', methods = ["GET", "POST"])
def rest_get_ingredients():
    username = request.form.get("username")
    password = request.form.get("password")
    recipes = request.form.get("recipes")
    current_ingredients = request.form.get("current_ingredients")
    
    auth_result = authenticate_rest(username=username, password=password)
    if auth_result:
        current_ingredient_list = current_ingredients.lower().split('\r\n')
        recipe_list = recipes.split('\r\n')
        
        mandatory_ingredients = []
        for recipe in recipe_list:
            rest_filter = {"user": username, "pretty_name": recipe}
            all_recipes = list(food_collection.find(filter=rest_filter).sort('pretty_name'))
            for item in all_recipes:
                mandatory_ingredients.extend(item["mandatory_ingredients"])

        ingredients_to_buy = []
        for ingredient in mandatory_ingredients:
            if ingredient.lower() not in current_ingredient_list:
                ingredients_to_buy.append(ingredient)
        
        return ingredients_to_buy


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 9000)
