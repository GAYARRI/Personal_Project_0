import matplotlib
matplotlib.use('Agg')  # Asegurar backend sin GUI
import matplotlib.pyplot as plt
import io

# Crear un gráfico simple
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
ax.set_title("Prueba de Matplotlib sin GUI")

# Guardar la imagen en memoria
img = io.BytesIO()
plt.savefig(img, format="png")
plt.close(fig)  # Cerrar el gráfico para liberar memoria

# Verificar si la imagen se ha guardado correctamente
if img.getvalue():
    print("✅ Matplotlib está funcionando correctamente con Agg")
else:
    print("❌ Hubo un problema al generar la imagen")
