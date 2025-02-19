
import random
from app import create_app
from app_db import db
from app.models import Categoria, Producto, Cliente, Compra
from datetime import datetime, timedelta

PROVINCIAS = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga", "Zaragoza", "Murcia", "Alicante", "Valladolid"]

app = create_app()

with app.app_context():
    print("🔄 Eliminando y creando la base de datos...")
    db.drop_all()
    db.create_all()

    # 📌 Insertar Categorías
    categorias = [Categoria(nombre=f"Categoría {i+1}") for i in range(10)]
    db.session.add_all(categorias)
    db.session.commit()

    # 📌 Insertar Productos
    productos = [Producto(nombre=f"Producto {i+1}", precio=random.uniform(5, 2000), categoria_id=random.choice(categorias).id) for i in range(250)]
    db.session.add_all(productos)
    db.session.commit()

    # 📌 Insertar Clientes
    clientes = [Cliente(nombre=f"Cliente {i+1}", apellidos="Apellido", direccion=f"Calle {i+1}", provincia=random.choice(PROVINCIAS), edad=random.randint(18, 80)) for i in range(75)]
    db.session.add_all(clientes)
    db.session.commit()

    # 📌 Insertar Compras
    compras = []
    for _ in range(500):  # 🔹 Generamos 100 compras ficticias
        producto = random.choice(productos)  # Producto aleatorio
        cliente = random.choice(clientes)  # Cliente aleatorio
        unidades_peso = round(random.uniform(1, 10), 2)  # Cantidad entre 1 y 10 unidades/kg
        fecha = datetime.utcnow() - timedelta(days=random.randint(1, 365))  # Fecha aleatoria en el último año
        provincia_compra = cliente.provincia  # La provincia de compra es la del cliente

        compras.append(Compra(
            producto_id=producto.id,
            cliente_id=cliente.id,
            unidades_peso=unidades_peso,
            fecha=fecha,
            provincia_compra=provincia_compra
        ))

    db.session.add_all(compras)
    db.session.commit()

    print("✅ Base de datos inicializada con Compras vinculadas a Productos y Clientes.")
