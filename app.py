from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_mysqldb import MySQL
from mysqlclient import MySQLdb.cursors
import bcrypt
import os 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv("HOST")
app.config['MYSQL_PORT'] = int(os.getenv("PORT"))
app.config['MYSQL_USER'] = os.getenv("USER")
app.config['MYSQL_PASSWORD'] = os.getenv("PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB")

mysql = MySQL(app)

# Route for Home Page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prospective_intern', methods=['GET', 'POST'])
def prospective_intern():
    if request.method == 'POST':
        # Get all form fields
        full_name = request.form['full_name']
        mobile = request.form['mobile']
        nationality = request.form['nationality']
        phone = request.form['phone']
        email = request.form['email']
        alternate_email = request.form['alternate_email']
        permanent_city = request.form['permanent_city']
        date_of_birth = request.form['date_of_birth']
        degree = request.form['degree']
        department = request.form['department']
        college_name = request.form['college_name']
        year_of_joining = request.form['year_of_joining']
        college_city = request.form['city']
        college_state = request.form['state']
        college_country = request.form['country']
        gpa_type = request.form['gpa_type']
        gpa_value = request.form['gpa_value']
        gender = request.form['gender']
        statement_of_purpose = request.form['statement_of_purpose']
        can_complete_internship = request.form.get('can_complete_internship') == 'yes'
        faculty = request.form['faculty']
        project_code = request.form['project_code']
        # project_title = ""

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Insert into database
        cursor.execute('''
            INSERT INTO intern (
                full_name, mobile, nationality, phone, email, alternate_email,
                permanent_city, date_of_birth, degree, department, college_name,
                year_of_joining, college_city,college_state,college_country, gpa_type, gpa_value, gender,
                statement_of_purpose, can_complete_internship, faculty_id, project_code
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        ''', (
            full_name, mobile, nationality, phone, email, alternate_email,
            permanent_city, date_of_birth, degree, department, college_name,
            year_of_joining, college_city,college_state,college_country, gpa_type, gpa_value, gender,
            statement_of_purpose, can_complete_internship, faculty, project_code
        ))
        
        mysql.connection.commit()
        flash('Internship application submitted successfully!', 'success')
        return redirect(url_for('index'))

    # GET request - display form
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT faculty_id, name FROM faculty WHERE approved = 1')
    faculties = cursor.fetchall()
    return render_template('prospective_intern.html', faculties=faculties)

@app.route('/coordinator_login')
def coordinator_login():
    return render_template("coordinator_dashboard.html")


@app.route('/get_projects')
def get_projects():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    faculty_id = request.args.get('faculty_id')
    cursor.execute("SELECT project_code, project_title FROM projects WHERE faculty_id = %s", (faculty_id,))
    projects = cursor.fetchall()
    cursor.close()
    # Convert the projects data to JSON format
    return jsonify({"projects": projects}), 200
if __name__ == '__main__':
    app.run(debug=True)