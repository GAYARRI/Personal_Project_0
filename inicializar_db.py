from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configuración de la aplicación Flask
app = Flask(__name__)

# Ruta a la base de datos
db_path = os.path.join('C:/Users/gayar/Personal_Project/RepoP0', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo para la tabla `registro`
class Registro(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    valor = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Registro {self.nombre}>"

# Crear tablas y agregar registros en un contexto de aplicación
with app.app_context():
    # Crear las tablas si no existen
    db.create_all()
    print("Tabla 'registro' creada con éxito")

    # Insertar registros
    try:
        registro1 = Registro(nombre="Ejemplo Nombre 1", valor="100")
        registro2 = Registro(nombre="Ejemplo Nombre 2", valor="200")
        db.session.add_all([registro1, registro2])
        db.session.commit()
        print("Registros añadidos correctamente:")
        print(f"ID: {registro1.id}, Nombre: {registro1.nombre}, Valor: {registro1.valor}")
        print(f"ID: {registro2.id}, Nombre: {registro2.nombre}, Valor: {registro2.valor}")
    except Exception as e:
        db.session.rollback()
        print(f"Error al insertar los registros: {e}")





