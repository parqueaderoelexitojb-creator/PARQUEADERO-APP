import sqlite3
import os

ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parqueadero.db")

conn = sqlite3.connect(ruta)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()

print("📋 Tablas en la base de datos:")
for t in tablas:
    print(" -", t[0])

conn.close()
