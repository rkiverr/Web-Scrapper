import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

try:
    # Nos conectamos a MySQL en general, SIN especificar base de datos
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conexion.cursor()

    print("Construyendo la base de datos...")
    
    # 1. Crear la base de datos
    cursor.execute("CREATE DATABASE IF NOT EXISTS price_tracker;")
    cursor.execute("USE price_tracker;")
    
    # 2. Crear tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(500) UNIQUE NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 3. Crear tabla del historial
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_precios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            producto_id INT NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
        );
    """)
    
    conexion.commit()
    print("✅ ¡Base de datos y tablas creadas exitosamente!")

except mysql.connector.Error as err:
    print(f"❌ Error de MySQL: {err}")
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conexion' in locals(): conexion.close()