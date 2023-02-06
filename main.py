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
from form_data import LoginForm, RegisterForm, FacultyForm, AdminForm, SubjectForm, SwapRequestForm, DEPARTMENT_NAMES
## for graph
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invi-system.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:toor@localhost/users'

# app.config['SQLALCHEMY_BINDS'] = {'faculty': 'sqlite:///faculty.db',
#                                   'subject': 'sqlite:///subject.db',
#                                   'admin': 'sqlite:///admin.db',
#                                   'departments': 'sqlite:///departments.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))


class Faculty(db.Model):
    # __bind_key__ = 'faculty'
    fac_id = db.Column(db.Integer, primary_key=True)
    fac_email = db.Column(db.String(250), unique=True, nullable=False)
    fac_fname = db.Column(db.String(250), unique=False, nullable=False)
    fac_mname = db.Column(db.String(250), unique=False, nullable=False)
    fac_lname = db.Column(db.String(250), unique=False, nullable=False)
    group_id = db.Column(db.Integer, unique=False, nullable=False)
    phone_no = db.Column(db.Integer, unique=True, nullable=False)
    dept_id = db.Column(db.Integer, unique=False, nullable=False)
    dept_name = db.Column(db.String(250), unique=False, nullable=False)

    fac_admin_foreign = db.Column(db.Integer, db.ForeignKey('admin.fac_id'))


class Subject(db.Model):
    # __bind_key__ = 'subject'
    sub_id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(250), unique=False, nullable=False)
    sub_duration = db.Column(db.Integer, unique=False, nullable=False)
    academic_year = db.Column(db.Integer, unique=False, nullable=False)
    classroom_no = db.Column(db.String(250), unique=False, nullable=False)


class Admin(db.Model):
    # __bind_key__ = 'inviDuty'
    entry_id = db.Column(db.Integer, primary_key=True)
    fac_id = db.Column(db.Integer, unique=False, nullable=False)
    group_id = db.Column(db.String(250), unique=False, nullable=False)
    dept_id = db.Column(db.String(250), unique=False, nullable=False)
    date = db.Column(db.String(250), unique=False, nullable=False)
    timeslot = db.Column(db.String(250), unique=False, nullable=False)
    exam_type = db.Column(db.String(250), unique=False, nullable=False)
    exam_year = db.Column(db.String(250), unique=False, nullable=False)
    faculty_role = db.Column(db.String(250), unique=False, nullable=False)
    subject_code = db.Column(db.String(250), unique=False, nullable=False)
    invigilators = db.relationship("Faculty", backref="admin")


class Departments(db.Model):
    dept_id = db.Column(db.String(250), primary_key=True)
    dept_name = db.Column(db.String(250), unique=True, nullable=True)


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
                    if user.email == f.fac_email:
                        # return redirect(url_for('add_faculty', display_name=user.username))
                        return redirect(url_for("faculty_dashboard", fac_id=f.fac_id))
                    # else:
                    #     return redirect(url_for('add_faculty', display_name=user.username, default_email=user.email))
    return render_template('enter.html', form=form, title_given="Login")


@app.route('/add-faculty', methods=["GET", "POST"])
def add_faculty():
    display_name = request.args.get("display_name")
    default_email = request.args.get("default_email")
    form = FacultyForm(
        fac_email=default_email
    )
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
    return render_template("add_details.html", form=form, display_name=display_name)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    ADMIN_OPTIONS = [
        "Generate Invigilator Report",
        "Generate Department Report",
        "Generate Duty Report",
        "Give Invigilator Duty",
        "View Swap Requests",
        "No of Faculties vs Department Plot"
    ]
    ADMIN_LINKS = [url_for('view_faculties'), url_for('view_faculty_dept'), url_for("view_invi_report"),
                   url_for('admin_assign'), url_for("view_swap_requests"), url_for("plot")]
    return render_template(
        "grid.html",
        title="Admin",
        grid_options=ADMIN_OPTIONS,
        grid_links=ADMIN_LINKS,
        grid_no=len(ADMIN_OPTIONS)
    )


