from flask import Flask, flash, url_for, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_pymongo import PyMongo
from bson import json_util
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_bcrypt import Bcrypt
import os
SECRET_KEY = os.urandom(32)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask:1234@localhost/flask'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
bcrypt = Bcrypt(app)

#MONGODB CONFIG
app.config["MONGO_URI"] = "mongodb://localhost:27017/python"
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
	__tablename__ = "users"
	id = db.Column("id", db.Integer, primary_key=True)
	user = db.Column("user", db.String(100), nullable=False, unique=True)
	password = db.Column("password", db.String(100), nullable=False)

	
class Tareas(db.Model):
	__tablename__ = "tareas"
	id = db.Column("id", db.Integer, primary_key=True)
	tarea = db.Column("tarea", db.String(399))

	def __init__(self, tarea):
		self.tarea = tarea

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route("/")
def hello():
	return render_template("inicio.html")
@app.route('/dashboard/<user>', methods=['GET', 'POST'])
@login_required
def dashboard(user):
    return render_template('dashboard.html',user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(user=form.username.data).first()
		print()
		if user:
			if bcrypt.check_password_hash(user.password, form.password.data):
				login_user(user)
				return redirect(url_for('dashboard',user=form.username.data))
			else:
				flash('ERROR! CONTRASEÑA INCORRECTA')
				return redirect("/login")
		else:
			flash('ERROR! USUARIO NO ENCONTRADO')
			return redirect("/login")
	return render_template("login.html",form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
	form = LoginForm()
	if form.validate_on_submit():
	    hashed_password = bcrypt.generate_password_hash(form.password.data)
	    new_user = Users(user=form.username.data, password=hashed_password)
	    db.session.add(new_user)
	    db.session.commit()
	    return redirect("/")


	return render_template("register.html", form=form)

@app.route("/index")
def index():
	consulta = db.session.query(Tareas).all()
	print(consulta)
	return render_template("index.html", tareas0=consulta)

@app.route("/agregar.html", methods=["GET", "POST"])
def agregar():
    if request.method == "GET":

        return render_template("agregar.html")
    else:
        tarea = request.form.get("tarea")
        tareas0 = Tareas(tarea=tarea)
        db.session.add(tareas0)
        db.session.commit()

        return redirect("/index")

@app.route("/borrar", methods=["POST"])
def borrar():
	tarea_id = request.form.get("tarea_id")
	tarea_borrar = db.session.query(Tareas).filter(Tareas.id==tarea_id).first()
	db.session.delete(tarea_borrar)
	db.session.commit()
	return redirect("/index")

@app.route("/editar/<tarea_id>", methods=["GET"])
def editar(tarea_id):
	return render_template("editar.html", tarea_id=tarea_id)

@app.route("/actualizar/<tarea_id>", methods=["POST"])
def actualizar(tarea_id):
	editar = request.form.get("editar_tarea")
	db.session.query(Tareas).filter(Tareas.id==tarea_id).update({Tareas.tarea: editar})
	db.session.commit()
	print(request.form.get("editar_tarea"))
	print(editar)
	return redirect("/index")


@app.route("/usuarios", methods=['GET'])
def usuarios():

	usuarios = mongo.db.usuarios.find()
	
	print(usuarios)
	return render_template("usuarios.html", usuarios=usuarios)

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True)