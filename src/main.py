from flask import Flask, render_template, request
import sqlite3
import hashlib

app = Flask(__name__, template_folder='./templates')

def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, blood_type INTEGER, age INTEGER, weight INTEGER, location TEXT, lattitude REAL, longitude REAL, rating REAL, is_donor BIT, medical_conditions TEXT)')
    conn.commit()
    conn.close()

def create_data_entry(username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    insert_req = f'INSERT INTO users (username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);'
    data = (username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions)
    c.execute(insert_req, data)
    conn.commit()
    conn.close()

def get_data_entry(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM users WHERE id={id}')
    data = c.fetchone()
    conn.close()
    print(data)
    return data

get_data_entry(1)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        blood_type = request.form['blood_type']
        age = request.form['age']
        weight = request.form['weight']
        location = request.form['location']
        lattitude = request.form['lattitude']
        longitude = request.form['longitude']
        rating = request.form['rating']
        is_donor = request.form['is_donor']
        medical_conditions = request.form['medical_conditions']
        create_data_entry(username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions)
        return "Registered"
    elif request.method == 'GET':
        return render_template('register.html')
    return "Fuck off"

@app.route('/')
def home():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run()

create_database()