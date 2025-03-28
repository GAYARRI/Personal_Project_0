import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

from flask import Blueprint, render_template, request, redirect, url_for, Flask
from flask import jsonify,flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
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
import matplotlib
matplotlib.use('Agg')  # 🔴 FORZAR BACKEND SIN GUI
import matplotlib.pyplot as plt
import base64
from docx import Document
import io
from scipy.optimize import linprog
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, pacf
import pycuber as pc
from pycuber.solver import CFOPSolver        
import json        
import ast
from colorthief import ColorThief # type: ignor
import cv2
import webcolors
from flask import flash, redirect, url_for, render_template
from flask import flash, redirect, url_for, render_template, session
import pycuber as pc
from pycuber.solver import CFOPSolver









ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = "app/static/uploads"



main = Blueprint('main', __name__)


# Getion de Compras
@main.route('/compras', methods=['GET'])
def compras():
    compras = Compra.query.all()
    productos = Producto.query.all()  # 🔹 Obtener productos para el formulario
    clientes = Cliente.query.all()  # 🔹 Obtener clientes para el formulario
    ciudades = Ciudad.query.all()  # 🔹 Obtener ciudades para el formulario
    return render_template('compras.html', compras=compras, productos=productos, clientes=clientes, ciudades=ciudades)


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

@main.route('/compras/borrar/<int:id>', methods=['POST'])
def borrar_compra(id):
    compra = Compra.query.get_or_404(id)  # 🔹 Obtiene la compra o devuelve error 404 si no existe
    db.session.delete(compra)
    db.session.commit()
    flash("Compra eliminada con éxito.", "success")
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
    return render_template('home.html',show_home_button=False)

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@main.route("/documento")
def documento():
    return render_template("documento.html")


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
        

        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1
)

      

        # Obtener la URL de la imagen generada
        image_url = response.data[0].url


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


docx_filename="Gracias.docx"
docx_path=os.path.join(os.getcwd(), "app", "static","uploads", docx_filename)
# --- LIMPIAR JSON ---
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

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@main.route('/procesar-cubo', methods=['GET'])
def procesar_cubo():
    import sys
    sys.stdout.write("🔥 Este print forzado aparece\n")
    sys.stdout.flush()


    carpeta = "./app/static/uploads"
    resultados = {}

    if not os.path.exists(carpeta) or not os.listdir(carpeta):
        return jsonify({"error": "No se encontraron imágenes en la carpeta."}), 400

    for cara in os.listdir(carpeta):
        ruta_completa = os.path.join(carpeta, cara)
        cara_sin_extension = os.path.splitext(cara)[0]

        if os.path.isfile(ruta_completa):
            image_base64 = encode_image(ruta_completa)
            
            # ✅ Llamada a la API de OpenAI para análisis de colores
            response = client.chat.completions.create(
                model="gpt-4.5-preview",
            messages=[
            {"role": "system", "content": "Eres un asistente experto en cubos de Rubik. Tu tarea es detectar colores en imágenes de cubos, usando solo colores estándar."},
            {"role": "user", "content": 
            f"Analiza esta imagen de una cara del cubo Rubik y detecta los 9 colores en una cuadrícula 3x3. "
            f"Utiliza únicamente estos colores: red, blue, green, yellow, white, orange, pink. "
            f"Devuelve el resultado en formato JSON con esta estructura EXACTA:\n\n"
            f"{{'{cara_sin_extension}': [['red', 'blue', 'green'], ['yellow', 'white', 'orange'], ['red', 'green', 'blue']]}}\n\n"
            f"Asegúrate de devolver un JSON válido, sin explicaciones ni comentarios."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Aquí está la imagen del cubo de Rubik:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }
    ],
    temperature=0  # Mantener temperatura BAJA para precisión
)    
            

            # ✅ Procesar respuesta de OpenAI
            if response.choices:
                content = response.choices[0].message.content.strip()

                if content:
                    try:
                        content_cleaned = limpiar_json(content)  # Función para limpiar el JSON si es necesario
                        json_response = json.loads(content_cleaned)

                        if cara_sin_extension in json_response:
                            resultados[cara_sin_extension] = json_response[cara_sin_extension]

                    except json.JSONDecodeError:
                        print(f"❌ Error al decodificar JSON para la imagen {cara}")
                        # Si la respuesta no es válida, usar visión por computadora
                        colores_detectados = detectar_colores_con_vision(ruta_completa)
                        if colores_detectados:
                            resultados[cara_sin_extension] = colores_detectados

    secuencia_cubo = generar_secuencia_estado(resultados) if resultados else {"secuencia_estado": ""}

    print(f"✅ SECUENCIA CUBO ENVIADA A rubik.html: {secuencia_cubo}")  # Depuración

    return render_template("rubik.html", estado_cubo=resultados, secuencia_cubo=secuencia_cubo,es_cubo=True)


        



