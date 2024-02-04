from flask import Flask, render_template, request, session, redirect
import sqlite3
import hashlib
import datetime
from user import User
import json

app = Flask(__name__, template_folder='./templates', static_folder='./assets/static')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, blood_type INTEGER, age INTEGER, weight INTEGER, location TEXT, lattitude REAL, longitude REAL, rating REAL, is_donor BIT, medical_conditions TEXT, requests TEXT, donations TEXT, amount_of_blood_left REAL, last_donation TEXT, recipient TEXT)')
    conn.commit()
    conn.close()

def create_data_entry(username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    insert_req = f'INSERT INTO users (username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions, amount_of_blood_left, last_donation, requests, donations) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    data = (username, password, email, blood_type, age, weight, location, lattitude, longitude, rating, is_donor, medical_conditions, 500, current_date, '', '')
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

def get_data_entry(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM users WHERE username=?', (username,))
    data = c.fetchone()
    conn.close()
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
        print(lattitude, longitude)
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    current_user = get_data_entry(session['username'])
    if request.method == 'POST':
        recipient = request.get_json()['recipient']
        recipient_data = get_data_entry(recipient)
        if current_user[1] in recipient_data[-5]:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute(f'UPDATE users SET recipient="{recipient}" WHERE username="{current_user[1]}"')
            conn.commit()
            conn.close()
            return json.dumps({'status': 'OK', 'data': "Connected"}), 200, {'ContentType': 'application/json'}

    users = get_all_entries()
    others_requests = list(filter(lambda x: current_user[1] in x[13], users))
    your_requests = list(filter(lambda x: x[1] in current_user[13], users))
    print(your_requests, current_user[13])
    your_requests = list(map(lambda x: list(x) + [round(User.getDistanceKm(lat1=x[8], lng1=x[9], lat2=current_user[8], lng2=current_user[9]))], your_requests))
    others_requests = list(map(lambda x: list(x) + [round(User.getDistanceKm(lat1=x[8], lng1=x[9], lat2=current_user[8], lng2=current_user[9]))], others_requests))
    accepted_user = list(filter(lambda x: x[1] in current_user[-1], users))
    being_assisted = list(filter(lambda x: current_user[1] in x[-1], users)) != []
    if accepted_user != []:
        accepted_user = accepted_user[0]
        accepted_user =  list(accepted_user) + [round(User.getDistanceKm(lat1=accepted_user[8], lng1=accepted_user[9], lat2=current_user[8], lng2=current_user[9]))]
    return render_template('requests_page.html', users=your_requests, current_user=current_user, others_requests=others_requests, accepted_requests=(accepted_user != []), accepted_user = accepted_user, being_assisted=being_assisted)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(f'SELECT * FROM users WHERE username="{username}" AND password="{password}"')
        data = c.fetchone()
        conn.close()
        print(data)
        if data:
            session['username'] = username
            print(session['username'])
            return redirect('/')
        else:
            return render_template('login.html', logged_in=False)
    elif request.method == 'GET':
        return render_template('login.html', logged_in=True)
    else:
        return "Invalid request"

@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        data = request.get_json()
        current_user = get_data_entry(data['user1'])
        receipient = get_data_entry(data['user2'])
        if current_user[13] == None or receipient[14] == None:
            current_users = data["user2"] + ","
            receipients = data["user1"] + ","
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute(f'UPDATE users SET requests="{current_users}" WHERE username="{current_user[1]}"')
            c.execute(f'UPDATE users SET donations="{receipients}" WHERE username="{receipient[1]}"')
            conn.commit()
            conn.close()
            return json.dumps({'status': 'OK', 'data': "Connected"}), 200, {'ContentType': 'application/json'}
        
        elif (data["user2"] in current_user[13] or data["user1"] in receipient[14]):
            return json.dumps({'status': 'OK', 'data': "Already connected"}), 200, {'ContentType': 'application/json'}
        else:
            current_users = current_user[13] + data["user2"] + ","
            receipients = receipient[14] + data["user1"] + ","
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute(f'UPDATE users SET requests="{current_users}" WHERE username="{current_user[1]}"')
            c.execute(f'UPDATE users SET donations="{receipients}" WHERE username="{receipient[1]}"')
            conn.commit()
            conn.close()
            return json.dumps({'status': 'OK', 'data': "Connected"}), 200, {'ContentType': 'application/json'}
    
@app.route('/disconnect', methods=['GET', 'POST'])
def disconnect():
    if request.method == 'POST':
        current_user = get_data_entry(session['username'])
        receipient = get_data_entry(current_user[-1])
        current_users = current_user[13].replace(receipient[1] + ",", "")
        receipients = receipient[14].replace(current_user[1] + ",", "")
        blood_donated = current_user[-3] - int(request.form['bloodAmount'])
        rating = current_user[10] + float(request.form['rating'])
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(f'UPDATE users SET donations="{current_users}" WHERE username="{current_user[1]}"')
        c.execute(f'UPDATE users SET requests="{receipients}" WHERE username="{receipient[1]}"')
        c.execute(f'UPDATE users SET recipient="" WHERE username="{current_user[1]}"')
        c.execute(f'UPDATE users SET amount_of_blood_left="{blood_donated}" WHERE username="{current_user[1]}"')
        c.execute(f'UPDATE users SET rating="{rating}" WHERE username="{receipient[1]}"')
        conn.commit()
        conn.close()
        return redirect('/profile')
    
    elif request.method == 'GET':
        current_user = get_data_entry(session['username'])
        receipient = get_data_entry(current_user[-1])
        if receipient != None:
            current_users = current_user[13].replace(receipient[1] + ",", "")
            receipients = receipient[14].replace(current_user[1] + ",", "")
            
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute(f'UPDATE users SET donations="{current_users}" WHERE username="{current_user[1]}"')
            c.execute(f'UPDATE users SET requests="{receipients}" WHERE username="{receipient[1]}"')
            c.execute(f'UPDATE users SET recipient="" WHERE username="{current_user[1]}"')
            conn.commit()
            conn.close()
            return redirect('/profile')

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        current_user = get_data_entry(session['username'])
        assert current_user != None
    except Exception as e:
        print(e)
        current_user = None
        return redirect('/login')
    
    users = get_all_entries()
    print(users[0])
    if request.method == 'GET':
        users = list(map(lambda x: list(x) + [round(User.getDistanceKm(lat1=x[8], lng1=x[9], lat2=current_user[8], lng2=current_user[9]))], users))
    if request.method == 'POST':
        users = list(map(lambda x: list(x) + [round(User.getDistanceKm(lat1=x[8], lng1=x[9], lat2=current_user[8], lng2=current_user[9]))], users))
        users = list(filter(lambda x: x[-1] <= int(request.form["distanceFromUser"]) and x[4] == request.form["bloodTypes"] and x[10] >= int(request.form["bloodAmount"]), users))
    users = list(filter(lambda x: x[1] not in current_user[13], users))
    users = sorted(users, key=lambda x: x[-1])
    return render_template('index.html', users = users, current_user=current_user)

try:
    print(session["username"], "you are")
except:
    print("You're not logged in")

create_database()
if __name__ == '__main__':
    app.run()
