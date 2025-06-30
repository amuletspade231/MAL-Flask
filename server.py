from flask import Flask, render_template, request
from waitress import serve
import pyodbc
import csv
import io
import requests

app = Flask(__name__)

class Recipe:
  def __init__(self, name, ingredients):
    self.name = name
    self.ingredients = ingredients

SERVER = "localhost\SQLEXPRESS"
DATABASE = "GGM_MAL"
USERNAME = "DESKTOP-CTVHPLV\Amanda C"

connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes'

#list the urls of your app
@app.route('/')
@app.route('/index')

#define the contents of the index page
def index():
    try:
        connection = pyodbc.connect(connection_string)

        cursor = connection.cursor()

        #get the names of crops you can grow each season
        query = " select crop.name from crop inner join season on season_id = season.id where season.name = 'warm'"
        cursor.execute(query)
        output1 = io.StringIO()
        csv.writer(output1, quoting=csv.QUOTE_NONE).writerows(cursor)
        warm_plants = ", ".join(output1.getvalue().split())

        query = " select crop.name from crop inner join season on season_id = season.id where season.name = 'cold'"
        cursor.execute(query)
        output2 = io.StringIO()
        csv.writer(output2, quoting=csv.QUOTE_NONE).writerows(cursor)
        cold_plants = ", ".join(output2.getvalue().split())

        connection.close()

        #use dynamic html template and include query results
        return render_template('index.html', warm_plants=warm_plants, cold_plants=cold_plants)
    except Exception as e :
        print(e)
        #use static html template
        return render_template('index_static.html')

@app.route('/recipe_search')

def recipe_search():
        return render_template('recipe_search.html')

@app.route('/recipe')

def get_recipe():
    crop = request.args.get("crop")

    try:
        connection = pyodbc.connect(connection_string)

        cursor = connection.cursor()

        #get recipe names and ids that use a certain crop
        recipe_query = "select recipe.name, recipe.id from recipe inner join recipe_quantity on recipe_id = recipe.id inner join crop on crop_id = crop.id where crop.name = '" + crop + "'"
        cursor.execute(recipe_query)
        recipe_results = cursor.fetchall()

        recipes = list()
        for result in recipe_results:
            #get all ingredients for each recipe
            ingredient_query = "select crop.name from recipe inner join recipe_quantity on recipe_id = recipe.id inner join crop on crop_id = crop.id where recipe.id = " + str(result.id)
            cursor.execute(ingredient_query)
            ingredients = cursor.fetchall()
            recipes.append(Recipe(result.name, ingredients))

        connection.close()

        #use dynamic html template and include query results
        return render_template('recipe.html', recipes=recipes, crop=crop)
    except Exception as e :
        print(e)
        #use static html template
        return render_template('recipe_search.html')

if __name__ == "__main__":
    #use waitress to serve our local app
    serve(app, host="0.0.0.0", port=8000)