
from flask import Flask
from app_db import db
from app.models import Categoria, Producto, Ciudad  # Importar todas las clases necesarias
from app import routes
import os

def create_app():

    app = Flask(__name__)

    if not os.path.exists('app/static'):
        os.makedirs('app/static')
        
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)

    # Insertar datos de ejemplo si no existen
    with app.app_context():
        db.create_all()

        # Inicializar Categorías y Productos
        if not Categoria.query.first():  # Verifica si la tabla de categorías está vacía
            categorias_ejemplo = [
                Categoria(nombre="Electrónica"),
                Categoria(nombre="Ropa"),
                Categoria(nombre="Hogar"),
            ]
            db.session.add_all(categorias_ejemplo)
            db.session.flush()  # Asegura que las categorías tengan IDs asignados

            productos_ejemplo = [
                Producto(nombre="Teléfono", precio=500.0, categoria_id=categorias_ejemplo[0].id),
                Producto(nombre="Laptop", precio=1200.0, categoria_id=categorias_ejemplo[0].id),
                Producto(nombre="Camiseta", precio=20.0, categoria_id=categorias_ejemplo[1].id),
                Producto(nombre="Sofá", precio=800.0, categoria_id=categorias_ejemplo[2].id),
            ]
            db.session.add_all(productos_ejemplo)
            db.session.commit()

        # Inicializar Ciudades
        if not Ciudad.query.first():  # Verifica si la tabla de ciudades está vacía
            ciudades_ejemplo = [
                Ciudad(nombre="Madrid", lat=40.4168, lon=-3.7038),
                Ciudad(nombre="Barcelona", lat=41.3879, lon=2.16992),
                Ciudad(nombre="Sevilla", lat=37.3886, lon=-5.9823),
                Ciudad(nombre="Valencia", lat=39.4699, lon=-0.3763),
                Ciudad(nombre="Bilbao", lat=43.2630, lon=-2.9350),
            ]
            db.session.add_all(ciudades_ejemplo)
            db.session.commit()

    # Registrar las rutas
    app.register_blueprint(routes.main)

    return app