@app.route("/faculty-home", methods=['GET', 'POST'])
def faculty_dashboard():
    fac_id = int(request.args.get("fac_id"))
    current_faculty = Faculty.query.get(fac_id)
    if current_faculty:
        FACULTY_OPTIONS = [
            "Edit Profile",
            "View Profile",
            "Generate Duty Report",
            "Request Swap from Admin",
        ]
        FACULTY_LINKS = [
            url_for('edit_profile', fac_id=fac_id),
            url_for('view_profile', fac_id=fac_id),
            url_for("view_invi_report"),
            url_for("swap_request", fac_id=fac_id)]
        return render_template(
            "grid.html",
            title=current_faculty.fac_fname,
            grid_options=FACULTY_OPTIONS,
            grid_links=FACULTY_LINKS,
            grid_no=len(FACULTY_OPTIONS)
        )


@app.route("/faculty-home/edit", methods=['GET', 'POST'])
def edit_profile():
    fac_id = int(request.args.get("fac_id"))
    current_faculty = Faculty.query.get(fac_id)
    if current_faculty:
        form = FacultyForm(
            fac_id=int(current_faculty.fac_id),
            fac_email=current_faculty.fac_email,
            fac_fname=current_faculty.fac_fname,
            fac_mname=current_faculty.fac_mname,
            fac_lname=current_faculty.fac_lname,
            phone_no=current_faculty.phone_no,
            dept_id=str(current_faculty.dept_id),
            dept_name=current_faculty.dept_name
        )
        if form.validate_on_submit():
            current_faculty.fac_email = form.fac_email.data
            current_faculty.fac_fname = form.fac_fname.data
            current_faculty.fac_mname = form.fac_mname.data
            current_faculty.fac_lname = form.fac_lname.data
            current_faculty.phone_no = form.phone_no.data
            current_faculty.dept_id = str(form.dept_id.data)
            current_faculty.dept_name = form.dept_name.data
            db.session.commit()
            new_fac_id = int(form.fac_id.data)
            return redirect(url_for("faculty_dashboard", fac_id=new_fac_id))
        return render_template("add_details.html", form=form, display_name=current_faculty.fac_fname)


@app.route("/faculty-home/view")
def view_profile():
    fac_id = int(request.args.get("fac_id"))
    current_faculty = Faculty.query.get(fac_id)
    heading = f"{current_faculty.fac_fname} {current_faculty.fac_mname} {current_faculty.fac_lname}'s Saved Details"
    return render_template("faculty_details.html", cf=current_faculty, table_heading=heading)


@app.route("/faculty-home/swap-request", methods=['GET', 'POST'])
def swap_request():
    fac_id = int(request.args.get("fac_id"))
    current_faculty = Faculty.query.get(fac_id)
    if current_faculty:
        form = SwapRequestForm(
            cur_fac_id=int(current_faculty.fac_id),
        )
        if form.validate_on_submit():
            new_record = SwappingTable(
                curr_fac_id=int(form.curr_fac_id.data),
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
        return render_template("add_details.html", form=form, display_name=current_faculty.fac_fname)


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
                date=form.date.data,
                timeslot=form.timeslot.data,
                exam_type=form.exam_type.data,
                exam_year=form.exam_year.data,
                subject_code=form.subject_code.data
            )
            db.session.add(new_allotment)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin! Add/Update Faculty details below.")


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
    all_faculty = Admin.query.order_by("date").all()
    return render_template("view_invi_report.html", all_faculty=all_faculty, table_heading="All Faculty's Exam Duties")


@app.route('/admin/view-swap-requests', methods=['GET', 'POST'])
def view_swap_requests():
    all_requests = SwappingTable.query.order_by("swap_id").all()
    return render_template("view_swap_requests.html", all_requests=all_requests, table_heading="All Swap Requests")


@app.route('/plot')
def plot():
    pass


@app.route('/admin/approve-swap', methods=['GET', 'POST'])
def approve_swap():
    swap_id = int(request.args.get("swap_id"))
    current_swap = SwappingTable.query.get(swap_id)
    if current_swap:
        return redirect(url_for("logout"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/secrets')
# @login_required
def secrets():
    display_name = request.args.get("display_name")
    return render_template("secrets.html", display_name=display_name)


@app.route("/about")
def about():
    return render_template("admin-home.html")


@app.route('/download', methods=["GET", "POST"])
def download():
    return send_from_directory(app.config['static-dark-old'], "files/cheat_sheet.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