def detectar_colores_con_vision(imagen_path):

    img = cv2.imread(imagen_path)
    if img is None:
        print(f"\u274c No se pudo cargar la imagen: {imagen_path}")
        return None

    h, w, _ = img.shape
    grid_size = 3
    cell_h, cell_w = h // grid_size, w // grid_size

    resultado = []
    for i in range(grid_size):
        fila = []
        for j in range(grid_size):
            cell = img[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
            temp_file = f"temp_cell_{i}_{j}.jpg"
            cv2.imwrite(temp_file, cell)

            try:
                color_thief = ColorThief(temp_file)
                rgb = color_thief.get_color(quality=1)
                nombre_color = rgb_a_nombre_color(rgb)
                fila.append(nombre_color)
            except Exception as e:
                print(f"Error con ColorThief en celda ({i},{j}): {e}")
                fila.append("unknown")

            os.remove(temp_file)
        resultado.append(fila)

    return resultado
    
def rgb_a_nombre_color(rgb):
    try:
        return webcolors.rgb_to_name(rgb)
    except ValueError:
        min_distancia = float('inf')
        nombre_cercano = ""
        for nombre, valor in webcolors.CSS3_NAMES_TO_HEX.items():
            valor_rgb = webcolors.hex_to_rgb(valor)
            distancia = sum((a - b) ** 2 for a, b in zip(rgb, valor_rgb))
            if distancia < min_distancia:
                min_distancia = distancia
                nombre_cercano = nombre
        return nombre_cercano


   

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
        return render_template("rubik.html", secuencia_cubo=estado_cubo, solucion=solucion,es_cubo=True) 

    except Exception as e:
        # Manejo de errores generales
        print(f"❌ ERROR GENERAL EN resolver_cubo(): {str(e)}")  # Depuración
        return jsonify({"error": f"Error al resolver el cubo: {str(e)}"}), 500


def convertir_colores_a_movimientos(secuencia_colores):

    if len(secuencia_colores) != 54:
        raise ValueError("La secuencia de colores no es válida. Debe contener exactamente 54 caracteres.")
    caras = ["B", "D", "F", "L", "R", "U"]  # Ajusta este orden si es necesario

    color_cara = {
        secuencia_colores[4]: "B",  # Cara trasera
        secuencia_colores[13]: "D",  # Cara inferior
        secuencia_colores[22]: "F",  # Cara frontal
        secuencia_colores[31]: "L",  # Cara izquierda
        secuencia_colores[40]: "R",  # Cara derecha
        secuencia_colores[49]: "U"   # Cara superior 
    }
    
    secuencia_movimientos = []
    for color in secuencia_colores:
        if color in color_cara:
            secuencia_movimientos.append(color_cara[color])
    
    return "".join(secuencia_movimientos)

##############################################################

def limpiar_json(respuesta):
    """Extrae y limpia el bloque JSON de una respuesta con posibles delimitadores y texto adicional."""
    match = re.search(r"\{.*\}", respuesta, re.DOTALL)
    if match:
        return match.group(0).strip()
    return respuesta.strip()

# --- OBTENER COLOR DE PIEZA EN UNA CARA ---
def obtener_color_visible(pieza_id, cara_actual):
    color = color_por_pieza_cara.get((pieza_id, cara_actual), 'x')
    if color == 'x':
        print(f"⚠️ Color no encontrado para pieza {pieza_id} en cara {cara_actual}")
    return color


# Construye el estado final de 54 stickers con colores correctos
def construir_estado_rubik_desde_manzana(estado_manzana):
    orden_caras = ['UP', 'RIGHT', 'FRONT', 'DOWN', 'LEFT', 'BACK']
    estado = ''

    for cara in orden_caras:
        if cara not in estado_manzana:
            print(f"⚠️ Cara ausente: {cara}")
        for fila in estado_manzana.get(cara, []):
            for pieza in fila:
                pieza_id = pieza.split('_')[0].upper()
                color = obtener_color_visible(pieza_id, cara)
                print(f"🧩 {cara} | {pieza} → {color}")
                estado += color

    print(f"🎯 Estado final generado: {estado} (long: {len(estado)})")
    return estado

@main.route('/procesar_manzana', methods=['GET'])
def procesar_manzana():
 
    carpeta = "./app/static/uploads"
    resultados = {}

    if not os.path.exists(carpeta):
        return jsonify({"error": "No se encontraron imágenes en la carpeta."}), 400

    for cara in os.listdir(carpeta):
        ruta_completa = os.path.join(carpeta, cara)
        cara_sin_extension = os.path.splitext(cara)[0].upper()

        if os.path.isfile(ruta_completa):
            image_base64 = encode_image(ruta_completa)
            try:
                response = client.chat.completions.create(
                    model="gpt-4.5-preview",
                    messages=[
                        {"role": "system", "content": "Eres un experto en rompecabezas 3D como cubos o manzanas."},
                        {"role": "user", "content": f"Analiza esta imagen de una cara tridimensional dividida en 9 piezas. Devuelve solo JSON con etiquetas P1–P9 y rotación (ej: P1_0). Formato: {{'{cara_sin_extension}': [['P1_0', ..., 'P3_180'], ..., ['P7_0', ..., 'P9_90']]}}"},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Aquí está la imagen:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]}
                    ],
                    temperature=0
                )
                content = response.choices[0].message.content.strip()
                if content:
                    try:
                        json_data = json.loads(limpiar_json(content))
                        resultados[cara_sin_extension] = json_data.get(cara_sin_extension, [])
                        
                    except Exception as e:
                        print(f"⚠️ Error en {cara_sin_extension}: {e}")
            except Exception as e:
                print(f"❌ Error OpenAI para {cara_sin_extension}: {e}")

    session['estado_manzana'] = resultados
    estado_colores = construir_estado_rubik_desde_manzana(resultados) if resultados else ""

    print(f"estado_colores = {estado_colores}")


    return render_template("rubik.html",estado_manzana=resultados,estado_colores=estado_colores, es_cubo=False)

