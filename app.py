from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
# Importar Enum para usar en el modelo
from sqlalchemy import Enum, func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import datetime, timedelta


from flask_socketio import SocketIO, emit

from reportlab.pdfgen import canvas
from io import BytesIO

import uuid

# Inicializar la instancia de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Añadir la configuración de la clave secreta para las sesiones
app.config['SECRET_KEY'] = 'your_secret_key'

#verificacion de la persistencia de la sesion
app.config['SESSION_TYPE'] = 'filesystem'


# Inicializar la base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

from flask_sqlalchemy import SQLAlchemy

# Inicialización de la extensión SQLAlchemy
db = SQLAlchemy()

# Modelo para la tabla nombre_tramite
class NombreTramite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

# Modelo para la tabla niveles
class Nivel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_nivel = db.Column(db.String(100), nullable=False)

# Modelo para la tabla municipio
class Municipio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_municipio = db.Column(db.String(100), nullable=False)

# Modelo para la tabla asunto
class Asunto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asunto = db.Column(db.String(255), nullable=False)

# Modelo para la tabla tickets
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    curp = db.Column(db.String(18), nullable=False)
    nombre_completo = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    paterno = db.Column(db.String(100), nullable=False)
    materno = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    correo = db.Column(db.String(255), nullable=False)
    nivel_id = db.Column(db.Integer, db.ForeignKey('nivel.id'), nullable=False)
    municipio_id = db.Column(db.Integer, db.ForeignKey('municipio.id'), nullable=False)
    asunto_id = db.Column(db.Integer, db.ForeignKey('asunto.id'), nullable=False)
    nombre_tramite_id = db.Column(db.Integer, db.ForeignKey('nombre_tramite.id'))
    
    # Definir relaciones
    nivel = db.relationship('Nivel', backref=db.backref('tickets', lazy=True))
    municipio = db.relationship('Municipio', backref=db.backref('tickets', lazy=True))
    asunto = db.relationship('Asunto', backref=db.backref('tickets', lazy=True))
    nombre_tramite = db.relationship('NombreTramite', backref=db.backref('tickets', lazy=True))


# Modelo para la tabla usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Rutas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'cliente':
                return redirect(url_for('ticket'))
        else:
            error = 'Usuario o contraseña incorrectos'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/ticket')
def ticket_form():
    return render_template('ticket.html')

# Inicializar la aplicación
if __name__ == '__main__':
    app.run(debug=True)