from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask import Flask
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from wtforms.fields.html5 import DateField, IntegerField
import datetime
# from main import Exam, Subject

DEPARTMENT_NAMES = ["Aerospace Engineering", "Biotechnology", "Chemical Engineering", "Civil Engineering",
                    "Computer Science and Engineering", "Electrical and Electronics Engineering",
                    "Electronics and Communication Engineering", "Electronics and Instrumentation Engineering",
                    "Industrial Engineering and Management", "Information Science and Engineering",
                    "Master of Computer Applications", "Mechanical Engineering", "Telecommunication Engineering",
                    "Basic Sciences"]
DEPARTMENT_IDS = ["AE", "BT", "CH", "CV", "CSE", "ECE", "EEE", "EIE", "IME", "ISE", "MA", "ME", "TC", "BS"]
FACULTY_ROLE = ["Room Superintendent", "Deputy Room Superintendent", "Squad Team"]
EXAM_TYPE = ["Regular", "Fasttrack", "Make Up"]
EXAM_YEAR = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
SUBJECT_CODES = ["18MA11", "18PH12", "18EE13", "18CV14", "18EE15", "18ME16", "18HS17"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql12609170:XR9CRf2TYY@sql12.freesqldatabase.com/sql12609170'
db = SQLAlchemy(app)


class Exam(db.Model):
    academic_year = db.Column(db.String(4), primary_key=True, nullable=False)
    exam_type = db.Column(db.String(15), primary_key=True, nullable=False)


class Subject(db.Model):
    subject_id = db.Column(db.String(10), primary_key=True)
    subject_name = db.Column(db.String(100), unique=False, nullable=False)
    subject_duration = db.Column(db.String(15), unique=False, nullable=False)


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class RegisterForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Register')


class FacultyForm(FlaskForm):
    faculty_id = StringField('Faculty Id', validators=[DataRequired()])
    email = StringField('Faculty Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    f_name = StringField('First name', validators=[DataRequired()])
    m_name = StringField('Middle name')
    l_name = StringField('Last name')
    phone_no = StringField('Phone Number', validators=[DataRequired()])
    dept_id = SelectField('Department ID', choices=DEPARTMENT_IDS, validators=[DataRequired()])

    # dept_name = SelectField('Department Name', choices=DEPARTMENT_NAMES, validators=[DataRequired()])
    submit = SubmitField('Submit')


class AdminForm(FlaskForm):
    faculty_id = StringField('Faculty Id', validators=[DataRequired()])
    group_id = StringField('Group Id', validators=[DataRequired()])
    dept_id = SelectField('Department ID', choices=DEPARTMENT_IDS, validators=[DataRequired()])
    submit = SubmitField('Submit')


class ClassroomForm(FlaskForm):
    classroom_id = StringField('Classroom ID', validators=[DataRequired()])
    capacity = StringField('Capacity', validators=[DataRequired()])
    dept_id = SelectField('Department ID', choices=DEPARTMENT_IDS, validators=[DataRequired()])
    submit = SubmitField('Submit')


class ExamTypeForm(FlaskForm):
    academic_year = SelectField('Academic Year', choices=EXAM_YEAR, validators=[DataRequired()])
    exam_type = SelectField('Exam Type', choices=EXAM_TYPE, validators=[DataRequired()])
    submit = SubmitField('Submit')


class ExamDate(FlaskForm):
    academic_year = SelectField("Academic Year")
    exam_type = SelectField('Exam Type', choices=EXAM_TYPE, validators=[DataRequired()])
    subject_id = SelectField("Subject ID", validators=[DataRequired()])
    required_invigilators = IntegerField('Required Invigilators', validators=[DataRequired()])
    exam_date = DateField('Exam Date', format='%Y-%m-%d')
    exam_time_hour = IntegerField('Start Hour (24hr format)', validators=[DataRequired(), NumberRange(min=0, max=24,
                                                                                                      message='Please Enter a Valid Hour')])
    exam_time_min = IntegerField('Start Minute', validators=[DataRequired(), NumberRange(min=0, max=59,
                                                                                         message='Please Enter a Valid Minute')])

    def validate_date(form, field):
        if field.data < datetime.date.today():
            raise ValidationError("The date cannot be in the past!")

    def __init__(self, *args, **kwargs):
        super(ExamDate, self).__init__(*args, **kwargs)
        self.academic_year.choices = [c.academic_year for c in Exam.query.all()]
        self.subject_id.choices = [c.subject_id for c in Subject.query.all()]

    submit = SubmitField(label='Submit')


class SubjectForm(FlaskForm):
    sub_id = StringField('Subject Id', validators=[DataRequired()])
    sub_name = StringField('Subject Name', validators=[DataRequired()])
    subject_code = SelectField('Subject Code', choices=SUBJECT_CODES, validators=[DataRequired()])
    submit = SubmitField('Submit')


class SwapRequestForm(FlaskForm):
    curr_fac_id = StringField('Your Faculty ID', validators=[DataRequired()])
    other_fac_id = StringField('Their Faculty ID', validators=[DataRequired()])
    old_date = StringField('Your Old Date of Invigilation Duty (DD/MM/YYYY)', validators=[DataRequired()])
    new_date = StringField('Your New Date of Invigilation Duty (DD/MM/YYYY)', validators=[DataRequired()])
    old_time = StringField('Your Old Time of Invigilation Duty (DD/MM/YYYY)', validators=[DataRequired()])
    new_time = StringField('Your New Time of Invigilation Duty (DD/MM/YYYY)', validators=[DataRequired()])
    old_exam_type = SelectField('Your Old Exam Type', choices=EXAM_TYPE, validators=[DataRequired()])
    new_exam_type = SelectField('Your New Exam Type', choices=EXAM_TYPE, validators=[DataRequired()])
    old_exam_year = SelectField('Your Old Exam Year', choices=EXAM_YEAR, validators=[DataRequired()])
    new_exam_year = SelectField('Your New Exam Year', choices=EXAM_YEAR, validators=[DataRequired()])
    old_subject_code = SelectField("Old Subject Code", choices=SUBJECT_CODES, validators=[DataRequired()])
    new_subject_code = SelectField('New Subject Code', choices=SUBJECT_CODES, validators=[DataRequired()])
    submit = SubmitField('Submit')
