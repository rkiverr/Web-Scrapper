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
from database import guardar_precio, obtener_ultimo_precio
from notifier import enviar_alerta_discord

# --- EJECUCIÓN DEL PIPELINE ---
if __name__ == "__main__":
    # Puedes probar con el link real de algún componente que necesites, 
    # por ejemplo, un microcontrolador ESP32 o algún módulo de sensores.
    url_objetivo = "https://www.mercadolibre.com.mx/2pzs-modulo-esp32-wifibluetooth-42-ble-nodemcu-con-cable-usb/p/MLM46943073?pdp_filters=item_id:MLM2761507563#is_advertising=true&searchVariation=MLM46943073&backend_model=search-backend&be_origin=backend&position=1&search_layout=grid&type=pad&tracking_id=02b2ec4b-b3de-4bf9-abb6-ee8a16177f1e&ad_domain=VQCATCORE_LST&ad_position=1&ad_click_id=YmY3NWUyNDktMzZhYi00MDE4LTlmMDMtY2JhZjU3Njg5Mzlj" 
    
    print("🚀 Iniciando pipeline de extracción...")
    datos = extraer_precio_producto(url_objetivo)
    
    if datos:
        nombre = datos['titulo']
        precio_actual = datos['precio']
        
        print(f"📦 Producto: {nombre} | Precio Actual: ${precio_actual}")
        
        # 1. Revisamos el historial
        ultimo_precio = obtener_ultimo_precio(url_objetivo)
        
        if ultimo_precio is None:
            print("ℹ️ Es la primera vez que rastreamos este producto. No hay historial para comparar.")
        else:
            print(f"🕒 Último precio registrado: ${ultimo_precio}")
            
            # 2. Lógica de alerta
            if precio_actual < ultimo_precio:
                print("📉 ¡El precio bajó! Disparando alerta...")
                enviar_alerta_discord(nombre, precio_actual, url_objetivo)
            elif precio_actual > ultimo_precio:
                print("📈 El precio subió. Qué triste, no enviaremos alerta.")
            else:
                print("⚖️ El precio se mantiene igual.")
                
        # 3. Guardamos el nuevo registro en MySQL
        guardar_precio(url_objetivo, nombre, precio_actual)
        print("✅ Ejecución del pipeline finalizada con éxito.")