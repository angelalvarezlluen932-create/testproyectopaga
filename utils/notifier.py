import requests
import json
from config import DISCORD_WEBHOOK_URL

def enviar_alerta_discord(producto, precio, tienda, url, imagen_url=None):
    """Envía una notificación visualmente atractiva (Embed) al canal de Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("❌ Error: No se ha configurado la variable DISCORD_WEBHOOK_URL en el archivo .env")
        return

    # Estructura del mensaje en formato de tarjeta (Embed)
    payload = {
        "username": "Pokémon Monitor Bot",
        "avatar_url": "https://pt.pinterest.com/pin/365565694758911139/",  # Icono de Pikachu
        "embeds": [
            {
                "title": f"🚨 ¡NUEVO STOCK / OFERTA DETECTADA EN {tienda.upper()}! 🚨",
                "description": f"Se encontró disponibilidad para:\n**{producto}**",
                "url": url,
                "color": 16711680,  # Color rojo intenso en formato decimal
                "fields": [
                    {
                        "name": "💰 Precio",
                        "value": f"S/. {precio}" if "amazon" not in tienda.lower() else f"${precio}",
                        "inline": True
                    },
                    {
                        "name": "🏪 Tienda",
                        "value": tienda,
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Pokémon prueba monitor  v1.0 • Monitoreo en vivo"
                }
            }
        ]
    }

    # Si lograste raspar la URL de la imagen del producto, la añade a la tarjeta
    if imagen_url:
        payload["embeds"][0]["image"] = {"url": imagen_url}

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            data=json.dumps(payload), 
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 204:
            print(f"✅ Alerta enviada con éxito a Discord para: {producto}")
        else:
            print(f"❌ Error al enviar a Discord ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error de red al conectar con el Webhook de Discord: {e}")