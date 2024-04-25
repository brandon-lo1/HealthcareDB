import mysql.connector

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
        test_type VARCHAR(50) NOT NULL),
        result VARCHAR(255) NOT NULL,
        date DATE NOT NULL)
        ''')
    
    # Insurance
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insurance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        
        company VARCHAR(50) NOT NULL)
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
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE
        FOREIGN KEY (med_id) REFERENCES medications(id) ON UPDATE CASCADE ON DELETE CASCADE)
        ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescribed_lab (
        doctor_id INT NOT NULL,
        patient_id INT NOT NULL,
        lab_id INT NOT NULL,
        PRIMARY KEY (doctor_id, patient_id, lab_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON UPDATE CASCADE ON DELETE CASCADE
        FOREIGN KEY (lab_id) REFERENCES lab_tests(id) ON UPDATE CASCADE ON DELETE CASCADE)
        ''')
    
    # Insurance Claims



def insert_sample_data(cursor):
    # Start ID increment
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
        ('patient4', 'patientpass4', 'Brandon', 'Lo', 'S'),
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


def main():
    # Connect to MySQL
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd=''  # Replace with your own password
    )
    cursor = db.cursor()

    # Run functions to create database and tables, and then insert sample data
    try:
        create_database(cursor)
        cursor.execute('DELETE FROM doctors')
        cursor.execute('DELETE FROM patients')
        cursor.execute('DELETE FROM users')
        
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
