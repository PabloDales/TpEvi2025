# backend/app.py
# Este es el código de tu aplicación Flask API para gestionar tareas.

from flask import Flask, request, jsonify
import mysql.connector
import os
import time
from flask_cors import CORS # Nueva importación para CORS

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos, obtenida de las variables de entorno de Docker Compose.
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# Función para conectar a la base de datos.
# Incluye reintentos para asegurar que el backend espere a que la base de datos esté lista.
def get_db_connection():
    max_retries = 10
    retry_delay = 5  # segundos
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Conexión a la base de datos establecida exitosamente.")
            return conn
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")
            print(f"Reintentando en {retry_delay} segundos... ({i+1}/{max_retries})")
            time.sleep(retry_delay)
    raise Exception("No se pudo conectar a la base de datos después de varios reintentos.")

# Función para inicializar la base de datos (crear la tabla 'tasks' si no existe).
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'ToDo'
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabla 'tasks' verificada/creada.")

# Ejecuta la inicialización de la base de datos al inicio de la aplicación.
# Se asegura de que la tabla exista antes de que se realicen operaciones.
with app.app_context():
    init_db()

# Rutas de la API

# Obtener todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # Retorna filas como diccionarios
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks)

# Crear una nueva tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    title = data.get('title')
    if not title:
        return jsonify({"error": "El título es requerido"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
    conn.commit()
    new_task_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_task_id, "title": title, "status": "ToDo"}), 201

# Actualizar el estado de una tarea
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    status = data.get('status')
    if not status or status not in ['ToDo', 'Doing', 'Done']:
        return jsonify({"error": "El estado debe ser 'ToDo', 'Doing' o 'Done'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify({"message": "Tarea actualizada correctamente"}), 200

# Eliminar una tarea
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify({"message": "Tarea eliminada correctamente"}), 200

# Punto de entrada para ejecutar la aplicación Flask.
if __name__ == '__main__':
    # host='0.0.0.0' hace que el servidor Flask sea accesible desde cualquier IP (necesario en Docker).
    # debug=True habilita el modo de depuración, que recarga la aplicación al cambiar el código.
    app.run(host='0.0.0.0', debug=True)
