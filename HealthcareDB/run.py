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
        # Gets login and user information
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
    # Return different home pages for doctors and patients
    if session['role'] == 'doctor':
        return render_template('doctor_home.html', name = session.get('name'))
    elif session['role'] == 'patient':
        return render_template('patient_home.html', name = session.get('name'))
    return redirect(url_for('login'))

@app.route('/appointments')
def appointments():
    if 'logged_in' in session and session['role'] == 'doctor':
        cursor = db.connection.cursor()
        # Find all future appointments
        cursor.execute("""
            SELECT u.first_name, u.last_name, a.date, a.time 
            FROM appointments a
            JOIN users u ON u.id = a.patient_id
            WHERE a.doctor_id = %s AND a.date >= CURDATE()
            ORDER BY a.date, a.time
            """, (session['user_id'],))
        future_appointments = cursor.fetchall()

        # Find all past appointments
        cursor.execute("""
            SELECT u.first_name, u.last_name, a.date, a.time 
            FROM appointments a
            JOIN users u ON u.id = a.patient_id
            WHERE a.doctor_id = %s AND a.date < CURDATE()
            ORDER BY a.date, a.time
            """, (session['user_id'],))
        past_appointments = cursor.fetchall()
        cursor.close()
        return render_template('doctor_appointments.html', 
            future_appointments = future_appointments, 
            past_appointments = past_appointments, 
            name = session.get('name'))
    elif 'logged_in' in session and session['role'] == 'patient':
        pass
    else:
        return redirect(url_for('login'))
    
@app.route('/patients')
def patients():
    if 'logged_in' in session and session['role'] == 'doctor':
        cursor = db.connection.cursor()
        # Find all distinct patients that the logged in doctor has an appointment with
        cursor.execute("""
            SELECT DISTINCT u.id, u.first_name, u.last_name
            FROM users u
            JOIN appointments a ON u.id = a.patient_id
            WHERE a.doctor_id = %s
            ORDER BY u.last_name, u.first_name
            """, (session['user_id'],))
        patients_data = cursor.fetchall()
        cursor.close()
        return render_template('doctor_patients.html', patients = patients_data)
    else:
        return redirect(url_for('login'))

@app.route('/patient/<int:patient_id>')
def patient_details(patient_id):
    if 'logged_in' in session and session['role'] == 'doctor':
        cursor = db.connection.cursor()
        # Find patient name
        cursor.execute('SELECT first_name, last_name FROM users WHERE id = %s', (patient_id,))
        patient_name = cursor.fetchone()

        # Find past appointments for this patient
        cursor.execute("""
            SELECT u.first_name, u.last_name, a.date, a.time 
            FROM appointments a 
            JOIN users u ON u.id = a.doctor_id
            WHERE a.patient_id = %s AND a.date < CURDATE()
            ORDER BY a.date, a.time
            """, (patient_id,))
        past_visits = cursor.fetchall()

        # Find future appointments for this patient
        cursor.execute("""
            SELECT u.first_name, u.last_name, a.date, a.time 
            FROM appointments a 
            JOIN users u ON u.id = a.doctor_id
            WHERE a.patient_id = %s AND a.date >= CURDATE()
            ORDER BY a.date, a.time
            """, (patient_id,))
        future_visits = cursor.fetchall()

        # Find all medications this patient is taking and doctor who prescribed
        cursor.execute("""
            SELECT m.medication_name, u.first_name, u.last_name
            FROM medications m 
            JOIN prescribed_med p ON p.med_id = m.id
            JOIN users u ON u.id = p.doctor_id
            WHERE p.patient_id = %s
            """, (patient_id,))
        medications = cursor.fetchall()

        # Find all allergies for this patient
        cursor.execute("""
            SELECT a.allergy
            FROM allergies a
            WHERE a.patient_id = %s
            """, (patient_id,))
        allergies = cursor.fetchall()

        # Find all lab tests for this patient
        cursor.execute("""
            SELECT l.test_type, l.result, u.first_name, u.last_name
            FROM lab_tests l 
            JOIN prescribed_lab p ON p.lab_id = l.id
            JOIN users u ON u.id = p.doctor_id
            WHERE p.patient_id = %s
            """, (patient_id,))
        labs = cursor.fetchall()

        # Find all insurance claims for this patient
        cursor.execute("""
            SELECT i.company, a.date, u.first_name, u.last_name
            FROM insurance_claims i
            JOIN appointments a ON a.id = i.appointment_id
            JOIN users u ON u.id = a.doctor_id
            WHERE i.patient_id = %s
            """, (patient_id,))
        insurance = cursor.fetchall()
        cursor.close()
        return render_template('doctor_patientdetails.html', 
            past_visits = past_visits, 
            future_visits = future_visits,
            medications = medications,
            allergies = allergies,
            labs = labs,
            insurance = insurance,
            patient_name = patient_name,
            patient_id = patient_id)
    else:
        return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True)