# --- MAPEOS CLAROS DE PIEZA + CARA A COLOR ---
color_por_pieza_cara = {
    # UP face (white)
    ('P1', 'UP'): 'w', ('P2', 'UP'): 'w', ('P3', 'UP'): 'w',
    ('P4', 'UP'): 'w', ('P5', 'UP'): 'w', ('P6', 'UP'): 'w',
    ('P7', 'UP'): 'w', ('P8', 'UP'): 'w', ('P9', 'UP'): 'w',

    # DOWN face (yellow)
    ('P1', 'DOWN'): 'y', ('P2', 'DOWN'): 'y', ('P3', 'DOWN'): 'y',
    ('P4', 'DOWN'): 'y', ('P5', 'DOWN'): 'y', ('P6', 'DOWN'): 'y',
    ('P7', 'DOWN'): 'y', ('P8', 'DOWN'): 'y', ('P9', 'DOWN'): 'y',

    # FRONT face (blue)
    ('P1', 'FRONT'): 'b', ('P2', 'FRONT'): 'b', ('P3', 'FRONT'): 'b',
    ('P4', 'FRONT'): 'b', ('P5', 'FRONT'): 'b', ('P6', 'FRONT'): 'b',
    ('P7', 'FRONT'): 'b', ('P8', 'FRONT'): 'b', ('P9', 'FRONT'): 'b',

    # BACK face (green)
    ('P1', 'BACK'): 'g', ('P2', 'BACK'): 'g', ('P3', 'BACK'): 'g',
    ('P4', 'BACK'): 'g', ('P5', 'BACK'): 'g', ('P6', 'BACK'): 'g',
    ('P7', 'BACK'): 'g', ('P8', 'BACK'): 'g', ('P9', 'BACK'): 'g',

    # LEFT face (orange)
    ('P1', 'LEFT'): 'o', ('P2', 'LEFT'): 'o', ('P3', 'LEFT'): 'o',
    ('P4', 'LEFT'): 'o', ('P5', 'LEFT'): 'o', ('P6', 'LEFT'): 'o',
    ('P7', 'LEFT'): 'o', ('P8', 'LEFT'): 'o', ('P9', 'LEFT'): 'o',

    # RIGHT face (red)
    ('P1', 'RIGHT'): 'r', ('P2', 'RIGHT'): 'r', ('P3', 'RIGHT'): 'r',
    ('P4', 'RIGHT'): 'r', ('P5', 'RIGHT'): 'r', ('P6', 'RIGHT'): 'r',
    ('P7', 'RIGHT'): 'r', ('P8', 'RIGHT'): 'r', ('P9', 'RIGHT'): 'r',

}
pieza_colores = {
    'P1': {'UP': 'w', 'LEFT': 'o', 'BACK': 'g'},
    'P2': {'UP': 'w', 'BACK': 'g'},
    'P3': {'UP': 'w', 'RIGHT': 'r', 'BACK': 'g'},
    'P4': {'UP': 'w', 'LEFT': 'o'},
    'P5': {'UP': 'w', 'DOWN': 'y'},
    'P6': {'UP': 'w', 'RIGHT': 'r'},
    'P7': {'UP': 'w', 'LEFT': 'o', 'FRONT': 'b'},
    'P8': {'UP': 'w', 'FRONT': 'b'},
    'P9': {'UP': 'w', 'RIGHT': 'r', 'FRONT': 'b'},

    'P1b': {'DOWN': 'y', 'LEFT': 'o', 'BACK': 'g'},
    'P2b': {'DOWN': 'y', 'BACK': 'g'},
    'P3b': {'DOWN': 'y', 'RIGHT': 'r', 'BACK': 'g'},
    'P4b': {'DOWN': 'y', 'LEFT': 'o'},
    'P5b': {'DOWN': 'y'},
    'P6b': {'DOWN': 'y', 'RIGHT': 'r'},
    'P7b': {'DOWN': 'y', 'LEFT': 'o', 'FRONT': 'b'},
    'P8b': {'DOWN': 'y', 'FRONT': 'b'},
    'P9b': {'DOWN': 'y', 'RIGHT': 'r', 'FRONT': 'b'},
}

