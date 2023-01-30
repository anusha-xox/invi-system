from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {'faculty': 'sqlite:///faculty.db',
                                  'subject': 'sqlite:///subject.db',
                                  'admin': 'sqlite:///admin.db',
                                  'departments': 'sqlite:///departments.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

DEPARTMENT_NAMES = ["Aerospace Engineering", "Biotechnology", "Chemical Engineering", "Civil Engineering",
                    "Computer Science and Engineering", "Electrical and Electronics Engineering",
                    "Electronics and Communication Engineering", "Electronics and Instrumentation Engineering",
                    "Industrial Engineering and Management", "Information Science and Engineering",
                    "Master of Computer Applications", "Mechanical Engineering", "Telecommunication Engineering",
                    "Basic Sciences"]

FACULTY_ROLE = ["Room Superintendent", "Deputy Room Superintendent", "Squad Team"]

EXAM_TYPE = ["Regular", "Fasttrack", "Make Up"]
EXAM_YEAR = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23"]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Faculty(db.Model):
    __bind_key__ = 'faculty'
    fac_id = db.Column(db.Integer, primary_key=True)
    fac_email = db.Column(db.String(250), unique=True, nullable=False)
    fac_fname = db.Column(db.String(250), unique=False, nullable=False)
    fac_mname = db.Column(db.String(250), unique=False, nullable=False)
    fac_lname = db.Column(db.String(250), unique=False, nullable=False)
    group_id = db.Column(db.Integer, unique=False, nullable=False)
    phone_no = db.Column(db.Integer, unique=True, nullable=False)
    dept_id = db.Column(db.Integer, unique=False, nullable=False)
    dept_name = db.Column(db.String(250), unique=False, nullable=False)


class Subject(db.Model):
    __bind_key__ = 'subject'
    sub_id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(250), unique=False, nullable=False)
    sub_duration = db.Column(db.Integer, unique=False, nullable=False)
    academic_year = db.Column(db.Integer, unique=False, nullable=False)
    classroom_no = db.Column(db.String(250), unique=False, nullable=False)


class Admin(db.Model):
    __bind_key__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    fac_id = db.Column(db.Integer, unique=False, nullable=False)
    group_id = db.Column(db.String(250), unique=False, nullable=False)
    dept_id = db.Column(db.String(250), unique=False, nullable=False)
    faculty_role = db.Column(db.String(250), unique=False, nullable=False)
    exam_type = db.Column(db.String(250), unique=False, nullable=False)
    exam_year = db.Column(db.String(250), unique=False, nullable=False)


class Departments(db.Model):
    __bind_key__ = 'departments'
    dept_id = db.Column(db.String(250), primary_key=True)
    dept_name = db.Column(db.String(250), unique=True, nullable=True)


db.create_all()


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


@app.route('/')
def home():
    return redirect(url_for('register'))
    # return render_template("admin-home.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        new_user = User(
            email=data["email"],
            password=generate_password_hash(data["password"], method='pbkdf2:sha256', salt_length=8),
            name=request.form.get("name"),
        )
        display_name = data["name"]
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('secrets', display_name=display_name))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        if email == 'admin@email.com' and password == 'admin':
            return redirect(url_for('admin'))
        else:
            user = User.query.filter_by(email=email).first()
            requested_user_email = User.query.get(email)
            if check_password_hash(user.password, password):
                login_user(user)
                # return redirect(url_for('secrets', display_name=user.name))
                # for f in Faculty.query.all():
                #     if user.email == f.fac_email:
                #         return redirect(url_for("faculty_dashboard", fac_id=f.fac_id))
                return redirect(url_for('add_faculty', display_name=user.name))
    return render_template("login.html")


@app.route('/admin-assign', methods=['GET', 'POST'])
def admin_assign():
    form = AdminForm()
    if form.validate_on_submit():
        fac_id = form.fac_id.data
        group_id = int(form.group_id.data)
        dept_id = str(form.dept_id.data)
        faculty_to_edit = Faculty.query.filter_by(fac_id=fac_id).first()
        if faculty_to_edit:
            faculty_to_edit.group_id = group_id
            new_allotment = Admin(
                fac_id=fac_id,
                group_id=group_id,
                dept_id=dept_id,
                faculty_role=form.faculty_role.data,
                exam_type=form.exam_type.data,
                exam_year=form.exam_year.data
            )
            db.session.add(new_allotment)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template("admin-form.html", form=form)


@app.route("/faculty-dashboard/<int:fac_id>", methods=['GET', 'POST'])
def faculty_dashboard(fac_id):
    current_faculty = User.query.filter_by(fac_id=fac_id).first()
    return render_template("faculty-dashboard.html", current_faculty=current_faculty)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template("admin-home.html")


@app.route('/add-faculty', methods=["GET", "POST"])
def add_faculty():
    form = FacultyForm()
    display_name = request.args.get("display_name")
    if form.validate_on_submit():
        new_faculty = Faculty(
            fac_id=int(form.fac_id.data),
            fac_email=form.fac_email.data,
            fac_fname=form.fac_fname.data,
            fac_mname=form.fac_mname.data,
            fac_lname=form.fac_lname.data,
            phone_no=form.phone_no.data,
            group_id=0,
            dept_id=str(form.dept_id.data),
            dept_name=form.dept_name.data
        )
        db.session.add(new_faculty)
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template("add_faculty.html", form=form, display_name=display_name)


@app.route('/view-faculties')
def view_faculties():
    all_faculty = Faculty.query.all()
    return render_template("view_faculties.html", all_faculty=all_faculty)


@app.route('/view-faculty-dept')
def view_faculty_dept():
    all_faculty = Faculty.query.order_by("dept_id").all()
    return render_template("view-faculty-dept.html", all_faculty=all_faculty)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/secrets')
# @login_required
def secrets():
    display_name = request.args.get("display_name")
    return render_template("secrets.html", display_name=display_name)


@app.route("/preview")
def preview():
    return render_template("admin-home.html")


@app.route('/download', methods=["GET", "POST"])
def download():
    return send_from_directory(app.config['static-old'], "files/cheat_sheet.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
