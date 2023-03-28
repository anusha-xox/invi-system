from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
import pymysql
import cryptography
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from form_data import *
## for graph
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
import run as r
## for idcard
# from pyzbar import pyzbar
# import cv2

# cursor,connection = None,None
# try:
#     connection = mysql.connector.connect(host="localhost",
#                                          database="SEE_INV_withflask",
#                                          user="root",
#                                          password="root@123")
#     if connection.is_connected():
#         db_Info = connection.get_server_info()
#         print("Connected to MySQL Server version ", db_Info)
#         cursor = connection.cursor(buffered=True)
#         cursor.execute("select database();")
#         record = cursor.fetchone()
#         print("You're connected to database: ", record)
# except Error as e:
#     print("Error while connecting to MySQL", e)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invi-system.db'
engine = create_engine('mysql+pymysql://sql12609170:XR9CRf2TYY@sql12.freesqldatabase.com/sql12609170')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql12609170:XR9CRf2TYY@sql12.freesqldatabase.com/sql12609170'
#

# app.config['SQLALCHEMY_BINDS'] = {'faculty': 'sqlite:///faculty.db',
#                                   'subject': 'sqlite:///subject.db',
#                                   'admin': 'sqlite:///admin.db',
#                                   'departments': 'sqlite:///departments.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

