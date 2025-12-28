import sqlite3
import os
import sys

def obtener_ruta_db():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "parqueadero.db")

ruta = obtener_ruta_db()
print("👉 Usando base de datos:", ruta)

conn = sqlite3.connect(ruta)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE vehiculos ADD COLUMN deuda REAL DEFAULT 0")
    print("✅ Columna 'deuda' agregada a la tabla vehiculos")
except sqlite3.OperationalError as e:
    print("ℹ️ No se pudo agregar la columna (probablemente ya existe):", e)

conn.commit()
conn.close()
