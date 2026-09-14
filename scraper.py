import requests
from bs4 import BeautifulSoup
import re

from database import guardar_precio

def extraer_precio_producto(url):
    # 1. EL SCRAPER BASE
    # Simulamos ser Google Chrome en Windows para evitar bloqueos básicos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    print(f"Conectando a la tienda: {url}")
    
    try:
        # Hacemos la petición con un tiempo de espera (timeout) por si la página se cuelga
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status() # Lanza un error si el código HTTP no es 200 (OK)
        
        # Parseamos el HTML obtenido
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # IMPORTANTE: Estos selectores cambian dependiendo de la tienda.
        # Debes hacer "Clic derecho -> Inspeccionar" en la web para ver las etiquetas reales.
        # Aquí usamos selectores genéricos de ejemplo.
        etiqueta_titulo = soup.find('h1') 
        etiqueta_precio = soup.find(class_='ui-pdp-price') # Selector común en tiendas de LATAM
        
        # Si no encontramos las etiquetas, asignamos un texto por defecto
        titulo_sucio = etiqueta_titulo.text if etiqueta_titulo else "Título no encontrado"
        precio_sucio = etiqueta_precio.text if etiqueta_precio else "0"
        
        print(f"Texto crudo del precio obtenido: {repr(precio_sucio)}")
        
        # 2. DATA CLEANING (LIMPIEZA DE DATOS)
        # Limpiamos espacios laterales y saltos de línea del título
        titulo_limpio = titulo_sucio.strip()
        
        # Limpiamos el precio con Expresiones Regulares (regex)
        # r'[^\d.]' significa: "Encuentra cualquier cosa que NO sea un dígito (\d) o un punto (.)"
        # y lo reemplazamos por nada ('')
        precio_limpio_str = re.sub(r'[^\d.]', '', precio_sucio)
        
        # Manejo de casos donde haya más de un punto (ej. errores de lectura)
        # o donde el string quede vacío
        if not precio_limpio_str:
            precio_limpio_str = "0"
            
        # Convertimos el string resultante a un flotante matemático
        precio_float = float(precio_limpio_str)
        
        return {
            "titulo": titulo_limpio,
            "precio": precio_float
        }

    except requests.exceptions.RequestException as e:
        print(f"Error de red o conexión: {e}")
        return None
    except ValueError as e:
        print(f"Error al convertir el precio a número: {e}")
        return None

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    url_prueba = "https://tu-url-de-prueba.com" 
    datos = extraer_precio_producto(url_prueba)
    
    if datos:
        print(f"Producto: {datos['titulo']} | Precio: {datos['precio']}")
        # Guardamos en la base de datos
        guardar_precio(url_prueba, datos['titulo'], datos['precio'])