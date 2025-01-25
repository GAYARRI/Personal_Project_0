from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Registro
from app_db import db
import os

# Definir el Blueprint
main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        valor = request.form.get('valor')

        # Validar campos
        if not nombre or not valor:
            flash("Todos los campos son obligatorios", "error")
        elif Registro.query.filter_by(nombre=nombre).first():
            flash("Ya existe un registro con este nombre", "error")
        else:
            # Añadir un nuevo registro
            nuevo_registro = Registro(nombre=nombre, valor=valor)
            db.session.add(nuevo_registro)
            db.session.commit()
            flash("Registro añadido con éxito", "success")

        # Redirigir a la misma página para evitar reenvío del formulario
        return redirect(url_for('main.home'))

    # Consultar registros para mostrar en la tabla
    registros = Registro.query.all()
    print("Registros obtenidos:", registros)  # Depuración
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
    print("Prompt recibido:", prompt)  # Depuración
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        flash("Error: La clave de OpenAI no está configurada como variable de entorno.", "error")
        return redirect(url_for('main.home'))


    # Simulación de la generación de imagen con DALL-E
    # Cambia esto para usar la API de DALL-E con tu clave
    dall_e_url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": "Bearer TU_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "256x256"
    }

    try:
        response = requests.post(dall_e_url, headers=headers, json=data)

        # Depurar la respuesta completa de la API
        print("Respuesta completa de la API:", response.text)

        response_data = response.json()
        imagen_url = response_data['data'][0]['url']  # URL de la imagen generada

    except requests.exceptions.RequestException as e:
        flash(f"Error al generar la imagen: {str(e)}", "error")
        imagen_url = None
    except KeyError:
        flash("Error en la respuesta de la API. No se pudo generar la imagen.", "error")
        imagen_url = None

    registros = Registro.query.all()
    return render_template('home.html', registros=registros, imagen_url=imagen_url)    

    
