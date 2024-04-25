import mysql.connector
from datetime import date, time

def create_database(cursor):
    cursor.execute('CREATE DATABASE IF NOT EXISTS healthcare_db')
    cursor.execute('USE healthcare_db')

def create_tables(cursor):
    # ENTITIES
    # Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(50) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        middle_initial VARCHAR(1))
        ''')

    # Doctors
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INT PRIMARY KEY,
        specialty VARCHAR(255) NOT NULL,
        FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE) 
        ''')

    # Patients
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INT PRIMARY KEY,
        FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE)
        ''')
    
    # Appointments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        time TIME NOT NULL,
        doctor_id INT NOT NULL,
        patient_id INT NOT NULL,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE)
        ''')
    
    # Medications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        medication_name VARCHAR(50) NOT NULL)
        ''')
    
    # Lab Tests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lab_tests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        test_type VARCHAR(50) NOT NULL,
        result VARCHAR(255) NOT NULL,
        date DATE NOT NULL)
        ''')
    
    # Insurance
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insurance_claims (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company VARCHAR(50) NOT NULL,
        patient_id INT NOT NULL,
        appointment_id INT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON UPDATE CASCADE ON DELETE CASCADE)
        ''')
    
    # RELATIONSHIPS
    # Prescriptions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescribed_med (
        doctor_id INT NOT NULL,
        patient_id INT NOT NULL,
        med_id INT NOT NULL,
        PRIMARY KEY (doctor_id, patient_id, med_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (med_id) REFERENCES medications(id) ON UPDATE CASCADE ON DELETE CASCADE)
        ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescribed_lab (
        doctor_id INT NOT NULL,
        patient_id INT NOT NULL,
        lab_id INT NOT NULL,
        PRIMARY KEY (doctor_id, patient_id, lab_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (lab_id) REFERENCES lab_tests(id) ON UPDATE CASCADE ON DELETE CASCADE)
        ''')
    
    # MULTI-VALUED ATTRIBUTES
    # Allergies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS allergies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        allergy VARCHAR(50) NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE)
        ''')
    
def insert_sample_data(cursor):
    # Start user ID increment
    id = 1

    # List of sample doctors
    doctors = [
        ('doctor1', 'doctorpass1', 'John', 'Doe', 'S', 'Cardiology'),
        ('doctor2', 'doctorpass2', 'George', 'Brady', 'D', 'Pediatric'),
        ('doctor3', 'doctorpass3', 'Spencer', 'Peters', 'T', 'Dermatology'),
        ('doctor4', 'doctorpass4', 'Darren', 'Knowles', 'F', 'General Practice/Family Medicine'),
        ('doctor5', 'doctorpass5', 'Ali', 'Clark', 'R', 'General Practice/Family Medicine'),
        ('doctor6', 'doctorpass6', 'Hope', 'Washington', 'L', 'General Practice/Family Medicine'),
        ('doctor7', 'doctorpass7', 'Melody', 'Ingram', 'K', 'Obstetrics and Gynecology'),
        ('doctor8', 'doctorpass8', 'Joy', 'Sparks', 'O', 'Dermatology'),
        ('doctor9', 'doctorpass9', 'Marcus', 'Huang', 'S', 'Opthamology'),
        ('doctor10', 'doctorpass10', 'Alisha', 'Baxter', 'I', 'Pediatric'),
    ]

    # List of sample patients
    patients = [
        ('patient1', 'patientpass1', 'Jane', 'Doe', 'R'),
        ('patient2', 'patientpass2', 'Jennie', 'Cannon', 'F'),
        ('patient3', 'patientpass3', 'Blanca', 'Blake', 'B'),
        ('patient4', 'patientpass4', 'Tory', 'Lanez', 'T'),
        ('patient5', 'patientpass5', 'Daryl', 'Sheldon', 'W'),
        ('patient6', 'patientpass6', 'Lola', 'Espinoza', 'A'),
        ('patient7', 'patientpass7', 'Dustin', 'Bryant', 'N'),
        ('patient8', 'patientpass8', 'Lebron', 'James', 'R'),
        ('patient9', 'patientpass9', 'Kanye', 'West', 'D'),
        ('patient10', 'patientpass10', 'Aubrey', 'Graham', 'D'),
        ('patient11', 'patientpass11', 'Kendrick', 'Lamar', 'D'),
        ('patient12', 'patientpass12', 'Dina', 'Bradley', 'D'),
        ('patient13', 'patientpass13', 'Rudy', 'Harmon', 'A'),
        ('patient14', 'patientpass14', 'Cynthia', 'Denton', 'E'),
        ('patient15', 'patientpass15', 'Lonnie', 'Smith', 'I'),
        ('patient16', 'patientpass16', 'Ken', 'Webber', 'P'),
        ('patient17', 'patientpass17', 'Monique', 'Murray', 'B'),
        ('patient18', 'patientpass18', 'Leona', 'Spears', 'K'),
        ('patient19', 'patientpass19', 'Carolina', 'Greene', 'W'),
        ('patient20', 'patientpass20', 'Armando', 'Cooley', 'M'),
    ]

    # List of sample appointments
    appointments = [
        (date(2024, 5, 7), time(12, 0), 1, 11),
        (date(2024, 5, 4), time(10, 0), 1, 11),
        (date(2024, 5, 24), time(13, 0), 7, 11),
        (date(2024, 4, 27), time(10, 0), 5, 11),
        (date(2024, 5, 23), time(16, 0), 5, 12),
        (date(2024, 5, 6), time(8, 0), 5, 14),
        (date(2024, 5, 14), time(14, 0), 9, 19),
        (date(2024, 5, 4), time(10, 0), 8, 14),
        (date(2024, 5, 18), time(8, 0), 1, 15),
        (date(2024, 5, 22), time(12, 0), 2, 18),
        (date(2024, 5, 23), time(9, 0), 5, 20),
        (date(2024, 5, 9), time(11, 0), 1, 14),
        (date(2024, 5, 13), time(8, 0), 2, 13),
        (date(2024, 5, 18), time(13, 0), 6, 19),
        (date(2024, 5, 20), time(9, 0), 5, 26),
        (date(2024, 5, 7), time(12, 0), 10, 11),
        (date(2024, 5, 2), time(8, 0), 6, 18),
        (date(2024, 5, 25), time(16, 0), 7, 16),
        (date(2024, 5, 6), time(8, 0), 4, 26),
        (date(2024, 5, 11), time(12, 0), 6, 23),
        (date(2024, 5, 17), time(8, 0), 8, 17),
        (date(2024, 5, 19), time(13, 0), 3, 30),
        (date(2024, 5, 20), time(8, 0), 10, 16),
        (date(2024, 5, 8), time(15, 0), 10, 16),
        (date(2024, 4, 30), time(13, 0), 7, 30),
        (date(2024, 5, 6), time(15, 0), 8, 15),
        (date(2024, 5, 10), time(16, 0), 9, 28),
        (date(2024, 5, 5), time(11, 0), 1, 11),
        (date(2024, 5, 9), time(11, 0), 4, 12),
        (date(2024, 5, 16), time(9, 0), 8, 22),
        (date(2024, 5, 22), time(13, 0), 10, 25),
        (date(2024, 5, 21), time(14, 0), 6, 26),
        (date(2024, 4, 25), time(8, 0), 9, 14),
        (date(2024, 5, 2), time(8, 0), 9, 17),
        (date(2024, 5, 17), time(14, 0), 7, 17),
        (date(2024, 5, 13), time(12, 0), 8, 16),
        (date(2024, 5, 16), time(16, 0), 2, 20),
        (date(2024, 5, 17), time(14, 0), 10, 28),
        (date(2024, 5, 7), time(13, 0), 2, 12),
        (date(2024, 5, 13), time(12, 0), 2, 17),
        (date(2024, 5, 12), time(15, 0), 8, 29),
        (date(2024, 4, 29), time(10, 0), 2, 16),
        (date(2024, 5, 10), time(10, 0), 4, 17),
        (date(2024, 4, 29), time(13, 0), 5, 28),
        (date(2024, 5, 3), time(14, 0), 5, 25),
        (date(2024, 5, 10), time(15, 0), 9, 18),
        (date(2024, 5, 18), time(8, 0), 4, 29),
        (date(2024, 4, 25), time(9, 0), 9, 27),
        (date(2024, 5, 15), time(14, 0), 3, 19),
        (date(2024, 5, 6), time(8, 0), 8, 17)
        ]
    
    # List of sample medications
    medications = [
        ('Vitamin D',),
        ('Amoxicillin',),
        ('Lisinopril',),
        ('Ibuprofen',),
        ('Prednisone',),
        ('Alprazolam',),
        ('Amphetamine',),
        ('Atorvastatin',),
        ('Amlopidine',),
        ('Albuterol',)
    ]

    # List of sample lab tests
    lab_tests = [
        ('Blood Cholesterol', 'Normal', date(2024, 5, 8)),
        ('Blood Glucose', 'High Blood Sugar', date(2024, 5, 10)),
        ('Urinalysis', 'Normal', date(2024, 4, 29)),
        ('Pap Smear', 'Normal', date(2024, 4, 28)),
        ('Lipid Panel', 'Normal', date(2024, 5, 1))
    ]
    
    # List of sample insurance claims
    insurance = [
        ('United Healthcare', 11, 1),
        ('United Healthcare', 11, 2),
        ('Anthem', 12, 3)
    ]

    # List of sample prescriptions
    prescribed_meds = [
        (1, 11, 3),
        (8, 11, 4),
        (5, 11, 7),
        (1, 11, 9)
    ]
    prescribed_labs = [
        (1, 11, 1),
        (7, 11, 4),
        (1, 11, 2),
        (5, 11, 3),
        (5, 12, 5)
    ]

    # List of sample allergies
    allergies = [
        (11, 'Nuts'),
        (11, 'Dairy'),
        (11, 'Shellfish'),
        (12, 'Nuts'),
        (12, 'Soy')
    ]


    # Add doctors to users and doctors table and increment ID
    for doctor in doctors:
        cursor.execute('INSERT INTO users (id, username, password, first_name, last_name, middle_initial) VALUES (%s, %s, %s, %s, %s, %s)', (id, doctor[0], doctor[1], doctor[2], doctor[3], doctor[4]))
        cursor.execute('INSERT INTO doctors (id, specialty) VALUES (%s, %s)', (id, doctor[5]))
        id += 1

    # Add patients to users and patients table and increment ID
    for patient in patients:
        cursor.execute('INSERT INTO users (id, username, password, first_name, last_name, middle_initial) VALUES (%s, %s, %s, %s, %s, %s)', (id, patient[0], patient[1], patient[2], patient[3], patient[4]))
        cursor.execute('INSERT INTO patients (id) VALUES (%s)', (id,))
        id += 1

    # add all other sample data to tables
    cursor.executemany("INSERT INTO appointments (date, time, doctor_id, patient_id) VALUES (%s, %s, %s, %s)", appointments)
    cursor.executemany("INSERT INTO medications (medication_name) VALUES (%s)", medications)
    cursor.executemany("INSERT INTO lab_tests (test_type, result, date) VALUES (%s, %s, %s)", lab_tests)
    cursor.executemany("INSERT INTO insurance_claims (company, patient_id, appointment_id) VALUES (%s, %s, %s)", insurance)
    cursor.executemany("INSERT INTO prescribed_med (doctor_id, patient_id, med_id) VALUES (%s, %s, %s)", prescribed_meds)
    cursor.executemany("INSERT INTO prescribed_lab (doctor_id, patient_id, lab_id) VALUES (%s, %s, %s)", prescribed_labs)
    cursor.executemany("INSERT INTO allergies (patient_id, allergy) VALUES (%s, %s)", allergies)


def main():
    # Connect to MySQL
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='' # Replace with your own password
    )
    cursor = db.cursor()

    # Run functions to create database and tables, and then insert sample data
    try:
        create_database(cursor)

        # Uncomment this block if you need to delete/reset the rows in the database because of errors
        # cursor.execute('DELETE FROM doctors')
        # cursor.execute('DELETE FROM patients')
        # cursor.execute('DELETE FROM users')
        # cursor.execute('DELETE FROM appointments')
        # cursor.execute('DELETE FROM medications')
        # cursor.execute('DELETE FROM lab_tests')
        # cursor.execute('DELETE FROM insurance_claims')
        # cursor.execute('DELETE FROM prescribed_med')
        # cursor.execute('DELETE FROM prescribed_lab')
        # cursor.execute('DELETE FROM allergies')
        # cursor.execute('ALTER TABLE appointments AUTO_INCREMENT = 1')
        # cursor.execute('ALTER TABLE medications AUTO_INCREMENT = 1')
        # cursor.execute('ALTER TABLE lab_tests AUTO_INCREMENT = 1')
        # cursor.execute('ALTER TABLE insurance_claims AUTO_INCREMENT = 1')
        # cursor.execute('ALTER TABLE allergies AUTO_INCREMENT = 1')

        create_tables(cursor)
        insert_sample_data(cursor)
        db.commit()
    except mysql.connector.Error as err:
        print("An error occurred: {}".format(err))
        db.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    main()
