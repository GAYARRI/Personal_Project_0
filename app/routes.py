from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Categoria, Producto, Ciudad
from app_db import db
import os # Para leer variables de entorno
import requests
import folium
from geopy.distance import geodesic # Para calcular distancias entre ciudades



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
        "size": "512x512",
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


@main.route('/tsp', methods=['GET', 'POST'])
def tsp():
    if request.method == 'GET':
        # Mostrar la página con el formulario de selección de ciudades
        ciudades = Ciudad.query.all()  # Obtener todas las ciudades de la base de datos
        return render_template('tsp_form.html', ciudades=ciudades)
    
    if request.method == 'POST':
        # Procesar la selección de ciudades
        ciudades_seleccionadas_ids = request.form.getlist('ciudades')
        print("Ciudades seleccionadas IDs:", ciudades_seleccionadas_ids)

        if len(ciudades_seleccionadas_ids) != 15:
            flash("Por favor selecciona exactamente 15 ciudades.", "error")
            return redirect(url_for('main.tsp'))
        

        # Consultar las ciudades seleccionadas en la base de datos

        ciudades_seleccionadas = Ciudad.query.filter(Ciudad.id.in_(ciudades_seleccionadas_ids)).all()

        print([(ciudad.nombre, ciudad.lat, ciudad.lon) for ciudad in ciudades_seleccionadas])


        # Generar el mapa
        try:
            mapa = generar_mapa(ciudades_seleccionadas)
        except Exception as e:
            print("Error al generar el mapa:", e)
            flash("Error al generar el mapa.", "error")
            return redirect(url_for('main.tsp'))

        # Calcular la matriz de distancias
        try:
            matriz = calcular_distancias(ciudades_seleccionadas)
            print("Matriz generada:", matriz)
            if not matriz:
                raise ValueError("La matriz de distancias está vacía.")
        except Exception as e:
            print("Error al calcular la matriz de distancias:", e)
            flash("No se pudo generar la matriz de distancias.", "error")
            return redirect(url_for('main.tsp'))

        # Construir matriz con índices
        matriz_con_indices = []
        for i, fila in enumerate(matriz):
            matriz_con_indices.append({
                'ciudad': ciudades_seleccionadas[i].nombre,
                'distancias': fila
            })

        # Renderizar resultado
        return render_template(
            'tsp_result.html',
            mapa='static/mapa.html',
            matriz_con_indices=matriz_con_indices,
            ciudades=[c.nombre for c in ciudades_seleccionadas]
        )






import folium

@main.route('/mostrar-mapa', methods=['GET'])
def generar_mapa(ciudades):
    print("se reciben las ciudades seleccionadas")
    ids = request.args.get('ids', '')  # Recuperar IDs de las ciudades seleccionadas
    ids = [int(id_) for id_ in ids.split(',') if id_]  # Convertirlos a lista de enteros
    
    ciudades = Ciudad.query.filter(Ciudad.id.in_(ids)).all()  # Obtener las ciudades seleccionadas
    
    # Crear el mapa centrado en España
    mapa = folium.Map(location=[40.416775, -3.703790], zoom_start=6)
    
    # Añadir marcadores para cada ciudad
    for ciudad in ciudades:
        folium.Marker([ciudad.lat, ciudad.lon], tooltip=ciudad.nombre).add_to(mapa)
    
    mapa_html = mapa._repr_html_()  # Generar el mapa en HTM



def calcular_distancias(ciudades):
    try:
        coordenadas = [(ciudad.lat, ciudad.lon) for ciudad in ciudades]
        print("Coordenadas de las ciudades seleccionadas:", coordenadas)

        matriz = []
        for ciudad1 in coordenadas:
            fila = []
            for ciudad2 in coordenadas:
                distancia = geodesic(ciudad1, ciudad2).kilometers
                fila.append(round(distancia, 2))
            matriz.append(fila)
        print("Matriz calculada correctamente:", matriz)
        return matriz       

    except Exception as e:
        print("Error al calcular las distancias.", e)
        return None





