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
        INSERT INTO foods (
            name, serving_size, calories, 
            total_fats, saturated_fats, carbohydrates, sugar,
            protein, calcium, fats, trans_fats, cholesterol, 
            fiber, iron, sodium
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s
        )
        """,
        (
            food['name'], food['serving_size'], food['calories'],
            food.get('total_fats', 0), food.get('saturated_fats', 0),
            food.get('carbohydrates', 0), food.get('sugar', 0),
            food.get('protein', 0), food.get('calcium', 0), 
            food.get('fats', 0), food.get('trans_fats', 0),
            food.get('cholesterol', 0), food.get('fiber', 0),
            food.get('iron', 0), food.get('sodium', 0)
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

@app.route('/add_food', methods=['POST'])
def add_food_post():
    data = request.form
    
    query = """
        INSERT INTO foods (
            name, serving_size, calories, 
            total_fats, saturated_fats, carbohydrates, sugar,
            protein, calcium, fats, trans_fats, cholesterol, 
            fiber, iron, sodium
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s
        )
    """
    
    values = (
        data['name'], data['serving_size'], data['calories'],
        data['total_fats'], data['saturated_fats'], 
        data['carbohydrates'], data['sugar'],
        data['protein'], data['calcium'], data['fats'], 
        data['trans_fats'], data['cholesterol'], data['fiber'], 
        data['iron'], data['sodium']
    )
    
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()
    return redirect(url_for('admin_panel'))

@app.route('/edit_food/<int:id>', methods=['POST'])
def edit_food(id):
    data = request.form
    
    query = """
        UPDATE foods SET 
            name = %s, serving_size = %s, calories = %s,
            total_fats = %s, saturated_fats = %s,
            carbohydrates = %s, sugar = %s,
            protein = %s, calcium = %s, fats = %s,
            trans_fats = %s, cholesterol = %s,
            fiber = %s, iron = %s, sodium = %s
        WHERE id = %s
    """
    
    values = (
        data['name'], data['serving_size'], data['calories'],
        data['total_fats'], data['saturated_fats'],
        data['carbohydrates'], data['sugar'],
        data['protein'], data['calcium'], data['fats'],
        data['trans_fats'], data['cholesterol'], data['fiber'],
        data['iron'], data['sodium'], id
    )
    
    cursor.execute(query, values)
    mysql.connection.commit()
    return redirect(url_for('admin_panel'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)