from flask import Blueprint, render_template, request, redirect, url_for, Flask
from flask import jsonify,flash
from app.models import Categoria, Producto, Ciudad, Cliente, Compra
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
from flask import session, jsonify
import numpy as np
from app.heuristica_tsp import heuristica_tsp  # Importamos el algoritmo heurístic
from sklearn.cluster import KMeans
import base64
import numpy as np
from skimage.color import rgb2lab
from PIL import Image
from io import BytesIO
import re
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io




ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = "app/static/uploads"



main = Blueprint('main', __name__)


# Getion de Compras
@main.route('/compras', methods=['GET'])
def compras():
    compras = Compra.query.all()
    return render_template('compras.html', compras=compras)


@main.route('/agregar_compra', methods=['POST'])
def agregar_compra():
    producto_id = request.form.get('producto_id')
    cliente_id = request.form.get('cliente_id')
    unidades_peso = request.form.get('unidades_peso')
    fecha = request.form.get('fecha')
    provincia_compra = request.form.get('provincia_compra')

    if not producto_id or not cliente_id or not unidades_peso or not fecha or not provincia_compra:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for('main.compras'))

    try:
        nueva_compra = Compra(
            producto_id=int(producto_id),
            cliente_id=int(cliente_id),
            unidades_peso=float(unidades_peso),
            fecha=datetime.strptime(fecha, '%Y-%m-%d'),
            provincia_compra=provincia_compra
        )
        db.session.add(nueva_compra)
        db.session.commit()
        flash("Compra añadida con éxito.", "success")
    except ValueError:
        flash("Error en los datos ingresados.", "error")

    return redirect(url_for('main.compras'))


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

        # Validaciones antes de insertar en la BD
        if not nombre or not precio or not categoria_id:
            flash("Todos los campos son obligatorios.", "error")
        else:
            try:
                precio = float(precio)  # Convertir precio a float
                categoria_id = int(categoria_id)  # Convertir ID a entero
                nuevo_producto = Producto(nombre=nombre, precio=precio, categoria_id=categoria_id)
                db.session.add(nuevo_producto)
                db.session.commit()
                flash("Producto añadido con éxito.", "success")
            except ValueError:
                flash("El precio debe ser un número válido.", "error")

    productos = Producto.query.all()
    return render_template('productos.html', productos=productos, categorias=categorias)   

@main.route('/productos/borrar/<int:id>', methods=['POST'])
def borrar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado con éxito.", "success")
    return redirect(url_for('main.productos'))

# 📌 Ruta para ver clientes
@main.route('/clientes', methods=['GET'])
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

# 📌 Ruta para agregar un cliente
@main.route('/clientes', methods=['POST'])
def agregar_cliente():
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    direccion = request.form.get('direccion')
    provincia = request.form.get('provincia')
    edad = request.form.get('edad')

    if not nombre or not apellidos or not direccion or not provincia or not edad:
        flash("Todos los campos son obligatorios.", "error")
    else:
        try:
            edad = int(edad)
            nuevo_cliente = Cliente(
                nombre=nombre, apellidos=apellidos, 
                direccion=direccion, provincia=provincia, edad=edad
            )
            db.session.add(nuevo_cliente)
            db.session.commit()
            flash("Cliente añadido con éxito.", "success")
        except ValueError:
            flash("La edad debe ser un número válido.", "error")

    return redirect(url_for('main.clientes'))

# 📌 Ruta para eliminar un cliente
@main.route('/clientes/borrar/<int:id>', methods=['POST'])
def borrar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado con éxito.", "success")
    return redirect(url_for('main.clientes'))

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


@main.route('/dashboard')
def dashboard():
    # Obtener datos de la base de datos
    compras = Compra.query.all()

    # Convertir datos a un DataFrame de Pandas
    data = [
        {
            "categoria": compra.producto.categoria.nombre,
            "provincia": compra.provincia_compra,
            "fecha": compra.fecha.strftime('%Y-%m-%d'),
            "unidades_peso": compra.unidades_peso
        }
        for compra in compras
    ]

    df = pd.DataFrame(data)

    # 📊 1️⃣ Compra Media Totalizada por Categoría
    df_categoria = df.groupby("categoria")["unidades_peso"].mean()
    img_categoria = plot_to_base64(df_categoria, "Compra Media por Categoría", "Categoría", "Compra Media (kg/unidades)")

    # 📊 2️⃣ Compra Media Totalizada por Provincia
    df_provincia = df.groupby("provincia")["unidades_peso"].mean()
    img_provincia = plot_to_base64(df_provincia, "Compra Media por Provincia", "Provincia", "Compra Media (kg/unidades)")

    # 📊 3️⃣ Compra Promedio por Día
    df_fecha = df.groupby("fecha")["unidades_peso"].mean()
    df_fecha = df_fecha.iloc[::7]  # 🔹 Toma solo cada 7 días

    img_fecha = plot_to_base64(df_fecha, "Compra Promedio por Día", "Fecha", "Compra Media (kg/unidades)")

    return render_template('dashboard.html',
                           img_categoria=img_categoria,
                           img_provincia=img_provincia,
                           img_fecha=img_fecha)


