# ver_db.py
import sqlite3
import os

# Usamos la misma ruta exacta que configuraste en tu db_manager.py
DB_NAME = os.path.join("database", "database.db")

def consultar_productos():
    if not os.path.exists(DB_NAME):
        print(f"❌ No se encontró el archivo de base de datos en: {DB_NAME}")
        return

    # Nos conectamos a tu base de datos
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Traemos todas las columnas de la tabla productos
        cursor.execute("SELECT fecha,hora,tienda, nombre, precio_actual, en_stock, url FROM productos order by fecha, hora asc")
        filas = cursor.fetchall()
        
        if not filas:
            print("📭 La base de datos existe, pero la tabla 'productos' está vacía.")
            return
            
        print(f"📊 --- PRODUCTOS REGISTRADOS EN LA BD ({len(filas)} ítems) ---")
        print(f"{'FECHA':<12} | {'HORA':<10} | {'TIENDA':<12} | {'ESTADO':<10} | {'PRECIO':<10} | {'NOMBRE DEL PRODUCTO'}")
        print("-" * 80)
        
        for fila in filas:
            fecha, hora, tienda, nombre, precio, stock, url = fila
            estado_texto = "🟢 STOCK" if stock == 1 else "🔴 AGOTADO"
            
            # Formateamos la salida para que se vea como una tabla limpia en tu terminal
            print(f"{fecha:<12} | {hora:<10} | {tienda:<12} | {estado_texto:<10} | S/. {precio:<7.2f} | {nombre}")
            
    except sqlite3.OperationalError as e:
        print(f"❌ Error al consultar la tabla (¿Seguro que ya corrió el init_db?): {e}")
    finally:
        conn.close()


def vaciar_tabla_productos():
    """Trunca (vacía) por completo la tabla productos sin borrar el archivo."""
    if not os.path.exists(DB_NAME):
        print(f"❌ No hay base de datos que vaciar en: {DB_NAME}")
        return

    # Pedimos una confirmación rápida para evitar errores accidentales
    confirmacion = input("\n⚠️ ¿Seguro que quieres VACIAS la tabla de productos? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("❌ Operación cancelada.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # En SQLite, 'DELETE FROM' actúa exactamente como un TRUNCATE TABLE
        cursor.execute("DELETE FROM productos")
        conn.commit()
        print("🗑️  ¡Tabla 'productos' vaciada con éxito de forma limpia!")
    except sqlite3.OperationalError as e:
        print(f"❌ Error al intentar vaciar la tabla: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🛠️  --- PANEL DE CONTROL DE BASE DE DATOS ---")
    print("[1] Ver productos registrados")
    print("[2] Vaciar (Truncar) tabla de productos")

    
    opcion = input("\nSelecciona una opción (1 o 2): ").strip()
    
    if opcion == "1":
        consultar_productos()
    elif opcion == "2":
            vaciar_tabla_productos()
    else:
        print("❌ Opción inválida.")