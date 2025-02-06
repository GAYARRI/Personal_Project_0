from app import create_app
import sys

venv_path = "C:\\Users\\gayar\\Personal_Project\\PPR0"
if sys.prefix != venv_path:
    activate_this = os.path.join(venv_path, "Scripts", "activate_this.py")
    exec(open(activate_this).read(), dict(__file__=activate_this))





app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)  # Cambia el host
print(f"Base de datos usada: {app.config['SQLALCHEMY_DATABASE_URI']}")