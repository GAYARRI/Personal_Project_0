
from flask import Blueprint, render_template
from app.models import Registro

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Consultar todos los registros
    registros = Registro.query.all()
    return render_template('registros.html', registros=registros)
