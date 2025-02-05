# Usa una imagen base oficial de Python
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /

# Copia los archivos de la aplicación al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que corre la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]


ENV APP_ENV=docker


