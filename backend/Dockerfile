# backend/Dockerfile
# Este Dockerfile construye la imagen para tu aplicación Flask.

FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor.
# Todos los comandos subsiguientes se ejecutarán en este directorio.
WORKDIR /app

# Copia el archivo de requisitos al directorio de trabajo.
# Esto es necesario para instalar las dependencias.
COPY requirements.txt requirements.txt

# Instala las dependencias de Python.
# --no-cache-dir evita guardar el caché de pip para reducir el tamaño de la imagen.
# -r requirements.txt instala todos los paquetes listados en el archivo.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación al directorio de trabajo.
# El '.' indica que se copie todo desde el contexto de construcción (el directorio donde está el Dockerfile).
COPY . .

# Expone el puerto 5000. Esto es meramente informativo y no publica el puerto.
# La publicación del puerto se realiza en docker-compose.yml.
EXPOSE 5000

# Define el comando para ejecutar la aplicación cuando el contenedor se inicie.
# python app.py inicia tu script Flask.
CMD ["python", "app.py"]