def construir_cubo_desde_estado(estado_colores):
    from pycuber import Cube
    # Verificación robusta del tipo de input
    if not isinstance(estado_colores, str):
        raise TypeError(f"❌ Error: estado_colores debe ser str, no {type(estado_colores)}")

    if len(estado_colores) != 54:
        raise ValueError("El estado debe tener exactamente 54 caracteres")

    cubo = Cube()
    caras = ['U', 'R', 'F', 'D', 'L', 'B']
    mapping = {
        'w': 'white',
        'r': 'red',
        'b': 'blue',
        'g': 'green',
        'y': 'yellow',
        'o': 'orange'
    }

    # Asignar colores a cada cara en orden URFDLB
    index = 0
    for cara in caras:
        face = cubo[cara]
        for i in range(3):
            for j in range(3):
                letra_raw=estado_colores[index]                
                print(f"🔎 index={index} | valor bruto={letra_raw} | tipo={type(letra_raw)}")

                if not isinstance(letra_raw, str):
                    raise TypeError(f"❌ Esperado str en estado_colores[{index}], recibido {type(letra_raw)}")

                letra = letra_raw.lower()
                if letra not in mapping:
                    raise ValueError(f"❌ Color inválido: {letra} en posición {index}")
                face[i][j].colorletra_raw = estado_colores[index]
                p = mapping[letra]
                index += 1

    return cubo
                


# --- VALIDAR ESTADO ---

from collections import Counter

def validar_estado(estado):
    
    if len(estado) != 54:
        return False, f"❌ Longitud inválida: {len(estado)}"
    if any(c not in 'wrbgyo' for c in estado):
        return False, f"❌ El estado contiene colores no válidos: {set(estado) - set('wrbgyo')}"
    conteo = Counter(estado)
    for c in 'wrbgyo':
        if conteo[c] != 9:
            return False, f"❌ Color '{c}' aparece {conteo[c]} veces (se esperaban 9)"
    return True, "✅ Estado válido"


