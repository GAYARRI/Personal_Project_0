import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.models import Registro
from app_db import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        valor = request.form.get('valor')
        prompt = request.form.get('prompt')

        if not nombre or not valor:
            flash("Todos los campos son obligatorios", "error")
        elif Registro.query.filter_by(nombre=nombre).first():
            flash("Ya existe un registro con este nombre", "error")
        else:
            nuevo_registro = Registro(nombre=nombre, valor=valor)
            db.session.add(nuevo_registro)
            db.session.commit()
            flash("Registro añadido con éxito", "success")

        return redirect(url_for('main.home'))

    registros = Registro.query.all()
    return render_template('home.html', registros=registros)

@main.route('/borrar/<int:id>', methods=['POST'])
def borrar(id):
    registro = Registro.query.get_or_404(id)
    db.session.delete(registro)
    db.session.commit()
    flash("Registro eliminado con éxito", "success")
    return redirect(url_for('main.home'))

@main.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    registro = Registro.query.get_or_404(id)

    if request.method == 'POST':
        registro.nombre = request.form['nombre']
        registro.valor = request.form['valor']
        db.session.commit()
        flash("Registro actualizado con éxito", "success")
        return redirect(url_for('main.home'))

    return render_template('editar.html', registro=registro)

@main.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.form.get('prompt')
    if not prompt:
        flash("Debes proporcionar un prompt para generar la imagen", "error")
        return redirect(url_for('main.home'))

    # Configuración de la API de OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        flash("Error: La clave de OpenAI no está configurada como variable de entorno.", "error")
        return redirect(url_for('main.home'))

    # Llamada al API de OpenAI
    dall_e_url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "256x256"
    }

    try:
        response = requests.post(dall_e_url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        imagen_url = response_data['data'][0]['url']  # URL de la imagen generada
        flash("Imagen generada con éxito.", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Error al generar la imagen: {str(e)}", "error")
        return redirect(url_for('main.home'))
    except KeyError:
        flash("Error en la respuesta de la API. No se pudo generar la imagen.", "error")
        return redirect(url_for('main.home'))

    # Redirigir y mostrar la imagen generada
    return render_template('home.html', imagen_url=imagen_url, registros=Registro.query.all())
