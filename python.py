from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_mysqldb import MySQL
from flask_mysqldb import MySQL

import MySQLdb
import bcrypt
import os 
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()
from flask_jwt_extended import create_access_token,JWTManager
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
db_host = os.getenv("HOST")
db_port = 21719
db_user = os.getenv("USER")
db_password = os.getenv("PASSWORD")
db_name = os.getenv("DB")

print(db_host,db_port,db_user,db_password,db_name)

app.config['MYSQL_HOST'] = db_host
app.config['MYSQL_PORT'] = db_port
app.config['MYSQL_USER'] = db_user
app.config['MYSQL_PASSWORD'] = db_password
app.config['MYSQL_DB'] = db_name
# f"avnadmin@mysql-15f7ba09-iitgn.g.aivencloud.com:21719/defaultdb"

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)
mysql = MySQL(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()
    
class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        print("********************************")
        print(type(data))
        print("********************************")
        
        username = data.get('username')
        password = data.get('password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        if not username or not password:
            return {'message': 'Missing username or password'}, 400
        
        user = User.query.filter_by(username=username).first()
        if user:
            return {'message': 'User already exists'}, 400
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201
    
class UserLogin(Resource):
    def post(self):
        print(request.get_json())
        data = request.get_json()
        username = data['username']
        password = data['password']
        print(username,password)
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return {'message': 'Invalid username or password'}, 401
        
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}, 200

api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')

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

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        
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
    return render_template("login.html")

@app.route('/faculty_login')
def faculty_login():
    return render_template("faculty-dashboard.html")

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


