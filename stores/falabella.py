import json
import urllib.parse
from bs4 import BeautifulSoup


def buscar_producto_por_nombre(session, nombre_producto):
    """Busca un producto en Falabella usando la sesión compartida del monitor."""
    termino_busqueda = urllib.parse.quote_plus(nombre_producto)
    search_url = (
            "https://www.falabella.com.pe/"
            f"falabella-pe/search?Ntt={termino_busqueda}"
        )

    print(f"🔎 Buscando en Falabella: {nombre_producto}")
    print(f"🌐 URL: {search_url}")

    try:
        # CAMBIO CLAVE: Usamos 'session' en lugar de 'requests' directamente
        response = session.get(search_url, timeout=20)

        print(f"📡 Status HTTP: {response.status_code}")
        print(f"📄 HTML recibido: {len(response.text)} caracteres")

        # Guardamos tu archivo de debug tal como lo tenías pensado
        with open("falabella_search_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("💾 HTML guardado en falabella_search_debug.html")

        if response.status_code != 200:
            print(f"❌ Falabella respondió con error {response.status_code}")
            return []

        # --- Extracción de datos usando BeautifulSoup ---
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")

        if not script_tag:
            print(
                "⚠️ No se encontró la etiqueta __NEXT_DATA__. Es posible que Cloudflare bloqueara la petición."
            )
            return []

        # Convertimos el texto oculto del script en un diccionario de Python
        data = json.loads(script_tag.string)
        results = (
            data.get("props", {})
            .get("pageProps", {})
            .get("results", [])
        )

        productos_encontrados = []

        for item in results:
            titulo = item.get("displayName")
            url_relativa = item.get("url", "")
            url_final = (
                url_relativa
                if url_relativa.startswith("http")
                else f"https://www.falabella.com.pe{url_relativa}"
            )

            # Extraer precio (Buscamos la estructura de Falabella)
            precios = item.get("prices", [])
            precio_mostrar = "Precio No Disponible"
            if precios:
                # Obtenemos el precio principal o el primero de la lista
                precio_mostrar = (
                    f"{precios[0].get('currency', 'S/.')} {precios[0].get('price', [''])[0]}"
                )

            # Extraer Imagen
            imagenes = item.get("images", [])
            url_imagen = imagenes[0].get("url") if imagenes else None

            # Validación de stock rápida basándonos en las etiquetas visuales del JSON
            badge_stock = item.get("badge", "")
            disponible = "Agotado" not in badge_stock

            productos_encontrados.append(
                {
                    "titulo": titulo,
                    "precio": precio_mostrar,
                    "url": url_final,
                    "imagen": url_imagen,
                    "disponible": disponible,
                }
            )

        return productos_encontrados

    except Exception as e:
        print(f"💥 Error al procesar Falabella: {e}")
        return []   