with engine.connect() as con:
    # con.execute("CREATE DATABASE IF NOT EXISTS SEE_INV_withflask")
    # con.execute("USE SEE_INV_withflask")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `user` (`id` int NOT NULL AUTO_INCREMENT,`email` varchar(100) DEFAULT NULL,`password` varchar(100) DEFAULT NULL,`username` varchar(1000) DEFAULT NULL,PRIMARY KEY (`id`),UNIQUE KEY `email` (`email`))")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `department` (`dept_id` varchar(250) NOT NULL,`dept_name` varchar(250) NOT NULL,`floors` int NOT NULL,PRIMARY KEY (`dept_id`),UNIQUE KEY `dept_name` (`dept_name`))")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `classroom` (   `classroom_id` varchar(250) NOT NULL,   `capacity` int NOT NULL,   `dept_id` varchar(250) NOT NULL,   PRIMARY KEY (`classroom_id`,`dept_id`),   KEY `dept_id` (`dept_id`),   CONSTRAINT `classroom_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `faculty` (   `faculty_id` varchar(10) NOT NULL,   `f_name` varchar(250) NOT NULL,   `m_name` varchar(250) NOT NULL,   `l_name` varchar(250) NOT NULL,   `email` varchar(250) NOT NULL,   `phone_no` varchar(10) NOT NULL,   `group_id` varchar(250) NOT NULL,   `invig_count` int NOT NULL,   `special_count` int NOT NULL,   `dept_id` varchar(250) NOT NULL,   PRIMARY KEY (`faculty_id`,`dept_id`),   UNIQUE KEY `email` (`email`),   UNIQUE KEY `phone_no` (`phone_no`),   KEY `dept_id` (`dept_id`),   CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `subject` (   `subject_id` varchar(250) NOT NULL,   `subject_name` varchar(250) NOT NULL,   `subject_duration` varchar(15) NOT NULL,   PRIMARY KEY (`subject_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `exam` (   `academic_year` varchar(4) NOT NULL,   `exam_type` varchar(15) NOT NULL,   PRIMARY KEY (`academic_year`,`exam_type`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `enrolled` (   `Academic_Year` varchar(4) NOT NULL,   `Exam_Type` varchar(20) NOT NULL,   `Subject_ID` varchar(10) NOT NULL,   `students_enrolled` int DEFAULT NULL,   PRIMARY KEY (`Academic_Year`,`Exam_Type`,`Subject_ID`),   KEY `Subject_ID` (`Subject_ID`),   CONSTRAINT `enrolled_ibfk_1` FOREIGN KEY (`Academic_Year`, `Exam_Type`) REFERENCES `exam` (`academic_year`, `exam_type`) ON DELETE CASCADE,   CONSTRAINT `enrolled_ibfk_2` FOREIGN KEY (`Subject_ID`) REFERENCES `subject` (`subject_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `invigilates` (   `faculty_id` varchar(10) NOT NULL,   `academic_year` varchar(4) NOT NULL,   `exam_type` varchar(15) NOT NULL,   `classroom_id` varchar(10) NOT NULL,   `department_id` varchar(10) NOT NULL,   `subject_id` varchar(10) NOT NULL,   PRIMARY KEY (`faculty_id`,`academic_year`,`exam_type`,`classroom_id`,`department_id`,`subject_id`),   KEY `academic_year` (`academic_year`,`exam_type`),   KEY `classroom_id` (`classroom_id`),   KEY `department_id` (`department_id`),   KEY `subject_id` (`subject_id`),   CONSTRAINT `invigilates_ibfk_1` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`),   CONSTRAINT `invigilates_ibfk_2` FOREIGN KEY (`academic_year`, `exam_type`) REFERENCES `exam` (`academic_year`, `exam_type`),   CONSTRAINT `invigilates_ibfk_3` FOREIGN KEY(`classroom_id`) REFERENCES `classroom` (`classroom_id`),   CONSTRAINT `invigilates_ibfk_4` FOREIGN KEY (`department_id`) REFERENCES `department` (`dept_id`),   CONSTRAINT `invigilates_ibfk_5` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `student` (   `student_id` varchar(12) NOT NULL,   `st_f_name` varchar(50) DEFAULT NULL,   `st_l_name` varchar(50) DEFAULT NULL,   `academic_year` varchar(4) NOT NULL,   `exam_type` varchar(15) NOT NULL,   `subject_id` varchar(10) NOT NULL,   PRIMARY KEY (`student_id`,`academic_year`,`exam_type`,`subject_id`),   KEY `academic_year` (`academic_year`,`exam_type`),   KEY `subject_id` (`subject_id`),   CONSTRAINT `student_ibfk_1` FOREIGN KEY (`academic_year`, `exam_type`) REFERENCES `exam` (`academic_year`, `exam_type`),   CONSTRAINT `student_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `has_exam` (   `academic_year` varchar(4) NOT NULL,   `exam_type` varchar(15) NOT NULL,   `subject_id` varchar(10) NOT NULL,   `required_invigilators` int DEFAULT NULL,   `exam_date` date DEFAULT NULL,   PRIMARY KEY (`academic_year`,`exam_type`,`subject_id`),   KEY `subject_id` (`subject_id`),   CONSTRAINT `has_exam_ibfk_1` FOREIGN KEY (`academic_year`, `exam_type`) REFERENCES `exam` (`academic_year`, `exam_type`),   CONSTRAINT `has_exam_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`) )")
    con.execute(
        "CREATE TABLE IF NOT EXISTS `assigned_classrooms` (   `classroom_id` varchar(10) NOT NULL,   `subject_id` varchar(10) NOT NULL,   `exam_type` varchar(15) NOT NULL,   `academic_year` varchar(4) NOT NULL,   `department_id` varchar(10) NOT NULL,   PRIMARY KEY (`classroom_id`,`subject_id`,`exam_type`,`academic_year`,`department_id`),   KEY `subject_id` (`subject_id`),   KEY `academic_year` (`academic_year`,`exam_type`),   KEY `department_id` (`department_id`),   CONSTRAINT `assigned_classrooms_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classroom` (`classroom_id`),   CONSTRAINT `assigned_classrooms_ibfk_2`FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`),   CONSTRAINT `assigned_classrooms_ibfk_3` FOREIGN KEY (`academic_year`, `exam_type`) REFERENCES `exam` (`academic_year`, `exam_type`),   CONSTRAINT `assigned_classrooms_ibfk_4` FOREIGN KEY (`department_id`) REFERENCES `department` (`dept_id`) )")


# def draw_barcode(decoded, image):
#     image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top),
#                           (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
#                           color=(0, 255, 0),
#                           thickness=5)
#     return image


# def gen():
#     camera = cv2.VideoCapture(0)
#
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             decoded_objects = pyzbar.decode(frame)
#             for obj in decoded_objects:
#                 # draw the barcode
#                 print("detected barcode:", obj)
#                 image = draw_barcode(obj, frame)
#                 global data_barcode
#                 global type_barcode
#                 type_barcode = obj.type
#                 data_barcode = obj.data
#                 str1 = obj.data.decode('UTF-8')
#                 data_barcode = str1
#                 # print barcode type & data
#                 print("Type:", obj.type)
#                 print("Data:", obj.data)
#                 print()
#
#             ret, buffer = cv2.imencode(".jpg", frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))


