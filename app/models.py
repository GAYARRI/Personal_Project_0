from app_db import db



class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    productos = db.relationship('Producto', backref='categoria', cascade='all, delete-orphan')

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

class Ciudad(db.Model):
    __tablename__ = 'ciudades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)  # Columna para la latitud
    lon = db.Column(db.Float, nullable=False)  # Columna para la longitud 

