from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from form_data import LoginForm, RegisterForm, FacultyForm, AdminForm, SubjectForm

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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))


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


# class Subject(db.Model):
#     __bind_key__ = 'subject'
#     sub_id = db.Column(db.Integer, primary_key=True)
#     sub_name = db.Column(db.String(250), unique=False, nullable=False)
#     sub_duration = db.Column(db.Integer, unique=False, nullable=False)
#     academic_year = db.Column(db.Integer, unique=False, nullable=False)
#     classroom_no = db.Column(db.String(250), unique=False, nullable=False)


class Admin(db.Model):
    __bind_key__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    fac_id = db.Column(db.Integer, unique=False, nullable=False)
    group_id = db.Column(db.String(250), unique=False, nullable=False)
    dept_id = db.Column(db.String(250), unique=False, nullable=False)
    faculty_role = db.Column(db.String(250), unique=False, nullable=False)
    exam_type = db.Column(db.String(250), unique=False, nullable=False)
    exam_year = db.Column(db.String(250), unique=False, nullable=False)


# class Departments(db.Model):
#     __bind_key__ = 'departments'
#     dept_id = db.Column(db.String(250), primary_key=True)
#     dept_name = db.Column(db.String(250), unique=True, nullable=True)


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
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        display_name = form.username.data
        return redirect(url_for('add_faculty', display_name=display_name))
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
                return redirect(url_for('add_faculty', display_name=user.username))
                # for f in Faculty.query.all():
                #     if user.email == f.fac_email:
                #         return redirect(url_for("faculty_dashboard", fac_id=f.fac_id))
    return render_template('enter.html', form=form, title_given="Login")


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
    return render_template("add_details.html", form=form, display_name=display_name)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    ADMIN_OPTIONS = ["Generate Invigilator Report", "Generate Department Report", "Generate Duty Report", "Assign Invigilator Roles"]
    ADMIN_LINKS = [url_for('view_faculties'), url_for('view_faculty_dept'), "", url_for('admin_assign')]
    return render_template("grid.html", title="Admin", grid_options=ADMIN_OPTIONS, grid_links=ADMIN_LINKS, grid_no=len(ADMIN_OPTIONS))


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
    return render_template("add_details.html", form=form, display_name="Admin! Add/Update Faculty details below.")


@app.route("/faculty-dashboard/<int:fac_id>", methods=['GET', 'POST'])
def faculty_dashboard(fac_id):
    current_faculty = Faculty.query.filter_by(fac_id=fac_id).first()
    return render_template("faculty-dashboard.html", current_faculty=current_faculty)


@app.route('/admin/view-faculties')
def view_faculties():
    all_faculty = Faculty.query.all()
    return render_template("view_faculties.html", all_faculty=all_faculty, table_heading="All Faculties")


@app.route('/admin/view-faculty-dept')
def view_faculty_dept():
    all_faculty = Faculty.query.order_by("dept_id").all()
    return render_template("view_faculty_dept.html", all_faculty=all_faculty, table_heading="All Faculty's Departments")


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
