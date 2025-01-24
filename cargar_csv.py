import csv
from app import create_app, db
from app.models import Registro

app = create_app()

with app.app_context():
    with open('datos.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nuevo_registro = Registro(nombre=row['nombre'], valor=row['valor'])
            db.session.add(nuevo_registro)
        db.session.commit()
    print("Registros añadidos desde CSV correctamente.")
