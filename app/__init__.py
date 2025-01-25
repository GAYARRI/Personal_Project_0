from flask import Flask,request

from app_db import db
from app.models import Registro

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')



    # Inicializar extensiones
    db.init_app(app)

    # Insertar datos de ejemplo si no existen
    with app.app_context():
        db.create_all()
        if not Registro.query.first():  # Verifica si la tabla está vacía
            datos_ejemplo = [
                Registro(nombre="Ejemplo 1", valor="123"),
                Registro(nombre="Ejemplo 2", valor="456"),
                Registro(nombre="Ejemplo 3", valor="789"),
            ]
            db.session.add_all(datos_ejemplo)
            db.session.commit()

    # Registrar las rutas
    from app import routes
    app.register_blueprint(routes.main)

    return app
