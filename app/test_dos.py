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
                    model="gpt-4o",
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
    ('P1', 'UP'): 'w', ('P1', 'LEFT'): 'o', ('P1', 'BACK'): 'g',
    ('P2', 'UP'): 'w', ('P2', 'BACK'): 'g',
    ('P3', 'UP'): 'w', ('P3', 'RIGHT'): 'r', ('P3', 'BACK'): 'g',
    ('P4', 'UP'): 'w', ('P4', 'LEFT'): 'o',
    ('P5', 'UP'): 'w',
    ('P6', 'UP'): 'w', ('P6', 'RIGHT'): 'r',
    ('P7', 'UP'): 'w', ('P7', 'LEFT'): 'o', ('P7', 'FRONT'): 'b',
    ('P8', 'UP'): 'w', ('P8', 'FRONT'): 'b',
    ('P9', 'UP'): 'w', ('P9', 'RIGHT'): 'r', ('P9', 'FRONT'): 'b',

    ('P1B', 'DOWN'): 'y', ('P1B', 'LEFT'): 'o', ('P1B', 'BACK'): 'g',
    ('P2B', 'DOWN'): 'y', ('P2B', 'BACK'): 'g',
    ('P3B', 'DOWN'): 'y', ('P3B', 'RIGHT'): 'r', ('P3B', 'BACK'): 'g',
    ('P4B', 'DOWN'): 'y', ('P4B', 'LEFT'): 'o',
    ('P5B', 'DOWN'): 'y',
    ('P6B', 'DOWN'): 'y', ('P6B', 'RIGHT'): 'r',
    ('P7B', 'DOWN'): 'y', ('P7B', 'LEFT'): 'o', ('P7B', 'FRONT'): 'b',
    ('P8B', 'DOWN'): 'y', ('P8B', 'FRONT'): 'b',
    ('P9B', 'DOWN'): 'y', ('P9B', 'RIGHT'): 'r', ('P9B', 'FRONT'): 'b'
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
    print("Se llamó a /resolver-manzana")
    if 'estado_manzana' not in session:
        flash("⚠️ No hay estado de manzana cargado.", "error")
        return redirect(url_for('main.rubik_home'))

    estado_manzana = session['estado_manzana']
    estado_string = construir_estado_rubik_desde_manzana(estado_manzana)

    valido, mensaje = validar_estado(estado_string)
    if not valido:
        flash(mensaje, "error")
        return redirect(url_for('main.rubik_home'))

    try:
        cubo = pc.Cube()
        cubo.from_string(estado_string.upper())
        solver = CFOPSolver(cubo)
        solucion = solver.solve()
        solucion_str = " ".join(map(str, solucion))

        return render_template("rubik.html", solucion=solucion_str, estado_colores="wrbwrbwrbrrggrggrgbyybyybyyooggwwwwwww", es_cubo=False)

    except Exception as e:
        flash(f"❌ Error al resolver: {str(e)}", "error")
        return redirect(url_for('main.rubik_home'))
