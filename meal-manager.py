from flask import Flask, render_template, request, flash, url_for, redirect, session
from db_man import get_database
import json
import bcrypt

db1 = get_database()
records = db1.register
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


class Ingredient:
    def __init__(self, name):
        self.name = name
        self.pretty_name = name.capitalize()


def get_all_ingredients():
    filter = {}
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
        return render_template("meal_manager.html", email=session["email"])
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
            return render_template("meal_manager.html", email=session["email"])
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
                return render_template("meal_manager.html", email=session["email"])
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
        # return render_template("signout.html")
        return render_template("login.html")
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
        food_collection.insert_one(new_recipe.get_document())
        return render_template("upload_success.html")
    return render_template("add_recipe.html")


@app.route('/meal_manager/find_food', methods = ["GET", "POST"])
def find_food():
    if request.method == "POST":
        content_type = request.headers.get('Content-Type')
        possible_recipes = []
        filter = {"user": session["email"]}
        all_recipes = list(food_collection.find(filter=filter).sort('pretty_name'))
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
            # return "You don't have anything to cook."
            return render_template("available_recipes.html", recipe_list = ["Nothing is available"])
        else:
            # return str(possible_recipes)
            return render_template("available_recipes.html", recipe_list = possible_recipes)

    return render_template("find_food.html")


@app.route('/meal_manager/upload_json', methods = ["GET", "POST"])
def upload_json():
    if request.method == "POST":
        file = request.files["file"]
        file.save(file.filename)
        file_content = open(file.filename, "r", encoding="utf-8")
        recipes_list = json.load(file_content)
        recipes_list_updated = [dict(recipe, user=session["email"]) for recipe in recipes_list]
        food_collection.insert_many(recipes_list_updated, ordered=False)
        return render_template("upload_success.html")
    return render_template("upload_json.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 9000)
 
