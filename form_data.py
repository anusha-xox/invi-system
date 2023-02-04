from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator

DEPARTMENT_NAMES = ["Aerospace Engineering", "Biotechnology", "Chemical Engineering", "Civil Engineering",
                    "Computer Science and Engineering", "Electrical and Electronics Engineering",
                    "Electronics and Communication Engineering", "Electronics and Instrumentation Engineering",
                    "Industrial Engineering and Management", "Information Science and Engineering",
                    "Master of Computer Applications", "Mechanical Engineering", "Telecommunication Engineering",
                    "Basic Sciences"]

FACULTY_ROLE = ["Room Superintendent", "Deputy Room Superintendent", "Squad Team"]
EXAM_TYPE = ["Regular", "Fasttrack", "Make Up"]
EXAM_YEAR = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23"]


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
    fac_id = StringField('Faculty Id', validators=[DataRequired()])
    fac_email = StringField('Faculty Email', validators=[DataRequired(), Email()])
    fac_fname = StringField('First name', validators=[DataRequired()])
    fac_mname = StringField('Middle name')
    fac_lname = StringField('Last name')
    phone_no = StringField('Phone Number', validators=[DataRequired()])
    dept_id = StringField('Department Id', validators=[DataRequired()])
    dept_name = SelectField('Department Name', choices=DEPARTMENT_NAMES, validators=[DataRequired()])
    submit = SubmitField('Submit')


class AdminForm(FlaskForm):
    fac_id = StringField('Faculty Id', validators=[DataRequired()])
    group_id = StringField('Group Id', validators=[DataRequired()])
    dept_id = StringField('Dept Id', validators=[DataRequired()])
    faculty_role = SelectField('Faculty Role', choices=FACULTY_ROLE, validators=[DataRequired()])
    exam_type = SelectField('Exam Type', choices=EXAM_TYPE, validators=[DataRequired()])
    exam_year = SelectField('Exam Year', choices=EXAM_YEAR, validators=[DataRequired()])
    submit = SubmitField('Submit')


class SubjectForm(FlaskForm):
    sub_id = StringField('Subject Id', validators=[DataRequired()])
    sub_name = StringField('Subject Name', validators=[DataRequired()])
    sub_duration = StringField('Subject Duration', validators=[DataRequired()])
    submit = SubmitField('Submit')
