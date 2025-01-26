from app_db import db
from app import create_app
from app.models import Categoria, Producto

# Crear la aplicación y establecer el contexto
app = create_app()
with app.app_context():
    db.create_all()  # Crear tablas si no existen

    # Insertar datos de ejemplo
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

    print("Base de datos inicializada con datos de ejemplo.")

