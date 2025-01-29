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

        # Verificar que la matriz se almacena correctamente en sesión
        session['matriz_distancias'] = matriz
        session['ciudades'] = [c.nombre for c in ciudades_seleccionadas]

        print("Matriz guardada en sesión:", session['matriz_distancias'])  # Agrega este print para depuración
    

        # Renderizar resultado
        return render_template(
            'tsp_result.html',
            mapa='static/mapa.html',
            matriz_con_indices=matriz_con_indices,
            ciudades=[c.nombre for c in ciudades_seleccionadas]
        )


from flask import session, jsonify
import numpy as np
from app.heuristica_tsp import heuristica_tsp  # Importamos el algoritmo heurístico

@main.route('/resolver-tsp', methods=['POST'])
def resolver_tsp():
    """Ejecuta la heurística TSP sobre la matriz almacenada y devuelve JSON."""
    if 'matriz_distancias' not in session:
        return jsonify({'error': 'No hay una matriz almacenada en la sesión'}), 400

    matriz = np.array(session['matriz_distancias'])

    if matriz.ndim != 2:
        return jsonify({'error': 'La matriz de distancias no tiene el formato correcto'}), 500

    ruta_heuristica = heuristica_tsp(matriz)

    # Calcular la distancia total recorrida
    distancia_total = sum(matriz[ruta_heuristica[i]][ruta_heuristica[i + 1]] for i in range(len(ruta_heuristica) - 1))

    # Guardar la ruta optimizada en sesión
    session['ruta_heuristica'] = ruta_heuristica

    # Crear el mapa con la ruta optimizada
    coordenadas_ciudades = {ciudad.nombre: (ciudad.lat, ciudad.lon) for ciudad in Ciudad.query.filter(Ciudad.nombre.in_(session['ciudades'])).all()}
    ruta_coordenadas = [coordenadas_ciudades[session['ciudades'][i]] for i in ruta_heuristica]

    # Crear el mapa
    mapa_ruta = folium.Map(location=ruta_coordenadas[0], zoom_start=6)
    folium.PolyLine(ruta_coordenadas, color="blue", weight=5, opacity=0.7).add_to(mapa_ruta)

    # Guardar el mapa en el directorio static
    mapa_ruta.save(os.path.join('app','static','mapa_ruta_optima.html'))

    print("Mapa generado y guardado en app/static/mapa_ruta_optima.html")  # Depuración

    # Retornar los datos de la ruta y la URL del mapa
    return jsonify({
        'ruta': [session['ciudades'][i] for i in ruta_heuristica],
        'orden_ids': ruta_heuristica,
        'distancia_total': round(distancia_total, 2),
        'mapa_ruta': "static/mapa_ruta_optima.html"  # Retornamos la URL del mapa generado
    })




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




@main.route('/ruta-optima', methods=['GET'])
def ruta_optima():

    """Genera y muestra un mapa con la ruta óptima."""
    if 'ruta_heuristica' not in session or 'ciudades' not in session:
        flash("No hay una ruta optimizada disponible. Selecciona ciudades primero.", "error")
        return redirect(url_for('main.tsp'))

    ciudades = session['ciudades']
    ruta_heuristica = session['ruta_heuristica']

    # Crear el mapa centrado en la primera ciudad
    coordenadas_ciudades = [ciudad.latlon for ciudad in Ciudad.query.filter(Ciudad.nombre.in_(ciudades)).all()]
    ruta_coordenadas = [coordenadas_ciudades[ciudades[i]] for i in ruta_heuristica]

    mapa_ruta = folium.Map(location=coordenadas_ciudades[0], zoom_start=6)

    # Añadir marcadores
    for i, ciudad in enumerate(ruta_heuristica):
        folium.Marker(coordenadas_ciudades[ciudad], tooltip=ciudades[ciudad]).add_to(mapa_ruta)

    # Dibujar la ruta óptima en el mapa
    folium.PolyLine([coordenadas_ciudades[i] for i in ruta_heuristica], color="blue", weight=5, opacity=0.7).add_to(mapa_ruta)

    # Guardar el mapa como HTML
    mapa_ruta.save("static/mapa_ruta_optima.html")

    return render_template("ruta_optima.html", mapa_ruta="static/mapa_ruta_optima.html")
