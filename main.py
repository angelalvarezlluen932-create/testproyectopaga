# main.py
import json
import os
import random
import re
import time
import requests
from config import DISCORD_WEBHOOK_URL
from db_manager import init_db, verificar_y_actualizar_producto
from stores.falabella import buscar_producto_por_nombre


def inicializar_sesion():
    """Inicializa la sesión global simulando un navegador real."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "es-PE,es-419;q=0.9,es;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua-Platform": '"Windows"',
    })
    try:
        print("🌱 Calentando sesión e inicializando cookies...")
        session.get("https://falabella.com.pe", timeout=15)
        time.sleep(random.randint(2, 4))
    except Exception as e:
        print(f"⚠️ Alerta al inicializar sesión: {e}")
    return session


def limpiar_precio_a_float(precio_texto):
    """Convierte de forma segura textos como 'S/. 184.90' a un float real."""
    try:
        precio_limpio = str(precio_texto).strip()

        # Si contiene espacio (ej: 'S/. 184.90'), nos quedamos con el número del final
        if " " in precio_limpio:
            partes = precio_limpio.split()
            precio_limpio = partes[-1]

        # Quitamos comas de millares y puntos huérfanos al inicio
        precio_limpio = precio_limpio.replace(",", "")
        precio_limpio = precio_limpio.lstrip(".")

        return float(precio_limpio)
    except Exception as e:
        print(f"⚠️ Error al convertir precio '{precio_texto}': {e}")
        return 0.0


def enviar_alerta_discord(producto, tipo_alerta):
    """Manda una tarjeta adaptada al tipo de evento detectado por la BD."""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Error: DISCORD_WEBHOOK_URL no configurado.")
        return

    titulos = {
        "NUEVO_STOCK": "🚨 ¡NUEVO PRODUCTO DETECTADO! 🚨",
        "RESTOCK": "🔄 ¡VOLVIÓ EL STOCK! (RESTOCK) 🔄",
        "BAJA_PRECIO": "📉 ¡BAJÓ DE PRECIO! 📉",
    }

    colores = {
        "NUEVO_STOCK": 16711680,  # Rojo
        "RESTOCK": 30800,  # Verde
        "BAJA_PRECIO": 16776960,  # Amarillo
    }

    payload = {
        "username": "Pokémon Stock Monitor",
        "avatar_url": "https://soundcloud.com/i_p_i_k_a_c_h_u",
        "embeds": [
            {
                "title": titulos.get(tipo_alerta, "🚨 ALERTA DE STOCK 🚨"),
                "description": f"**{producto['titulo']}**",
                "url": producto["url"],
                "color": colores.get(tipo_alerta, 16711680),
                "fields": [
                    {
                        "name": "💵 Precio",
                        "value": f"`{producto['precio']}`",  # Muestra 'S/. 184.90'
                        "inline": True,
                    },
                    {
                        "name": "🏪 Tienda",
                        "value": "Falabella",
                        "inline": True,
                    },
                ],
                "footer": {
                    "text": "Pokémon  Alerta en tiempo real"
                },
            }
        ],
    }

    if producto.get("imagen"):
        payload["embeds"][0]["image"] = {"url": producto["imagen"]}

    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if res.status_code == 204:
            print(
                f"✅ Discord notificado [{tipo_alerta}]: {producto['titulo']}"
            )
        else:
            print(f"❌ Error en Discord: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error al enviar Webhook: {e}")


def ejecutar_monitor():
    # Aseguramos que la tabla exista en database/database.db al arrancar
    init_db()

    session_global = inicializar_sesion()
    termino_pokemon = "TCG Pokemon 30 Aniversario Poster Collection"

    print(
        f"🔄 [{time.strftime('%H:%M:%S')}] Iniciando ronda única de monitoreo (Modo Batch)..."
    )

    # Escaneo de Falabella (Ronda única)
    productos_falabella = buscar_producto_por_nombre(
        session_global, termino_pokemon
    )
    cola_alertas = []

    for prod in productos_falabella:
        precio_numerico = limpiar_precio_a_float(prod["precio"])

        # Consultamos tu db_manager
        tipo_alerta = verificar_y_actualizar_producto(
            url=prod["url"],
            nombre=prod["titulo"],
            tienda="Falabella",
            precio_nuevo=precio_numerico,
            tiene_stock=prod["disponible"],
        )

        if tipo_alerta:
            cola_alertas.append((prod, tipo_alerta))
        else:
            print(f"🗒️  Sin cambios relevantes para: {prod['titulo']}")

    # Despachamos las alertas con lead time de 10s para proteger el Rate Limit de Discord
    if cola_alertas:
        total_alertas = len(cola_alertas)
        print(f"\n🚀 Se detectaron {total_alertas} cambios. Enviando a Discord...")

        for indice, (prod, tipo_alerta) in enumerate(cola_alertas, start=1):
            enviar_alerta_discord(prod, tipo_alerta)

            # Si quedan más mensajes en la cola, aplicamos el lead time obligatorio de 10 segundos
            if indice < total_alertas:
                print(
                    "⏳ [Lead Time] Esperando 5 segundos antes del siguiente envío..."
                )
                time.sleep(5)
    else:
        print("\n✨ Ronda finalizada sin alertas pendientes.")


if __name__ == "__main__":
    ejecutar_monitor()
    # El script termina aquí limpiamente. La máquina virtual se apaga y el archivo .yml
    # se encargará de realizar el push automático de tu base de datos SQLite.