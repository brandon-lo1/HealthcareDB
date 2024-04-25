from flask import Flask, render_template, url_for, request, session, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' # Replace with your own password
app.config['MYSQL_DB'] = 'healthcare_db'
db = MySQL(app)

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.connection.cursor()
        cursor.execute("SELECT id, username, password, first_name, last_name FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and user[2] == password:
            user_id = user[0]
            # Check if the user is a doctor
            cursor.execute("SELECT * FROM doctors WHERE id = %s", (user_id,))
            if cursor.fetchone():
                role = 'doctor'
            else:
                # If not a doctor, check if the user is a patient
                cursor.execute("SELECT * FROM patients WHERE id = %s", (user_id,))
                if cursor.fetchone():
                    role = 'patient'
                else:
                    role = 'undefined'

            # Store session info
            session['logged_in'] = True
            session['user_id'] = user_id
            session['username'] = username
            session['role'] = role
            session['name'] = user[3] + ' ' + user[4]
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error = error)

@app.route('/home')
def home():
    if session['role'] == 'doctor':
        return render_template('doctor_home.html', name = session.get('name'))
    elif session['role'] == 'patient':
        return render_template('patient_home.html', name = session.get('name'))
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)