class Department(db.Model):
    # __bind_key__ = 'departments'
    dept_id = db.Column(db.String(10), primary_key=True)
    dept_name = db.Column(db.String(100), unique=True, nullable=False)
    floors = db.Column(db.Integer, unique=False, nullable=False)


class Classroom(db.Model):
    # __bind_key__ = 'classroom'
    classroom_id = db.Column(db.String(10), primary_key=True)
    capacity = db.Column(db.Integer, unique=False, nullable=False)
    dept_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'), primary_key=True)


class Exam(db.Model):
    # __bind_key__ = 'exam'
    academic_year = db.Column(db.String(4), primary_key=True, nullable=False)
    exam_type = db.Column(db.String(15), primary_key=True, nullable=False)


class Faculty(db.Model):
    # __bind_key__ = 'faculty'
    faculty_id = db.Column(db.String(10), primary_key=True)
    f_name = db.Column(db.String(100), unique=False, nullable=False)
    m_name = db.Column(db.String(100), unique=False, nullable=False)
    l_name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(10), unique=True, nullable=False)
    group_id = db.Column(db.String(10), unique=False, nullable=False)
    invig_count = db.Column(db.Integer, unique=False, nullable=False)
    special_count = db.Column(db.Integer, unique=False, nullable=False)
    dept_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'), primary_key=True)


class Subject(db.Model):
    # __bind_key__ = 'subject'
    subject_id = db.Column(db.String(10), primary_key=True)
    subject_name = db.Column(db.String(100), unique=False, nullable=False)
    subject_duration = db.Column(db.String(15), unique=False, nullable=False)


class Enrolled(db.Model):
    #  __bind_key__ = 'enrolled'
    academic_year = db.Column(db.String(4), db.ForeignKey('exam.academic_year'), primary_key=True)
    exam_type = db.Column(db.String(15), db.ForeignKey('exam.exam_type'), primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.subject_id'), primary_key=True)
    students_enrolled = db.Column(db.Integer, unique=False, nullable=False)


class Invigilates(db.Model):
    # __bind_key__ = 'invigilation'
    faculty_id = db.Column(db.String(10), db.ForeignKey('faculty.faculty_id'), primary_key=True)
    academic_year = db.Column(db.String(4), db.ForeignKey('exam.academic_year'), primary_key=True)
    exam_type = db.Column(db.String(15), db.ForeignKey('exam.exam_type'), primary_key=True)
    classroom_id = db.Column(db.String(10), db.ForeignKey('classroom.classroom_id'), primary_key=True)
    department_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'), primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.subject_id'), primary_key=True)


