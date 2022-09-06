from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_pymongo import PyMongo
from bson import json_util
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask:1234@localhost/flask'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#MONGODB CONFIG
app.config["MONGO_URI"] = "mongodb://localhost:27017/python"
mongo = PyMongo(app)

class Tareas(db.Model):
	__tablename__ = "tareas"
	id = db.Column("id", db.Integer, primary_key=True)
	tarea = db.Column("tarea", db.String(399))

	def __init__(self, tarea):
		self.tarea = tarea

@app.route("/")
def hello():
	return render_template("inicio.html")

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
	return redirect("/index")


@app.route("/usuarios", methods=['GET'])
def usuarios():

	usuarios = mongo.db.usuarios.find()
	
	print(usuarios)
	return render_template("usuarios.html", usuarios=usuarios)

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True)