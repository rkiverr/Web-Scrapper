import os
import requests
from dotenv import load_dotenv

# Cargamos el archivo .env para leer la URL segura
load_dotenv()

def enviar_alerta_discord(nombre_producto, precio_nuevo, url_compra):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ Error: No se encontró DISCORD_WEBHOOK_URL en el archivo .env")
        return

    # Estructuramos el mensaje que leerá Discord
    mensaje = {
        "content": f"🚨 **¡CAÍDA DE PRECIO DETECTADA!** 🚨",
        "embeds": [
            {
                "title": nombre_producto,
                "description": f"El precio ha bajado a: **${precio_nuevo:,.2f}**",
                "url": url_compra,
                "color": 5814783, # Color verde en formato decimal
                "footer": {
                    "text": "Price Tracker Automático"
                }
            }
        ]
    }

    try:
        # Enviamos la petición HTTP POST a Discord
        respuesta = requests.post(webhook_url, json=mensaje)
        respuesta.raise_for_status()
        print("✅ Alerta enviada a Discord exitosamente.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar la alerta a Discord: {e}")

# (Opcional) Código de prueba aislado: 
# Si corres solo este archivo, enviará un mensaje de prueba.
if __name__ == "__main__":
    enviar_alerta_discord("Laptop Gamer de Prueba", 14500.50, "https://example.com")