class Has_exam(db.Model):
    # __bind_key__ = 'has_exam'
    academic_year = db.Column(db.String(4), db.ForeignKey('exam.academic_year'), primary_key=True)
    exam_type = db.Column(db.String(15), db.ForeignKey('exam.exam_type'), primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.subject_id'), primary_key=True)
    required_invigilators = db.Column(db.Integer, unique=False, nullable=True)
    exam_date = db.Column(db.Date, unique=False, nullable=True)


class Assigned_classrooms(db.Model):
    # __bind_key__ = 'assigned_classrooms'
    classroom_id = db.Column(db.String(10), db.ForeignKey('classroom.classroom_id'), primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.subject_id'), primary_key=True)
    exam_type = db.Column(db.String(15), db.ForeignKey('exam.exam_type'), primary_key=True)
    academic_year = db.Column(db.String(4), db.ForeignKey('exam.academic_year'), primary_key=True)
    department_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'), primary_key=True)


# class Admin(db.Model):
#     # __bind_key__ = 'inviDuty'
#     entry_id = db.Column(db.Integer, primary_key=True)
#     fac_id = db.Column(db.Integer, unique=False, nullable=False)
#     group_id = db.Column(db.String(250), unique=False, nullable=False)
#     dept_id = db.Column(db.String(250), unique=False, nullable=False)
#     date = db.Column(db.String(250), unique=False, nullable=False)
#     timeslot = db.Column(db.String(250), unique=False, nullable=False)
#     exam_type = db.Column(db.String(250), unique=False, nullable=False)
#     exam_year = db.Column(db.String(250), unique=False, nullable=False)
#     # faculty_role = db.Column(db.String(250), unique=False, nullable=False)
#     subject_code = db.Column(db.String(250), unique=False, nullable=False)
#     invigilators = db.relationship("Faculty", backref="admin")


# class Departments(db.Model):
#     dept_id = db.Column(db.String(250), primary_key=True)
#     dept_name = db.Column(db.String(250), unique=True, nullable=True)

class Student(db.Model):
    # _bind_key_ = 'student'
    student_id = db.Column(db.String(10), primary_key=True)
    st_f_name = db.Column(db.String(50), unique=False, nullable=False)
    st_l_name = db.Column(db.String(50), unique=False, nullable=False)
    academic_year = db.Column(db.String(4), db.ForeignKey('exam.academic_year'), primary_key=True)
    exam_type = db.Column(db.String(15), db.ForeignKey('exam.exam_type'), primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.subject_id'), primary_key=True)


class SwappingTable(db.Model):
    swap_id = db.Column(db.Integer, primary_key=True)
    curr_fac_id = db.Column(db.Integer, unique=False, nullable=False)
    other_fac_id = db.Column(db.Integer, unique=False, nullable=False)
    old_date = db.Column(db.String(250), unique=False, nullable=False)
    new_date = db.Column(db.String(250), unique=False, nullable=False)
    old_time = db.Column(db.String(250), unique=False, nullable=False)
    new_time = db.Column(db.String(250), unique=False, nullable=False)
    old_exam_type = db.Column(db.String(250), unique=False, nullable=False)
    new_exam_type = db.Column(db.String(250), unique=False, nullable=False)
    old_exam_year = db.Column(db.String(250), unique=False, nullable=False)
    new_exam_year = db.Column(db.String(250), unique=False, nullable=False)
    old_subject_code = db.Column(db.String(250), unique=False, nullable=False)
    new_subject_code = db.Column(db.String(250), unique=False, nullable=False)


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect(url_for('register'))
    # return render_template("admin-home.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        display_name = form.username.data
        default_email = form.email.data
        new_user = User(
            username=display_name,
            email=default_email,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('add_faculty', display_name=display_name, default_email=default_email))
    return render_template("enter.html", form=form, title_given="Register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if email == 'admin@email.com' and password == 'admin':
            return redirect(url_for('admin'))
        elif not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(email=email).first()
            if check_password_hash(user.password, password):
                login_user(user)
                # return redirect(url_for('add_faculty', display_name=user.username))
                for f in Faculty.query.all():
                    if user.email == f.email:
                        # return redirect(url_for('add_faculty', display_name=user.username))
                        return redirect(url_for("faculty_dashboard", faculty_id=f.faculty_id, dept_id=f.dept_id))
                    # else:
                    #     return redirect(url_for('add_faculty', display_name=user.username, default_email=user.email))
    return render_template('enter.html', form=form, title_given="Login")


@app.route('/add-faculty', methods=["GET", "POST"])
def add_faculty():
    display_name = request.args.get("display_name")
    default_email = request.args.get("default_email")
    form = FacultyForm(
        email=default_email
    )
    if form.validate_on_submit():
        new_faculty = Faculty(
            faculty_id=form.faculty_id.data,
            email=form.email.data,
            f_name=form.f_name.data,
            m_name=form.m_name.data,
            l_name=form.l_name.data,
            phone_no=form.phone_no.data,
            group_id=0,
            invig_count=0,
            special_count=0,
            dept_id=str(form.dept_id.data),
        )
        db.session.add(new_faculty)
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template("add_details.html", form=form, display_name=display_name)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    a = Assigned_classrooms.query.all()
    c = Classroom.query.all()
    d = Department.query.all()
    e = Enrolled.query.all()
    ex = Exam.query.all()
    f = Faculty.query.all()
    he = Has_exam.query.all()
    i = Invigilates.query.all()
    s = Student.query.all()
    su = Subject.query.all()
    ADMIN_OPTIONS = [
        "Generate Invigilator Report",
        "Generate Department Report",
        "Generate Duty Report",
        "Give Invigilator Group",
        "View Swap Requests",
        "No of Faculties vs Department Plot",
        "Invigilators vs Invigilation Count Plot",
        "Assign Classroom",
        "Add Exam Type",
        "Add Date to Exam",
    ]
    ADMIN_LINKS = [
        url_for('view_faculties'),
        url_for('view_faculty_dept'),
        url_for("view_invi_report"),
        url_for('admin_assign_group'),
        url_for("view_swap_requests"),
        url_for("plot"),
        url_for("admin_algo_plot"),
        url_for('admin_assign_classroom'),
        url_for('admin_add_exam'),
        url_for('admin_add_exam_date')
    ]
    if not (len(a) == 0 or len(c) == 0 or len(d) == 0 or len(e) == 0 or len(ex) == 0 or len(f) == 0 or len(
            he) == 0 or len(i) == 0 or len(s) == 0 or len(su) == 0):
        ADMIN_OPTIONS.append("Allocate Invigilator")
        ADMIN_LINKS.append(url_for('allocate_invigilator'))
    return render_template(
        "grid.html",
        title="Admin",
        grid_options=ADMIN_OPTIONS,
        grid_links=ADMIN_LINKS,
        grid_no=len(ADMIN_OPTIONS)
    )


@app.route("/faculty-home", methods=['GET', 'POST'])
def faculty_dashboard():
    faculty_id = request.args.get("faculty_id")
    dept_id = request.args.get("dept_id")
    current_faculty = Faculty.query.filter_by(faculty_id=faculty_id).filter_by(dept_id=dept_id).first()
    if current_faculty:
        FACULTY_OPTIONS = [
            "Edit Profile",
            "View Profile",
            "Generate Duty Report",
            "Request Swap from Admin",
        ]
        FACULTY_LINKS = [
            url_for('edit_profile', faculty_id=current_faculty.faculty_id, dept_id=current_faculty.dept_id),
            url_for('view_profile', faculty_id=current_faculty.faculty_id, dept_id=current_faculty.dept_id),
            url_for("view_invi_report"),
            url_for("swap_request", faculty_id=current_faculty.faculty_id, dept_id=current_faculty.dept_id)]
        return render_template(
            "grid.html",
            title=current_faculty.f_name + " " + current_faculty.l_name,
            grid_options=FACULTY_OPTIONS,
            grid_links=FACULTY_LINKS,
            grid_no=len(FACULTY_OPTIONS),
        )


@app.route("/faculty-home/edit", methods=['GET', 'POST'])
def edit_profile():
    faculty_id = request.args.get("faculty_id")
    dept_id = request.args.get("dept_id")
    current_faculty = Faculty.query.filter_by(faculty_id=faculty_id).filter_by(dept_id=dept_id).first()
    if current_faculty:
        form = FacultyForm(
            faculty_id=current_faculty.faculty_id,
            email=current_faculty.email,
            f_name=current_faculty.f_name,
            m_name=current_faculty.m_name,
            l_name=current_faculty.l_name,
            phone_no=current_faculty.phone_no,
            dept_id=current_faculty.dept_id,
        )
        if form.validate_on_submit():
            current_faculty.email = form.email.data
            current_faculty.f_name = form.f_name.data
            current_faculty.m_name = form.fac_mname.data
            current_faculty.l_name = form.fac_lname.data
            current_faculty.phone_no = form.phone_no.data
            current_faculty.dept_id = form.dept_id.data
            db.session.commit()
            new_fac_id = form.faculty_id.data
            new_dept_id = form.dept_id.data
            return redirect(url_for("faculty_dashboard", faculty_id=new_fac_id, dept_id=new_dept_id))
        return render_template("add_details.html", form=form, display_name=current_faculty.f_name)


@app.route("/faculty-home/view")
def view_profile():
    faculty_id = request.args.get("faculty_id")
    dept_id = request.args.get("dept_id")
    current_faculty = Faculty.query.filter_by(faculty_id=faculty_id).filter_by(dept_id=dept_id).first()
    heading = f"{current_faculty.f_name} {current_faculty.m_name} {current_faculty.l_name}'s Saved Details"
    return render_template("faculty_details.html", cf=current_faculty, table_heading=heading)


@app.route("/faculty-home/swap-request", methods=['GET', 'POST'])
def swap_request():
    faculty_id = request.args.get("faculty_id")
    dept_id = request.args.get("dept_id")
    current_faculty = Faculty.query.filter_by(faculty_id=faculty_id).filter_by(dept_id=dept_id).first()
    if current_faculty:
        form = SwapRequestForm(
            cur_fac_id=current_faculty.faculty_id,
        )
        if form.validate_on_submit():
            new_record = SwappingTable(
                curr_fac_id=form.curr_fac_id.data,
                other_fac_id=form.other_fac_id.data,
                old_date=form.old_date.data,
                new_date=form.new_date.data,
                old_time=form.old_time.data,
                new_time=form.new_time.data,
                old_exam_type=form.old_exam_type.data,
                new_exam_type=form.new_exam_type.data,
                old_exam_year=form.old_exam_year.data,
                new_exam_year=form.new_exam_year.data,
                old_subject_code=form.old_subject_code.data,
                new_subject_code=form.new_subject_code.data,
            )
            db.session.add(new_record)
            db.session.commit()
            curr_fac_id = int(form.curr_fac_id.data)
            return redirect(url_for("faculty_dashboard", fac_id=curr_fac_id))
        return render_template("add_details.html", form=form, display_name=current_faculty.f_name)


@app.route('/admin/assign-group', methods=['GET', 'POST'])
def admin_assign_group():
    form = AdminForm()
    if form.validate_on_submit():
        faculty_id = form.faculty_id.data
        group_id = form.group_id.data
        dept_id = form.dept_id.data
        faculty_to_edit = Faculty.query.filter_by(faculty_id=faculty_id).first()
        if faculty_to_edit:
            faculty_to_edit.group_id = group_id
            with engine.connect() as con:
                con.execute("UPDATE faculty SET group_id = %s WHERE faculty_id = %s AND dept_id = %s", group_id,
                            faculty_id, dept_id)
            return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin! Add/Update Faculty details below.")


@app.route('/admin/assign-classroom', methods=['GET', 'POST'])
def admin_assign_classroom():
    form = ClassroomForm()
    if form.validate_on_submit():
        new_classroom = Classroom(
            classroom_id=form.classroom_id.data,
            capacity=form.capacity.data,
            dept_id=form.dept_id.data
        )
        db.session.add(new_classroom)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin! Add Classroom details below.")


@app.route('/admin/add-exam-type', methods=['GET', 'POST'])
def admin_add_exam():
    form = ExamTypeForm()
    if form.validate_on_submit():
        new_exam_type = Exam(
            academic_year=form.academic_year.data,
            exam_type=form.exam_type.data
        )
        db.session.add(new_exam_type)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin! Add Exam type below.")


@app.route('/admin/add-exam-date', methods=['GET', 'POST'])
def admin_add_exam_date():
    form = ExamDate()
    if form.validate_on_submit():
        existing_exam_date = Has_exam.query.filter_by(academic_year=form.academic_year.data).filter_by(
            exam_type=form.exam_type.data).filter_by(subject_id=form.subject_id.data).first()
        if existing_exam_date:
            existing_exam_date.required_invigilators = form.required_invigilators.data
            existing_exam_date.exam_date = form.exam_date.data
        else:
            new_exam_date = Has_exam(
                academic_year=form.academic_year.data,
                exam_type=form.exam_type.data,
                subject_id=form.subject_id.data,
                required_invigilators=form.required_invigilators.data,
                exam_date=form.exam_date.data
            )
            db.session.add(new_exam_date)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin! Add Exam Date below.")


@app.route('/admin/edit-classroom', methods=['GET', 'POST'])
def admin_edit_classroom():
    form = ClassroomForm(
        classroom_id=request.args.get("classroom_id")
    )
    if form.validate_on_submit():
        classroom_id = form.classroom_id.data
        capacity = form.capacity.data
        dept_id = form.dept_id.data
        classroom_to_edit = Classroom.query.filter_by(classroom_id=classroom_id).first()
        if classroom_to_edit:
            classroom_id.capacity = capacity
            classroom_id.dept_id = dept_id
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin! Update Classroom details below.")


@app.route('/admin/allocate-invigilator', methods=["GET", "POST"])
def allocate_invigilator():
    r.run_the_algo()
    all_duties = Invigilates.query.all()
    all_has_exam = Has_exam.query.all()
    dates = []
    for i in all_duties:
        for j in all_has_exam:
            if i.academic_year == j.academic_year and i.exam_type == j.exam_type and i.subject_id == j.subject_id:
                current_entry = Has_exam.query.filter_by(academic_year=i.academic_year).filter_by(
                    exam_type=i.exam_type).filter_by(subject_id=i.subject_id).first()
                dates.append(current_entry.exam_date)
            else:
                dates.append("No date assigned yet.")
    no_invi = False
    if len(all_duties) == 0:
        no_invi = True
    return render_template("view-invi-duty.html", all_duties=all_duties, dates=dates, no_invi=no_invi,
                           len_all_duties=len(all_duties))


@app.route('/admin/view-faculties')
def view_faculties():
    all_faculty = Faculty.query.all()
    return render_template("view_faculties.html", all_faculty=all_faculty, table_heading="All Faculties")


@app.route('/admin/view-faculty-dept')
def view_faculty_dept():
    all_faculty = Faculty.query.order_by("dept_id").all()
    return render_template("view_faculty_dept.html", all_faculty=all_faculty, table_heading="All Faculty's Departments")


@app.route('/view-invi-report')
def view_invi_report():
    all_faculty = Invigilates.query.all()
    return render_template("view_invi_report.html", all_faculty=all_faculty, table_heading="All Faculty's Exam Duties")


@app.route('/admin/view-swap-requests', methods=['GET', 'POST'])
def view_swap_requests():
    all_requests = SwappingTable.query.order_by("swap_id").all()
    return render_template("view_swap_requests.html", all_requests=all_requests, table_heading="All Swap Requests")


@app.route('/plot')
def plot():
    plt.switch_backend('agg')
    grouped_up_data = db.session.query(Faculty.dept_id, func.count(Faculty.dept_id).label("total_count")).group_by(
        Faculty.dept_id).all()
    fields = [i[0] for i in grouped_up_data]
    for i in DEPARTMENT_IDS:
        if i in fields:
            pass
        else:
            grouped_up_data.append((i, 0))
    print(grouped_up_data)
    fields = [i[0] for i in grouped_up_data]
    left = [5, 20, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    # heights of bars
    # height = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    height = [i[1] for i in grouped_up_data]
    # labels for bars
    abrev = [i.split(" ") for i in fields]
    tick_label = [f"{i[0][0]}{i[len(i) - 1][0]}" for i in abrev]
    # plotting a bar chart
    plt.bar(left, height, tick_label=tick_label, width=1)

    # naming the y-axis
    plt.ylabel('Departments Present')
    # naming the x-axis
    plt.xlabel('No of Faculties Allotted')
    # plot title
    plt.title('No of Faculties vs Department Plot')

    plt.savefig('static/img/plot.png')
    return render_template('plot.html', url='/static/img/plot.png')


@app.route('/admin/approve-swap', methods=['GET', 'POST'])
def approve_swap():
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/secrets')
def secrets():
    display_name = request.args.get("display_name")
    return render_template("secrets.html", display_name=display_name)


@app.route("/about")
def about():
    return render_template("admin-home.html")


@app.route('/download', methods=["GET", "POST"])
def download():
    return send_from_directory(app.config['static-dark-old'], "files/cheat_sheet.pdf", as_attachment=True)


@app.route('/admin/algo-plot', methods=["GET", "POST"])
def admin_algo_plot():
    r.run_the_algo()
    return render_template("algo-plot-admin.html", url='static/img/algo_plot.png')


@app.route('/barcode_reader')
def barcode_reader():
    display_name = request.args.get("display_name")
    default_email = request.args.get("default_email")
    return render_template('barcode.html', display_name=display_name, default_email=default_email)


@app.route('/display_barcode')
def display_barcode():
    display_name = request.args.get("display_name")
    default_email = request.args.get("default_email")
    return render_template(
        'display_barcode.html',
        type1=type_barcode,
        data1=data_barcode,
        display_name=display_name,
        default_email=default_email
    )


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)

### Table with list of classrooms and edit feature
