# Data Preparation and Setup
- Used MySQL Community Server 8.0.36 (https://dev.mysql.com/downloads/mysql/) and MySQL Workbench 8.0.36 (https://dev.mysql.com/downloads/workbench/)
- All data used for this application is sample data added to the database by running the create_db.py script included in the repository
- All of the data is either randomly generated or manually created by me, we do not have access to any real healthcare data so all data is not referring to any real person's information

# Application and Code
- This application is written using Python and Flask for the backend and HTML for the front end
- All the necessary libraries can be found in the requirements.txt file

# Run Instructions
- In order to run, enter in your MySQL password in the run.py file and the create_db.py file to connect to your MySQL instance where the comment says "Replace with your own password"
- Create the database by running the create_db.py file which will also enter in sample data into the DB
- You can then run the application by running the run.py file and going to the address given in the terminal
- All the logins for the doctors in the sample data are in the form of (username: doctor1) (password: doctorpass1) and if you change the number you can login as another doctor (i.e. doctor2, doctorpass2)
- Same logins for the patients (patient1, patientpass1)
- All the doctor functionality can be observed by logging in as doctor1 and all the patient functionality can be observed by logging in as patient1

# Application Images

## Login Page:
![alt text](/images/login_page)

# Doctor Pages and Functionality
## Home Page
![alt text](/images/doctor_home_page)

## Appointments Page
![alt text](/images/doctor_appointments_page)

## Patients Page
![alt text](/images/doctor_patients_page)
From here, if you click to view details for a patient it brings you to that patient's details

## Patient Details Page
![alt text](/images/doctor_patientdetails1)
![alt text](/images/doctor_patientdetails2)
Under lab tests, you can filter to only show a specific test type (i.e. only show Blood Cholesterol tests)

# Patient Pages and Functionality
## Home Page
![alt text](/images/patient_home_page)

## Appointments Page
![alt text](/images/patient_appointments_page)
On this page, you can create an appointments with one of the doctors in the database. If there is a time conflict with either the patient or the doctor, it will show an error. Otherwise, it will enter your newly created appointment into the database.

## Doctors Page
![alt text](/images/patient_doctors_page)
On this page, the average rating for each doctor is displayed which are calculated based on all ratings given by patients stored in the database. You can also give a doctor a rating here which will enter your rating into the database.

## Prescriptions Page
![alt text](/images/patient_prescriptions_page)




