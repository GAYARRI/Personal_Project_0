from flask import Flask
from app_db import db
from app.models import Categoria, Producto  # Importar las nuevas clases de modelo
from app import routes

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)

    # Insertar datos de ejemplo si no existen
    with app.app_context():
        db.create_all()
        if not Categoria.query.first():  # Verifica si la tabla de categorías está vacía
            # Insertar categorías de ejemplo
            categorias_ejemplo = [
                Categoria(nombre="Electrónica"),
                Categoria(nombre="Ropa"),
                Categoria(nombre="Hogar"),
            ]
            db.session.add_all(categorias_ejemplo)
            db.session.flush()  # Asegura que las categorías tengan IDs asignados

            # Insertar productos de ejemplo
            productos_ejemplo = [
                Producto(nombre="Teléfono", precio=500.0, categoria_id=categorias_ejemplo[0].id),
                Producto(nombre="Laptop", precio=1200.0, categoria_id=categorias_ejemplo[0].id),
                Producto(nombre="Camiseta", precio=20.0, categoria_id=categorias_ejemplo[1].id),
                Producto(nombre="Sofá", precio=800.0, categoria_id=categorias_ejemplo[2].id),
            ]
            db.session.add_all(productos_ejemplo)
            db.session.commit()

    # Registrar las rutas
    app.register_blueprint(routes.main)

    return app
