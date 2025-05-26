# filepath: c:\Users\Joko\Documents\Coding Shit\Nutri-gauge\server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="nutrition_db"
)

def load_data():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM foods")
    return {f"food_{row['name']}": row for row in cursor.fetchall()}

def save_data(food):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO foods (name, serving_size, calories, protein, calcium, fats, trans_fats, cholesterol, carbohydrates, fiber, iron, sodium)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            food['name'], food['serving_size'], food['calories'], food['protein'], food['calcium'], food['fats'],
            food['trans_fats'], food['cholesterol'], food['carbohydrates'], food['fiber'],
            food['iron'], food['sodium']
        )
    )
    db.commit()

def delete_data(food_name):
    cursor = db.cursor()
    cursor.execute("DELETE FROM foods WHERE name = %s", (food_name,))
    db.commit()

@app.route("/foods", methods=["GET"])
def get_foods():
    return jsonify(load_data())

@app.route("/foods", methods=["POST"])
def add_food():
    food = request.json
    save_data(food)
    return jsonify(food), 201

@app.route("/foods/<food_name>", methods=["DELETE"])
def delete_food(food_name):
    delete_data(food_name)
    return "", 204

@app.route('/admin/add_food', methods=['GET', 'POST'])
def admin_add_food():
    if request.method == 'POST':
        name = request.form['name']
        serving_size = request.form['serving_size']  # FROM BREN
        calories = request.form['calories']
        food = {
            'name': name,
            'serving_size': serving_size,  # FROM BREN
            'calories': calories,
        }
        save_data(food)  
        return jsonify(food), 201
    return '''
        <form method="post">
            Name: <input type="text" name="name"><br>
            Serving Size: <input type="text" name="serving_size"><br>
            Calories: <input type="text" name="calories"><br>
            <!-- ...other fields... -->
            <input type="submit" value="Add Food">
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)