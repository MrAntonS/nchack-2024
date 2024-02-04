from flask import Flask, render_template, request, session
import sqlite3
import hashlib
from user import User

app = Flask(__name__, template_folder='./templates')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, blood_type INTEGER, age INTEGER, weight INTEGER, location TEXT, lattitude REAL, longitude REAL, rating REAL, is_donor BIT, medical_conditions TEXT, requests TEXT, donations TEXT)')
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

def check_username(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM users WHERE username="{username}"')
    data = c.fetchone()
    conn.close()
    if data:
        return False
    else:
        return True

def get_data_entry(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM users WHERE id={id}')
    data = c.fetchone()
    conn.close()
    print(data)
    return data


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        username_is_used = check_username(username)
        if not username_is_used:
            return render_template('register.html', name_used="Username is already in use")
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        email = request.form['email']
        blood_type = request.form['blood-type']
        age = request.form['age']
        weight = request.form['weight']
        location = request.form['location']
        medical_conditions = request.form['medical-conditions']
        lattitude, longitude = User.lngLat(location, User.API_KEY)
        create_data_entry(username, password, email, blood_type, age, weight, location, lattitude, longitude, 0, 0, medical_conditions)
        session['username'] = username
        return "Registered"
    elif request.method == 'GET':
        return render_template('register.html')
    else:
        return "Invalid request"
    
def get_all_entries():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    conn.close()
    return data

@app.route('/profile')
def profile():
    return render_template('requests_page.html')

@app.route('/')
def home():
    users = get_all_entries()
    print(users)
    return render_template('frontend.html', users = [["asdas"]])

try:
    print(session["username"], "you are")
except:
    print("You're not logged in")


if __name__ == '__main__':
    app.run()

create_database()