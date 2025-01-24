from app import create_app
from app_db import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run(debug=True)