@main.route('/resolver-manzana', methods=['POST'])
def resolver_manzana():
    print("📍 Entrando en /resolver-manzana")

    if 'estado_manzana' not in session:
        flash("⚠️ No hay estado de manzana cargado.", "error")
        return redirect(url_for('main.rubik_home'))

    estado_manzana = session['estado_manzana']
    estado_colores = construir_estado_rubik_desde_manzana(estado_manzana)

    print(f"🎯 estado_colores recibido: {estado_colores}")
    print(f"🔬 tipo(estado_colores): {type(estado_colores)}")
    print(f"🔬 contenido: {estado_colores[:10]}")

    # Transformar lista a string si fuera necesario
    if isinstance(estado_colores, list):
        estado_colores = ''.join(map(str, estado_colores))
        print(f"🔁 Convertido a string: {estado_colores}")

    valido, mensaje = validar_estado(estado_colores)
    if not valido:
        flash(mensaje, "error")
        return redirect(url_for('main.rubik_home'))

    try:
        cubo = construir_cubo_desde_estado(estado_colores)

        print("🧪 Cubo construido con éxito. Representación:")
        for face in 'URFDLB':
            print(f"{face}:")
            print(cubo[face])

        try:
            print("🧪 Probando movimientos básicos:")
            try:
               cubo('U')
               cubo('R')
               cubo("F'")
               print("✅ Movimientos aplicados correctamente.")
            except Exception as e:
               print(f"❌ Error al aplicar movimientos: {e}")

        except Exception as e:
            print(f"❌ Error interno en CFOPSolver: {str(e)}")
            raise

        solucion_str = " ".join(map(str, solucion))
        print(f"✅ Solución encontrada: {solucion_str}")

        return render_template(
            "rubik.html",
            solucion=solucion_str,
            estado_colores=estado_colores,
            es_cubo=False
        )

    except Exception as e:
        flash(f"❌ Error al resolver: {str(e)}", "error")
        return redirect(url_for('main.rubik_home'))
   

##############################################################


@main.route("/ver-documento")
def ver_documento():
    with open("Gracias_.txt", "r", encoding="utf-8") as file:
        contenido = file.read()
    
    return render_template("documento.html", contenido=contenido)

class LPForm(FlaskForm):
    variables = StringField('Decision Variables (comma-sep)', validators=[DataRequired()])
    objective_function = StringField('Objective Function to minimize (comma-sep)', validators=[DataRequired()])
    constraints = TextAreaField('Constraints (one per line, format: coefficients <=  /  >=  value)', validators=[DataRequired()])
    submit = SubmitField('Submit',render_kw={'class': 'button'})
  
@main.route('/simplex_input', methods=['GET', 'POST'])
def simplex_input():
    form = LPForm()
    if form.validate_on_submit():
        variables = [var.strip() for var in form.variables.data.split(',')]
        objective_function = list(map(float, form.objective_function.data.split(',')))
        constraint_lines = [line.strip() for line in form.constraints.data.splitlines()]
        
        
        A = []
        b = []
        sense = []
        
        for line in constraint_lines:
            parts = line.split()
            coeffs = list(map(float, parts[:-2]))
            op = parts[-2]
            value = float(parts[-1])
            A.append(coeffs)
            b.append(value)
            sense.append(op)
        
        # Convert constraints for linprog
        A_ub = []
        b_ub = []
        A_eq = []
        b_eq = []
        
        for i, s in enumerate(sense):
            if s == '<=':
                A_ub.append(A[i])
                b_ub.append(b[i])
            elif s == '==':
                A_eq.append(A[i])
                b_eq.append(b[i])
        
        res = linprog(c=objective_function, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                      A_eq=A_eq if A_eq else None, b_eq=b_eq if b_eq else None, method='highs')
        
    
        
        goal = sum(a * b for a, b in zip(res.x.tolist(), objective_function))
    

        return redirect(url_for('main.simplex', 
                variables=','.join(variables), 
                objective_function=form.objective_function.data, 
                constraints=';'.join(constraint_lines), 
                valores_optimos=','.join(map(str, res.x.tolist())) if res.success else 'Infeasible',
                goal=str(sum(a * b for a, b in zip(res.x.tolist(), objective_function))) if res.success else '0'))

        
    
    return render_template('simplex_input.html', form=form)  
    
