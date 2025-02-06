# Usa una imagen base oficial de Python
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /RepoP0

COPY . /RepoP0

# Copia los archivos de la aplicación al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt


ENV APP_ENV=docker
ENV FLASK_APP=run.py 

# Expone el puerto en el que corre la aplicación

EXPOSE 80


# Comando para ejecutar la aplicación

CMD ["python", "run.py"]






