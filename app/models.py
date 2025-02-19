from app_db import db
from datetime import datetime



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

from app_db import db

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellidos}>'
    
class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)  # 🔹 Relación con Productos
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)  # 🔹 Relación con Clientes
    unidades_peso = db.Column(db.Float, nullable=False)  # 🔹 Puede representar cantidad en unidades o en kg
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 🔹 Fecha de la compra
    provincia_compra = db.Column(db.String(100), nullable=False)  # 🔹 Lugar donde se realizó la compra

    # Relación con Producto y Cliente
    producto = db.relationship('Producto', backref=db.backref('compras', lazy=True))
    cliente = db.relationship('Cliente', backref=db.backref('compras', lazy=True))

    def __repr__(self):
        return f'<Compra {self.id} - {self.producto.nombre} por {self.cliente.nombre}>'

