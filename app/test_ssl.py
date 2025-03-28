import ssl
import certifi
import urllib.request

# Crear contexto SSL con certificados válidos
context = ssl.create_default_context(cafile=certifi.where())

# Probar acceso a un sitio seguro
try:
    with urllib.request.urlopen("https://www.google.com", context=context) as response:
        print(f"✅ Conexión exitosa: Código {response.status}")
except Exception as e:
    print(f"❌ Error SSL: {e}")
