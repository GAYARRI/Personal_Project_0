from app_db import db
from app.models import Ciudad
from app import create_app

# Crear la aplicación Flask
app = create_app()

# Lista de capitales de provincia con coordenadas
ciudades = [
    {"nombre": "A Coruña", "lat": 43.3623, "lon": -8.4115},
    {"nombre": "Álava", "lat": 42.8431, "lon": -2.6699},
    {"nombre": "Albacete", "lat": 38.995, "lon": -1.8564},
    {"nombre": "Alicante", "lat": 38.3452, "lon": -0.4815},
    {"nombre": "Almería", "lat": 36.834, "lon": -2.4637},
    {"nombre": "Asturias", "lat": 43.3619, "lon": -5.8494},
    {"nombre": "Ávila", "lat": 40.6564, "lon": -4.6818},
    {"nombre": "Badajoz", "lat": 38.8786, "lon": -6.9702},
    {"nombre": "Barcelona", "lat": 41.3888, "lon": 2.159},
    {"nombre": "Burgos", "lat": 42.3439, "lon": -3.6969},
    {"nombre": "Cáceres", "lat": 39.4752, "lon": -6.3722},
    {"nombre": "Cádiz", "lat": 36.5164, "lon": -6.2994},
    {"nombre": "Cantabria", "lat": 43.4636, "lon": -3.8044},
    {"nombre": "Castellón", "lat": 39.9864, "lon": -0.0513},
    {"nombre": "Ciudad Real", "lat": 38.9861, "lon": -3.9291},
    {"nombre": "Córdoba", "lat": 37.8847, "lon": -4.7792},
    {"nombre": "Cuenca", "lat": 40.0718, "lon": -2.1374},
    {"nombre": "Girona", "lat": 41.9794, "lon": 2.8214},
    {"nombre": "Granada", "lat": 37.1773, "lon": -3.5986},
    {"nombre": "Guadalajara", "lat": 40.6335, "lon": -3.1669},
    {"nombre": "Guipúzcoa", "lat": 43.312, "lon": -1.9844},
    {"nombre": "Huelva", "lat": 37.2614, "lon": -6.9447},
    {"nombre": "Huesca", "lat": 42.1401, "lon": -0.4089},
    {"nombre": "Jaén", "lat": 37.7796, "lon": -3.7849},
    {"nombre": "La Rioja", "lat": 42.465, "lon": -2.448},
    {"nombre": "Las Palmas", "lat": 28.1235, "lon": -15.4363},
    {"nombre": "León", "lat": 42.5987, "lon": -5.5671},
    {"nombre": "Lleida", "lat": 41.6167, "lon": 0.6222},
    {"nombre": "Lugo", "lat": 43.0097, "lon": -7.556},
    {"nombre": "Madrid", "lat": 40.4168, "lon": -3.7038},
    {"nombre": "Málaga", "lat": 36.7213, "lon": -4.421},
    {"nombre": "Murcia", "lat": 37.9834, "lon": -1.1299},
    {"nombre": "Navarra", "lat": 42.8169, "lon": -1.6432},
    {"nombre": "Ourense", "lat": 42.336, "lon": -7.864},
    {"nombre": "Palencia", "lat": 42.0118, "lon": -4.5312},
    {"nombre": "Pontevedra", "lat": 42.4335, "lon": -8.6478},
    {"nombre": "Salamanca", "lat": 40.9701, "lon": -5.6635},
    {"nombre": "Santa Cruz de Tenerife", "lat": 28.4636, "lon": -16.2518},
    {"nombre": "Segovia", "lat": 40.9481, "lon": -4.1184},
    {"nombre": "Sevilla", "lat": 37.3886, "lon": -5.9823},
    {"nombre": "Soria", "lat": 41.764, "lon": -2.4675},
    {"nombre": "Tarragona", "lat": 41.1167, "lon": 1.25},
    {"nombre": "Teruel", "lat": 40.3441, "lon": -1.1069},
    {"nombre": "Toledo", "lat": 39.8628, "lon": -4.0273},
    {"nombre": "Valencia", "lat": 39.4699, "lon": -0.3751},
    {"nombre": "Valladolid", "lat": 41.6523, "lon": -4.7245},
    {"nombre": "Vizcaya", "lat": 43.263, "lon": -2.935},
    {"nombre": "Zamora", "lat": 41.5033, "lon": -5.7445},
    {"nombre": "Zaragoza", "lat": 41.6488, "lon": -0.8891}
]

   

# Iniciar el contexto de la aplicación
from app import create_app
app = create_app()

with app.app_context():
    # Vaciar la tabla
    db.session.query(Ciudad).delete()
    db.session.commit()

    # Insertar datos
    for ciudad in ciudades:
        nueva_ciudad = Ciudad(nombre=ciudad["nombre"], lat=ciudad["lat"], lon=ciudad["lon"])
        db.session.add(nueva_ciudad)
    db.session.commit()

print("Ciudades inicializadas correctamente.")
