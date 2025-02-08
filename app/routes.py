from flask import Blueprint, render_template, request, redirect, url_for, Flask
from flask import jsonify,flash
from app.models import Categoria, Producto, Ciudad
from app_db import db
import os # Para leer variables de entorno
import requests
import folium
from geopy.distance import geodesic # Para calcular distancias entre ciudades
import openai
import json
from werkzeug.utils import secure_filename 
import cv2
import numpy as np
from collections import Counter  # 📌 Importar Counter para contar los colores más frecuentes
from sklearn.cluster import KMeans  # 📌


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}




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

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ruta para generar imágenes
@main.route('/generate-image', methods=['POST'])
def generate_image():

    try:
        # Obtener el prompt del formulario
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            return jsonify({'error': 'El campo de descripción está vacío.'}), 400

        # Solicitar la generación de la imagen usando ChatCompletion
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un generador de imágenes."},
                {"role": "user", "content": f"Genera una imagen basada en el siguiente texto: {prompt}"}
            ],
            functions=[
                {
                    "name": "generate_image",
                    "description": "Generar imágenes con DALL-E",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Texto descriptivo para la imagen."},
                            "n": {"type": "integer", "description": "Número de imágenes a generar.", "default": 1},
                            "size": {
                                "type": "string",
                                "description": "Tamaño de la imagen, e.g., '1024x1024'.",
                                "default": "1024x1024"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            ]
        )

        # Verificar si el modelo devolvió una llamada a la función
        function_call = response.get("choices", [{}])[0].get("message", {}).get("function_call")
        if not function_call or function_call.get("name") != "generate_image":
            raise ValueError("La respuesta del modelo no contiene una llamada a 'generate_image'.")

        # Extraer los argumentos de la función
        arguments = json.loads(function_call.get("arguments", "{}"))
        prompt_for_image = arguments.get("prompt", prompt)
        n = arguments.get("n", 1)
        size = arguments.get("size", "1024x1024")

        # Solicitar la imagen a la API de DALL-E
        image_response = openai.Image.create(
            prompt=prompt_for_image,
            n=n,
            size=size
        )

        # Obtener la URL de la imagen generada
        image_url = image_response['data'][0]['url']

        # Renderizar el resultado
        return render_template('image_result.html', image_url=image_url, home_url=url_for('main.home'))

        


    except Exception as e:
        print(f"Error generando la imagen: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/tsp', methods=['GET', 'POST'])
def tsp():
    if request.method == 'GET':
        # Mostrar la página con el formulario de selección de ciudades
        ciudades = Ciudad.query.all()  # Obtener todas las ciudades de la base de datos
        return render_template('tsp_form.html', ciudades=ciudades)
    
    if request.method == 'POST':

        # Procesar la selección de ciudades
        ciudades_seleccionadas_ids = request.form.getlist('ciudades')
        ciudades_seleccionadas = Ciudad.query.filter(Ciudad.id.in_(ciudades_seleccionadas_ids)).all()
        print("Ciudades seleccionadas IDs:", ciudades_seleccionadas_ids)

        if len(ciudades_seleccionadas_ids) != 15:
            flash("Por favor selecciona exactamente 15 ciudades.", "error")
            return redirect(url_for('main.tsp'))
        
        print([(ciudad.nombre, ciudad.lat, ciudad.lon) for ciudad in ciudades_seleccionadas])
        # Consultar las ciudades seleccionadas en la base de datos


        

        # Generar el mapa
        try:
            mapa = generar_mapa(ciudades_seleccionadas)
            mapa.save(os.path.join('app', 'static', 'mapa_seleccionado.html'))
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
            mapa='static/mapa_seleccionado.html',
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
    # Verificar si las ciudades tienen coordenadas válidas
    if not ciudades:
        return None  # Si no hay ciudades, retornar None

    # Crear el mapa centrado en la primera ciudad
    coordenadas = [(ciudad.lat, ciudad.lon) for ciudad in ciudades]  # Obtener las coordenadas de cada ciudad

    # Verificar si las coordenadas no están vacías
    if not coordenadas:
        return None  # Si no se obtienen coordenadas, retornar None

    # Crear el mapa en Folium
    mapa = folium.Map(location=coordenadas[0], zoom_start=6)

    # Añadir los marcadores de las ciudades al mapa
    for lat, lon in coordenadas:
        folium.Marker([lat, lon]).add_to(mapa)

    return mapa  # Retornar el mapa



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

@main.route('/rubik', methods=['GET'])
def rubik_home():
    return render_template('rubik.html')


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@main.route('/upload-rubik', methods=['POST'])
def upload_rubik_images():
    if 'files[]' not in request.files:
        return render_template("rubik.html", message="Error: No se enviaron archivos.")

    files = request.files.getlist('files[]')

    if len(files) != 6:
        return render_template("rubik.html", message="Debes subir exactamente 6 imágenes.")

    #os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    face_names = ["UP", "DOWN", "LEFT", "RIGHT", "FRONT", "BACK"]
    
    for i, file in enumerate(files):
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{face_names[i]}.jpg")
            file_path = os.path.join("app/static/uploads", filename)
            file.save(file_path)

    return render_template("rubik.html", message="Imágenes subidas correctamente.")

# Definir los rangos de colores en HSV para cada sticker y los procesamos en forma legible para el algoritmo

def obtener_colores_dominantes(image_path, k=6):
    """Detecta los colores más dominantes en la imagen usando K-Means."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: No se pudo cargar la imagen {image_path}")
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convertimos a HSV
    img = img.reshape((-1, 3))  # Convertimos a una lista de píxeles

    # Usar K-Means para encontrar los k colores dominantes
    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(img)
    colores = kmeans.cluster_centers_.astype(int)

    return colores  # Retorna los valores HSV de los colores detectados


def detectar_color(hsv_pixel, colores_dominantes):
    """Compara un píxel HSV con los colores dominantes de la imagen y encuentra la mejor coincidencia."""
    distancias = [
        (color, np.linalg.norm(hsv_pixel - color)) for color in colores_dominantes
    ]
    color_mas_cercano = min(distancias, key=lambda x: x[1])[0]  # Encuentra el color más cercano
    return str(color_mas_cercano)


def detectar_color_hsv(hsv_region, colores_dominantes):
    """Promedia una región de píxeles y detecta el color basado en HSV."""
    if hsv_region is None or hsv_region.size == 0:
        return "?"

    if hsv_region.ndim < 2:
        print(f"Advertencia: hsv_region con dimensiones inesperadas: {hsv_region.shape}")
        return "?"

    avg_hsv = np.median(hsv_region.reshape(-1, 3), axis=0)  # Usa mediana en lugar de promedio
    color_detectado = detectar_color(avg_hsv, colores_dominantes)


    return str(color_detectado)  # ✅ Ahora `detectar_color()` usa los colores dinámicos





def procesar_imagen_cubo(image_path):
    """Procesa una imagen y detecta los colores de los 9 stickers."""
    img = cv2.imread(image_path)
    if img is None:
        return None  # Evita continuar si la imagen no se pudo leer

    img = cv2.resize(img, (300, 300))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ✅ Obtener los colores dominantes en la imagen
    colores_dominantes = obtener_colores_dominantes(image_path)

    # ✅ Aumentar saturación y brillo
    hsv[:, :, 1] = cv2.add(hsv[:, :, 1], 50)
    hsv[:, :, 2] = cv2.add(hsv[:, :, 2], 30)

    posiciones = [
        (50, 50), (150, 50), (250, 50),
        (50, 150), (150, 150), (250, 150),
        (50, 250), (150, 250), (250, 250)
    ]

    colores_detectados = []
    for pos in posiciones:
        x, y = pos
        region = hsv[y-10:y+10, x-10:x+10]  # Extraemos una región

        if region.size == 0:
            region = hsv[y, x].reshape(1, 1, 3)  # Usamos el píxel central si la región está vacía

        color = detectar_color_hsv(region, colores_dominantes)  # Comparamos con los colores dinámicos
        colores_detectados.append(color)

    return colores_detectados




@main.route('/procesar-cubo', methods=['GET'])
def procesar_cubo():
    """Procesa las imágenes subidas y genera la representación del cubo."""
    face_names = ["UP", "DOWN", "LEFT", "RIGHT", "FRONT", "BACK"]
    estado_cubo = {}

    for face in face_names:
        image_path = f"app/static/uploads/{face}.jpg"
        colores = procesar_imagen_cubo(image_path)
        if colores is None:
            return render_template("rubik.html", message=f"Error procesando {face}.jpg")
        estado_cubo[face] = "".join(colores)  # Convertir lista a string

    return render_template("rubik.html", message="Colores detectados correctamente", estado_cubo=estado_cubo)
