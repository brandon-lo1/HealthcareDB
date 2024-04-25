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

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    # Check if logged in 
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Check if logged in user is doctor
    if session['role'] == 'doctor':
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
    
    # Check if logged in user is patient
    elif session['role'] == 'patient':
        error = None
        cursor = db.connection.cursor()

        # Get doctor information
        cursor.execute('''SELECT u.id, u.first_name, u.last_name, d.specialty 
                       FROM users u 
                       JOIN doctors d 
                       WHERE u.id = d.id
                       ''')
        doctors = cursor.fetchall()
        
        # Take in form request for creating new appointment
        if request.method == 'POST':
            doctor_id = request.form.get('doctor_id')
            date = request.form.get('date')
            time = request.form.get('time')

            # Check for existing appointments with the same doctor at the same time
            cursor.execute("""
                SELECT * FROM appointments
                WHERE doctor_id = %s AND date = %s AND time = %s
                """, (doctor_id, date, time))
            doctor_conflict = cursor.fetchone()

            # Check for existing appointments with the same patient at the same time
            cursor.execute("""
                SELECT * FROM appointments
                WHERE patient_id = %s AND date = %s AND time = %s
                """, (session['user_id'], date, time))
            patient_conflict = cursor.fetchone()

            if doctor_conflict or patient_conflict:
                error = "Appointment conflict exists. Please choose another time."
            else:
                # Insert new appointment into database
                cursor.execute("""
                    INSERT INTO appointments (doctor_id, patient_id, date, time)
                    VALUES (%s, %s, %s, %s)
                    """, (doctor_id, session['user_id'], date, time))
                db.connection.commit()
                return redirect(url_for('appointments'))
            
        # Find all future appointments
        cursor.execute("""
            SELECT u.first_name, u.last_name, a.date, a.time, IFNULL(i.company, 'Not covered') AS insurance_coverage
            FROM appointments a
            JOIN users u ON u.id = a.doctor_id
            LEFT JOIN insurance_claims i ON a.id = i.appointment_id AND a.patient_id = i.patient_id
            WHERE a.patient_id = %s AND a.date >= CURDATE()
            ORDER BY a.date, a.time
            """, (session['user_id'],))
        future_appointments = cursor.fetchall()

        # Find all past appointments
        cursor.execute("""
            SELECT u.first_name, u.last_name, a.date, a.time, IFNULL(i.company, 'Not covered') AS insurance_coverage
            FROM appointments a
            JOIN users u ON u.id = a.doctor_id
            LEFT JOIN insurance_claims i ON a.id = i.appointment_id AND a.patient_id = i.patient_id
            WHERE a.patient_id = %s AND a.date < CURDATE()
            ORDER BY a.date, a.time
            """, (session['user_id'],))
        past_appointments = cursor.fetchall()
        cursor.close()
        return render_template('patient_appointments.html', 
            future_appointments = future_appointments, 
            past_appointments = past_appointments, 
            doctors = doctors,
            error = error,
            name = session.get('name'))
        
    
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

@app.route('/patient/<int:patient_id>', methods=['GET', 'POST'])
def patient_details(patient_id):
    if 'logged_in' in session and session['role'] == 'doctor':
        test_type_filter = request.args.get('test_type_filter', None)
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
        cursor.execute("SELECT DISTINCT test_type FROM lab_tests")
        lab_test_types = cursor.fetchall()
        if test_type_filter:
            cursor.execute("""
                SELECT l.test_type, l.result, u.first_name, u.last_name
                FROM lab_tests l
                JOIN prescribed_lab p ON p.lab_id = l.id
                JOIN users u ON u.id = p.doctor_id
                WHERE p.patient_id = %s AND l.test_type = %s
                """, (patient_id, test_type_filter))
        else:
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
            lab_test_types=lab_test_types,
            insurance = insurance,
            patient_name = patient_name,
            patient_id = patient_id)
    else:
        return redirect(url_for('login'))
    
@app.route('/doctors')
def doctors():
    if 'logged_in' in session and session['role'] == 'patient':
        cursor = db.connection.cursor()
        # Get doctor information
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, d.specialty, AVG(r.rating) AS average_rating
            FROM users u
            JOIN doctors d ON u.id = d.id
            LEFT JOIN ratings r ON u.id = r.doctor_id
            GROUP BY u.id, u.first_name, u.last_name, d.specialty
            ORDER BY u.last_name, u.first_name
            ''')
        doctors = cursor.fetchall()
        cursor.close()
        return render_template('patient_doctors.html', doctors = doctors)
    else:
        return redirect(url_for('login'))

@app.route('/submit_rating/<int:doctor_id>', methods=['POST'])
def submit_rating(doctor_id):
    if 'logged_in' in session and session['role'] == 'patient':
        rating = request.form['rating']
        patient_id = session['user_id'] 
        cursor = db.connection.cursor()
        cursor.execute('''
            INSERT INTO ratings (rating, patient_id, doctor_id)
            VALUES (%s, %s, %s)
            ''', (rating, patient_id, doctor_id))
        db.connection.commit()
        cursor.close()
        return redirect(url_for('doctors'))
    else:
        return redirect(url_for('login'))
    
@app.route('/prescriptions', methods=['GET', 'POST'])
def prescriptions():
    if 'logged_in' in session and session['role'] == 'patient':
        test_type_filter = request.args.get('test_type_filter', None)
        cursor = db.connection.cursor()
        patient_id = session['user_id'] 
        # Find all medications for logged in patient
        cursor.execute("""
            SELECT m.medication_name, u.first_name, u.last_name
            FROM medications m 
            JOIN prescribed_med p ON p.med_id = m.id
            JOIN users u ON u.id = p.doctor_id
            WHERE p.patient_id = %s
            """, (patient_id,))
        medications = cursor.fetchall()

        # Get list of all lab test types
        cursor.execute("SELECT DISTINCT test_type FROM lab_tests")
        lab_test_types = cursor.fetchall()
        if test_type_filter:
            cursor.execute("""
                SELECT l.test_type, l.result, u.first_name, u.last_name
                FROM lab_tests l
                JOIN prescribed_lab p ON p.lab_id = l.id
                JOIN users u ON u.id = p.doctor_id
                WHERE p.patient_id = %s AND l.test_type = %s
                """, (patient_id, test_type_filter))
        else:
            cursor.execute("""
                SELECT l.test_type, l.result, u.first_name, u.last_name
                FROM lab_tests l 
                JOIN prescribed_lab p ON p.lab_id = l.id
                JOIN users u ON u.id = p.doctor_id
                WHERE p.patient_id = %s
                """, (patient_id,))
        labs = cursor.fetchall()
        return render_template('patient_prescriptions.html', 
            medications = medications,
            labs = labs,
            lab_test_types=lab_test_types,
            patient_id = patient_id)
    else:
        return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True)