def plot_to_base64(df, title, xlabel, ylabel):
    """Genera un gráfico y lo convierte en una imagen base64 para incrustar en HTML."""
    plt.figure(figsize=(8, 4))
    df.plot(kind="bar", color="skyblue", edgecolor="black")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convertir a imagen base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return base64.b64encode(img.getvalue()).decode('utf-8')





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

# ✅ Página principal

@main.route('/rubik', methods=['GET'])
def rubik_home():
    return render_template('rubik.html',secuencia_cubo={})

# ✅ Verifica si un archivo tiene extensión válida

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Manejo de la subida de imágenes del cubo




def encode_image(image_path):
    """Convierte una imagen a base64 para enviarla a OpenAI."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# ✅ Función para limpiar la respuesta JSON de OpenAI

def limpiar_json(respuesta):
    """Elimina delimitadores de Markdown en la respuesta JSON de OpenAI."""
    return re.sub(r"```json|```", "", respuesta).strip()



# ✅ Ruta para procesar las imágenes del cubo de Rubik

@main.route('/procesar-cubo', methods=['GET'])
def procesar_cubo():
    carpeta = "./app/static/uploads"
    resultados = {}

    if not os.path.exists(carpeta):
        return jsonify({"error": "No se encontraron imágenes en la carpeta."}), 400

    for cara in os.listdir(carpeta):
        ruta_completa = os.path.join(carpeta, cara)
        cara_sin_extension = os.path.splitext(cara)[0]

        if os.path.isfile(ruta_completa):
            image_base64 = encode_image(ruta_completa)

            # Llamada a ChatGPT para el reconocimiento de colores
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en cubos de Rubik."},
                    {"role": "user", "content": [
                        {"type": "text", "text": 
                            f"Analiza esta imagen y detecta los 9 colores en una cuadrícula 3x3. Devuelve el resultado en JSON con la estructura: "
                            f"{{'{cara_sin_extension}': [['color1', 'color2', 'color3'], ['color4', 'color5', 'color6'], ['color7', 'color8', 'color9']]}}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]}
                ],
                temperature=0
            )

            if "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"].strip()

                if content:
                    try:
                        content_cleaned = limpiar_json(content)
                        json_response = json.loads(content_cleaned)

                        if cara_sin_extension in json_response:
                            resultados[cara_sin_extension] = json_response[cara_sin_extension]

                    except json.JSONDecodeError:
                        print(f"❌ Error al decodificar JSON para la imagen {cara}")
                        # Si no se pudo procesar la respuesta, usar visión por computadora
                        colores_detectados = detectar_colores_con_vision(cara)
                        if colores_detectados:
                            resultados[cara_sin_extension] = colores_detectados

    # ✅ NO USAR `json.dumps()` AQUÍ
    secuencia_cubo = generar_secuencia_estado(resultados) if resultados else {"secuencia_estado": ""}

    print(f"✅ SECUENCIA CUBO ENVIADA A rubik.html: {secuencia_cubo}")  # Depuración

    return render_template("rubik.html", estado_cubo=resultados, secuencia_cubo=secuencia_cubo)


def detectar_colores_con_vision(imagen_path):
    """
    Detecta colores en una imagen usando OpenCV. 
    Devuelve un JSON con la estructura adecuada para los colores detectados en un cubo de Rubik.
    """
    # Leer la imagen con OpenCV
    img = cv2.imread(imagen_path)
    if img is None:
       print(f"❌ No se pudo cargar la imagen: {imagen_path}")
       return None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
   

def encode_image(image_path):
        """Convierte una imagen a base64 para enviarla a OpenAI."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    # ✅ Función para limpiar la respuesta JSON de OpenAI

def limpiar_json(respuesta):
        """Elimina delimitadores de Markdown en la respuesta JSON de OpenAI."""
        return re.sub(r"```json|```", "", respuesta).strip()

    # ✅ Ruta para mostrar la página del cubo de Rubik




def generar_secuencia_estado(jsoncubo):
        # ✅ Generar la secuencia de colores a partir del estado del cubo
        secuencia_estado = ""

        # Iterar sobre las claves (caras) del cubo
        for cara in jsoncubo.keys():
            if cara in jsoncubo:  # Asegurarnos de que la cara existe
                for row in jsoncubo[cara]:
                    for color in row:
                        color_inicial = color[0]  # Obtener la inicial del color
                        secuencia_estado += color_inicial

        # Devolver el JSON con la secuencia de colores
        return {"secuencia_estado": secuencia_estado}

    # Definir carpeta de subida
UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

    # ✅ Verifica si un archivo tiene una extensión válida
def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # ✅ Ruta para manejar la subida de imágenes del cubo
@main.route('/upload-rubik', methods=['POST'])
def upload_rubik_images():
        if 'files[]' not in request.files:
            return render_template("rubik.html", estado_cubo="NA",secuencia_cubo="NA")

        files = request.files.getlist('files[]')

        if len(files) != 6:
            return render_template("rubik.html", message="⚠️ Debes subir exactamente 6 imágenes en el orden correcto.")

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Asegurar que la carpeta exista

        # **ORDEN OBLIGATORIO** para asignar las caras

        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Asegura un nombre seguro
                file_path = os.path.join(UPLOAD_FOLDER,filename)
                file.save(file_path)

        return render_template("rubik.html", message="✅ Imágenes subidas correctamente.",secuencia_cubo ="na",solucion="na")

import pycuber as pc
from pycuber.solver import CFOPSolver        
import json        

@main.route('/resolver-cubo', methods=['POST'])
def resolver_cubo():
    try:
        
        estado_cubo = request.form.get("secuencia_cubo")
    
        # Verificación de que se recibió el estado del cubo
        if not estado_cubo or estado_cubo.strip() == "":
            return jsonify({"error": "No se recibió el estado del cubo."}), 400

        # Convertir la secuencia de colores a un diccionario
        estado_cubo = json.loads(estado_cubo)

        print(f"✅ JSON CONVERTIDO EN resolver_cubo(): {estado_cubo}")  # Depuración

        # Verificar que `estado_cubo` sea un diccionario
        if not isinstance(estado_cubo, dict):
            print(f"❌ ERROR: `estado_cubo` NO ES UN DICCIONARIO, ES {type(estado_cubo)}")
            return jsonify({"error": "Error en la conversión de JSON a diccionario."}), 500

        # Verificar que la clave `secuencia_estado` esté presente en el JSON
        if "secuencia_estado" not in estado_cubo:
            return jsonify({"error": "Formato incorrecto en estado_cubo."}), 400

        # Extraer la secuencia de colores
        secuencia_colores = estado_cubo["secuencia_estado"]
        print(f"✅ SECUENCIA DE COLORES EXTRAÍDA: {secuencia_colores}")  # Depuración

        # Convertir la secuencia de colores a movimientos de Rubik
        secuencia_movimientos = convertir_colores_a_movimientos(secuencia_colores)

        # Inicializar el cubo y aplicar los movimientos
        cubo = pc.Cube()
        for movimiento in secuencia_movimientos:
            cubo(movimiento)

        # Resolver el cubo con CFOP Solver
        solver = CFOPSolver(cubo)
        solucion = solver.solve()

        # Verificar si se generó una solución
        print(f"✅ SOLUCIÓN GENERADA: {solucion}")  # Depuración

        # Si no se generó una solución, asignar un mensaje de error
        if not solucion:
            solucion = "No se pudo generar una solución válida."
        
        
        solucion = " ".join(map(str, solucion))
        
   

        # Redirigir a la página de solución con la solución como parámetro
        print(f"🔍 SOLUCIÓN PASADA A rubik.html: {(solucion)}")  # Depuración
        return render_template("rubik.html", secuencia_cubo=estado_cubo, solucion=solucion) 

    except Exception as e:
        # Manejo de errores generales
        print(f"❌ ERROR GENERAL EN resolver_cubo(): {str(e)}")  # Depuración
        return jsonify({"error": f"Error al resolver el cubo: {str(e)}"}), 500


def convertir_colores_a_movimientos(secuencia_colores):

    if len(secuencia_colores) != 54:
        raise ValueError("La secuencia de colores no es válida. Debe contener exactamente 54 caracteres.")
    caras = ["B", "D", "F", "L", "R", "U"]  # Ajusta este orden si es necesario

    color_cara = {
        secuencia_colores[4]: "B",  # Cara superior
        secuencia_colores[13]: "D",  # Cara inferior
        secuencia_colores[22]: "F",  # Cara frontal
        secuencia_colores[31]: "L",  # Cara izquierda
        secuencia_colores[40]: "R",  # Cara derecha
        secuencia_colores[49]: "U"   # Cara trasera
    }
    
    secuencia_movimientos = []
    for color in secuencia_colores:
        if color in color_cara:
            secuencia_movimientos.append(color_cara[color])
    
    return "".join(secuencia_movimientos)


if __name__ == "__main__":
    app.run(debug=True)