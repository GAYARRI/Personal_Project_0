from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Categoria, Producto
from app_db import db
import os # Para leer variables de entorno
import requests

main = Blueprint('main', __name__)

# Gestión de categorías
@main.route('/categorias', methods=['GET', 'POST'])
def categorias():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "error")
        else:
            nueva_categoria = Categoria(nombre=nombre)
            db.session.add(nueva_categoria)
            db.session.commit()
            flash("Categoría añadida con éxito.", "success")
    categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=categorias)

@main.route('/categorias/borrar/<int:id>', methods=['POST'])
def borrar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoría eliminada con éxito.", "success")
    return redirect(url_for('main.categorias'))

# Gestión de productos
@main.route('/productos', methods=['GET', 'POST'])
def productos():
    categorias = Categoria.query.all()
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        categoria_id = request.form.get('categoria_id')
        if not nombre or not precio or not categoria_id:
            flash("Todos los campos son obligatorios.", "error")
        else:
            nuevo_producto = Producto(nombre=nombre, precio=float(precio), categoria_id=int(categoria_id))
            db.session.add(nuevo_producto)
            db.session.commit()
            flash("Producto añadido con éxito.", "success")
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos, categorias=categorias)

@main.route('/productos/borrar/<int:id>', methods=['POST'])
def borrar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado con éxito.", "success")
    return redirect(url_for('main.productos'))

# Resumen por categorías
@main.route('/resumen', methods=['GET'])
def resumen():
    resumen = db.session.query(
        Categoria.nombre,
        db.func.count(Producto.id).label('total_productos'),
        db.func.sum(Producto.precio).label('suma_precios'),
        db.func.avg(Producto.precio).label('promedio_precio')
    ).join(Producto, Categoria.id == Producto.categoria_id).group_by(Categoria.id).all()
    return render_template('resumen.html', resumen=resumen)

@main.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# Ruta para generar imágenes
@main.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.form.get('prompt')
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        flash("Error: Falta la clave de API de OpenAI.", "error")
        return redirect(url_for('main.home'))

    # Configuración de la solicitud a la API de DALL-E
    dall_e_url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "256x256",
    }

    try:
        response = requests.post(dall_e_url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        imagen_url = response_data['data'][0]['url']
    except requests.exceptions.RequestException as e:
        flash(f"Error al generar la imagen: {e}", "error")
        return redirect(url_for('main.home'))
    except KeyError:
        flash("Error en la respuesta de la API.", "error")
        return redirect(url_for('main.home'))

    return render_template('home.html', imagen_url=imagen_url)