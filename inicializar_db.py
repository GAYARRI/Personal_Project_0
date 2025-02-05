from app_db import db
from app import create_app
from app.models import Categoria, Producto,Ciudad

# Crear la aplicación y establecer el contexto
app = create_app()
with app.app_context():
    db.create_all(checkfirst=True)  # Crear tablas si no existen

with app.app_context():
    # Insertar categorías
    categorias = [
        Categoria(nombre="Electrónica"),
        Categoria(nombre="Hogar"),
        Categoria(nombre="Ropa"),
    ]
    db.session.add_all(categorias)
    db.session.commit()

    # Insertar productos
    productos = [
        Producto(nombre="Teléfono", precio=699.99, categoria_id=1),
        Producto(nombre="Aspiradora", precio=199.99, categoria_id=2),
        Producto(nombre="Camiseta", precio=29.99, categoria_id=3),
    ]
    db.session.add_all(productos)
    db.session.commit()

    # Insertar ciudades
    ciudades = [
        Ciudad(nombre="Madrid", lat=40.4168, lon=-3.7038),
        Ciudad(nombre="Barcelona", lat=41.3851, lon=2.1734),
        Ciudad(nombre="Valencia", lat=39.4699, lon=-0.3763),
    ]
    db.session.add_all(ciudades)
    db.session.commit()

    print("Datos iniciales insertados en las tablas.") 
