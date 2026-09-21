import sqlite3
import os

# Le indicamos a Python que busque el archivo dentro de la carpeta 'database'
DB_NAME = os.path.join("database", "database.db")

def init_db():
    """Inicializa la tabla de productos dentro de database/database.db"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            url TEXT PRIMARY KEY,
            nombre TEXT,
            tienda TEXT,
            precio_actual REAL,
            en_stock INTEGER,
            fecha TEXT,  -- 📅 Guarda: YYYY-MM-DD (Ej: 2026-09-20)
            hora TEXT    -- ⏰ Guarda: HH:MM:SS (Ej: 20:45:12)
        )
    """)
    
    conn.commit()
    conn.close()
    print("💾 Base de datos SQLite inicializada correctamente en database/database.db")

def verificar_y_actualizar_producto(url, nombre, tienda, precio_nuevo, tiene_stock):
    """Compara el producto con la BD y detecta cambios de precio o stock."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT precio_actual, en_stock FROM productos WHERE url = ?", (url,))
    resultado = cursor.fetchone()
    
    alerta_tipo = None
    
    if resultado is None:
        # Insertamos asignando de forma nativa la fecha y la hora en sus respectivas columnas
        cursor.execute("""
            INSERT INTO productos (url, nombre, tienda, precio_actual, en_stock, fecha, hora)
            VALUES (?, ?, ?, ?, ?, DATE('now', 'localtime'), TIME('now', 'localtime'))
        """, (url, nombre, tienda, precio_nuevo, 1 if tiene_stock else 0))
        if tiene_stock:
            alerta_tipo = "NUEVO_STOCK"
    else:
        precio_anterior, stock_anterior = resultado
        stock_anterior_bool = True if stock_anterior == 1 else False
        
        if tiene_stock and not stock_anterior_bool:
            alerta_tipo = "RESTOCK"
        elif tiene_stock and precio_nuevo < precio_anterior:
            alerta_tipo = "BAJA_PRECIO"
            
        # Actualizamos precio, stock, y refrescamos tanto la fecha como la hora del cambio
        cursor.execute("""
            UPDATE productos 
            SET precio_actual = ?, 
                en_stock = ?, 
                fecha = DATE('now', 'localtime'), 
                hora = TIME('now', 'localtime') 
            WHERE url = ?
        """, (precio_nuevo, 1 if tiene_stock else 0, url))
        
    conn.commit()
    conn.close()
    return alerta_tipo