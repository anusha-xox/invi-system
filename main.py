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
                                  'subject': 'sqlite:///subject.db'
                                  'admin': 'sqlite:///admin.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


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
    id = db.Column(db.Integer, primary_key=True)
    fac_id = title = db.Column(db.String(250), unique=True, nullable=False)
    fac_email = db.Column(db.String(250), unique=True, nullable=False)
    fac_fname = db.Column(db.String(250), unique=False, nullable=False)
    fac_mname = db.Column(db.String(250), unique=False, nullable=False)
    fac_lname = db.Column(db.String(250), unique=False, nullable=False)
    group_id = db.Column(db.Integer, unique=False, nullable=False)
    phone_no = db.Column(db.Integer, unique=True, nullable=False)
    submit = SubmitField('Submit')


class Subject(db.Model):
    __bind_key__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)

class Admin(db.Model):
    __bind_key__ = 'admin'
    fac_id = db.Column(db.String(250), primary_key=True)
    group_id = db.Column(db.String(250), unique=False, nullable=False)

#db.create_all()


class FacultyForm(FlaskForm):
    fac_id = StringField('Faculty Id', validators=[DataRequired()])
    fac_email = StringField('Faculty Email', validators=[DataRequired(), Email()])
    fac_fname = StringField('First name', validators=[DataRequired()])
    fac_mname = StringField('Middle name', validators=[DataRequired()])
    fac_lname = StringField('Last name', validators=[DataRequired()])
    group_id = StringField('Group ID', validators=[DataRequired()])
    phone_no = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AdminForm(FlaskForm):
    fac_id = StringField('Faculty Id', validators=[DataRequired()])
    group_id = StringField('Group Id', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    return render_template("index.html")


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
            requested_post = User.query.get(email)
            if check_password_hash(user.password, password):
                login_user(user)
                # return redirect(url_for('secrets', display_name=user.name))
                return redirect(url_for('add_faculty', display_name=user.name))
    return render_template("login.html")


@app.route('/secrets')
# @login_required
def secrets():
    display_name = request.args.get("display_name")
    return render_template("secrets.html", display_name=display_name)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        new_allotment = Admin(
            fac_id=form.fac_id.data,
            group_id=form.group_id.data,
        )
        db.session.add(new_allotment)
        db.session.commit()
    return render_template("admin.html", form=form)

@app.route('/add-faculty', methods=["GET", "POST"])
def add_faculty():
    form = FacultyForm()
    display_name = request.args.get("display_name")
    if form.validate_on_submit():
        new_faculty = Faculty(
            fac_id=form.fac_id.data,
            fac_email=form.fac_email.data,
            fac_fname=form.fac_fname.data,
            fac_mname=form.fac_mname.data,
            fac_lname=form.fac_lname.data,
            phone_no=form.phone_no.data,
            group_id=0,
            dept_no=0,
        )
        db.session.add(new_faculty)
        db.session.commit()
    return render_template("add_faculty.html", form=form, display_name=display_name)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download', methods=["GET", "POST"])
def download():
    return send_from_directory(app.config['static'], "files/cheat_sheet.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
