import os
import mysql.connector
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

def conectar_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def guardar_precio(url, nombre, precio):
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        # 1. Insertar el producto si no existe (ignorando si la URL ya está registrada)
        sql_producto = "INSERT IGNORE INTO productos (url, nombre) VALUES (%s, %s)"
        cursor.execute(sql_producto, (url, nombre))
        
        # 2. Obtener el ID del producto (ya sea recién creado o existente)
        cursor.execute("SELECT id FROM productos WHERE url = %s", (url,))
        producto_id = cursor.fetchone()[0]

        # 3. Insertar el nuevo precio en el historial
        sql_precio = "INSERT INTO historial_precios (producto_id, precio) VALUES (%s, %s)"
        cursor.execute(sql_precio, (producto_id, precio))
        
        # Confirmar los cambios
        conexion.commit()
        print(f"✅ Precio de ${precio} guardado correctamente en la BD.")

    except mysql.connector.Error as error:
        print(f"❌ Error al guardar en MySQL: {error}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()