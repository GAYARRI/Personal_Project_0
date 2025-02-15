import openai
import base64
import os

# Configurar la clave de API

openai.api_key = os.getenv('OPENAI_API_KEY')


# Función para codificar la imagen en base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Ruta de la imagen
image_path = "./app/static/uploads/FRONT.jpg"

# Codificar la imagen en Base64
image_base64 = encode_image(image_path)

# Llamada al endpoint de OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Eres un asistente de visión artificial experto en detección de colores en cubos de Rubik."},
        {"role": "user", "content": [
            {"type": "text", "text": 
                "Analiza esta imagen y detecta los 9 colores en una cuadrícula 3x3, asegurando que cada celda se identifique independientemente aunque los colores se repitan. Devuelve el resultado en formato JSON con una estructura como esta: " 
                "{'colors': [['color1', 'color2', 'color3'], ['color4', 'color5', 'color6'], ['color7', 'color8', 'color9']]}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]}
    ],
    temperature=0
)

# Imprimir el JSON con los 9 colores detectados
print(response["choices"][0]["message"]["content"])