@main.route('/simplex')
def simplex():
    variables = request.args.get('variables', '').split(',')
    objective_function = request.args.get('objective_function', '')
    constraints = request.args.get('constraints', '').split(';')
    valores_optimos = request.args.get('valores_optimos')
    

    goal=request.args.get('goal','0')

    return render_template('simplex.html', variables=variables, 
                           objective_function=objective_function, 
                           constraints=constraints, val_opt_= valores_optimos, goal_= goal)



# Ruta para la carga del archivo y procesamiento de SARIMA

@main.route('/sarima', methods=['GET', 'POST'])
def sarima():
    if request.method == 'GET':
        return render_template('sarima.html')  # Mostrar página inicial

    # Si es una solicitud POST y no se envió archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No se ha seleccionado un archivo'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se ha seleccionado un archivo'})

    # Cargar los datos del CSV
    df = pd.read_csv(file, parse_dates=[0], index_col=0)
    df = df.asfreq('D')  # Asegurar frecuencia diaria
    df.interpolate(inplace=True)  # Rellenar valores faltantes si hay

    # Obtener parámetros del formulario
    try:
        p = int(request.form.get('p', 1))
        d = int(request.form.get('d', 1))
        q = int(request.form.get('q', 1))
        P = int(request.form.get('P', 1))
        D = int(request.form.get('D', 1))
        Q = int(request.form.get('Q', 1))
        s = int(request.form.get('s', 7))
    except ValueError:
        return jsonify({'error': 'Los parámetros deben ser números enteros válidos'})

    # Ajustar el modelo SARIMA con los parámetros ingresados
    order = (p, d, q)
    seasonal_order = (P, D, Q, s)

    try:
        model = sm.tsa.statespace.SARIMAX(df, order=order, seasonal_order=seasonal_order)
        results = model.fit()
    except Exception as e:
        return jsonify({'error': f'Error al ajustar el modelo: {str(e)}'})

    df['fitted'] = results.fittedvalues
    residuals = results.resid


    # Predicciones para los próximos 6 días
    forecast_steps = 6
    forecast_index = pd.date_range(start=df.index[-1], periods=forecast_steps+1, freq='D')[1:]
    forecast = results.get_forecast(steps=forecast_steps)

    # Extraer la forma funcional del modelo
    model_summary = results.summary().as_text()

    # Cálculo de ACF y PACF
    acf_values = acf(residuals, nlags=40)
    pacf_values = pacf(residuals, nlags=40)

    # --- Creación de gráficos en base64 ---
    
    # 1. Serie Original vs Ajustada
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df.index, df.iloc[:, 0], label='Serie Original', color='blue', alpha=0.5)
    ax.plot(df.index, df['fitted'], label='Serie Ajustada', color='red', linewidth=2)
    ax.set_title('Serie Original y Ajustada')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Valor')
    ax.legend()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    original_fitted_plot = base64.b64encode(img.getvalue()).decode()

    # 2. Residuos del Modelo
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, residuals, label='Residuos', color='purple')
    ax.set_ylim(-10, 10)  # Ajusta el rango vertical de los residuos
    ax.set_title('Residuos del Modelo')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Residuo')
    ax.legend()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    residuals_plot = base64.b64encode(img.getvalue()).decode()

    # 3. Gráficos de ACF y PACF
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))

    # Gráfico ACF
    sm.graphics.tsa.plot_acf(residuals, lags=40, ax=axes[0])
    axes[0].set_title('Función de Autocorrelación (ACF)')

    # Gráfico PACF
    sm.graphics.tsa.plot_pacf(residuals, lags=40, ax=axes[1])
    axes[1].set_title('Función de Autocorrelación Parcial (PACF)')

    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    acf_pacf_plot = base64.b64encode(img.getvalue()).decode()

    # Renderizar la plantilla con gráficos
    return render_template('sarima.html', 
                           original_fitted_plot=original_fitted_plot, 
                           residuals_plot=residuals_plot, 
                           acf_pacf_plot=acf_pacf_plot,
                           model_summary=model_summary)


if __name__ == "__main__":
    app.run(debug=True)