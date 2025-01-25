from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Cambia el host
print(f"Base de datos usada: {app.config['SQLALCHEMY_DATABASE_URI']}")