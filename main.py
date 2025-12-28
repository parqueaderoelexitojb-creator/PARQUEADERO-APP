import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import math
import random
import win32print
import win32ui
import win32con
from tkcalendar import DateEntry
from tkinter import simpledialog
import calendar
from PIL import Image, ImageWin
import os
import sys

RUTA_DB = os.path.join(os.path.dirname(__file__), "parqueadero.db")


root = tk.Tk()
root.title("PARQUEADERO EL EXITO J.B")
root.geometry("1100x700")
root.resizable(True, True)
style = ttk.Style()
style.theme_use("clam")
FUENTE_TITULO = ("Segoe UI", 18, "bold")
FUENTE_LABEL = ("Segoe UI", 12)
FUENTE_ENTRY = ("Segoe UI", 12)

# ===== ESTILO GENERAL =====
style = ttk.Style()
style.theme_use("clam")

# Fondo general
style.configure("TFrame", background="#F2F2F2")
style.configure("TLabel", background="#F2F2F2")

# Configuración del estilo para el Notebook
style = ttk.Style()
style.configure("TNotebook",
                background="#f0f0f0",  # Fondo de las pestañas
                borderwidth=0)  # Sin bordes adicionales

style.configure("TNotebook.Tab", 
                background="#d3d3d3",  # Color de las pestañas inactivas
                padding=10)  # Espaciado del texto en las pestañas

style.map("TNotebook.Tab", 
          background=[("selected", "#4CAF50")])  # Color de la pestaña seleccionada

# Estilo de los botones
style.configure("TButton", 
                font=("Arial", 12, "bold"),  # Cambiar el tipo de fuente
                padding=10,  # Tamaño de los botones
                relief="flat",  # Sin bordes
                background="#4CAF50",  # Color de fondo
                foreground="white")  # Color del texto

# Botón al pasar el mouse
style.map("TButton", 
          background=[("active", "#45a049")])  # Color cuando el botón está activo (pasando el mouse)

# Estilo de las entradas de texto
style.configure("TEntry",
                font=("Arial", 12),  # Fuente de la entrada
                padding=5,  # Tamaño de la entrada
                relief="sunken",  # Tipo de borde
                background="#ffffff",  # Fondo blanco
                foreground="black")  # Color de texto

# Estilo de las etiquetas
style.configure("TLabel",
                font=("Arial", 12),  # Cambiar la fuente de las etiquetas
                background="#f0f0f0",  # Color de fondo de las etiquetas
                foreground="black")  # Color del texto

conexion = sqlite3.connect(RUTA_DB)
cursor = conexion.cursor()



def asegurar_columna_deuda():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    try:
        cursor.execute("ALTER TABLE vehiculos ADD COLUMN deuda INTEGER DEFAULT 0")
        conexion.commit()
        print("✅ Columna deuda creada")
    except sqlite3.OperationalError:
        print("ℹ️ Columna deuda ya existe")

    conexion.close()

def asegurar_columnas_cierres():
    columnas = [
        "diario_efectivo REAL DEFAULT 0",
        "diario_transferencia REAL DEFAULT 0",
        "mensualidades_efectivo REAL DEFAULT 0",
        "mensualidades_transferencia REAL DEFAULT 0"
    ]

    for col in columnas:
        try:
            cursor.execute(f"ALTER TABLE cierres ADD COLUMN {col}")
            print(f"✅ Columna creada: {col}")
        except sqlite3.OperationalError:
            pass  # ya existe

    conexion.commit()

asegurar_columnas_cierres()

def crear_tablas():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT,
        nombre TEXT,
        telefono TEXT,
        tipo TEXT,
        fecha_ingreso TEXT,
        hora_ingreso TEXT,
        fecha_salida TEXT,
        hora_salida TEXT,
        total INTEGER,
        deuda REAL DEFAULT 0,
        metodo_pago TEXT,
        estado TEXT
    )
    """)

    conexion.commit()
    conexion.close()


def reparar_tabla_mensualidades():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    try:
        cursor.execute("ALTER TABLE mensualidades ADD COLUMN metodo_pago TEXT")
        print("✅ metodo_pago agregado a mensualidades")
    except sqlite3.OperationalError as e:
        print("ℹ️ mensualidades:", e)

    conexion.commit()
    conexion.close()

def agregar_columnas_si_no_existen():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    try:
        cursor.execute("ALTER TABLE vehiculos ADD COLUMN metodo_pago TEXT")
    except sqlite3.OperationalError:
        pass  # ya existe

    conexion.commit()
    conexion.close()

def reparar_tabla_pagos():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    try:
        cursor.execute("ALTER TABLE pagos ADD COLUMN metodo_pago TEXT")
        print("✅ metodo_pago agregado a pagos")
    except sqlite3.OperationalError as e:
        print("ℹ️ pagos:", e)

    conexion.commit()
    conexion.close()

def reparar_base_datos():
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    try:
        cursor.execute("ALTER TABLE vehiculos ADD COLUMN metodo_pago TEXT")
        print("✅ Columna metodo_pago creada")
    except sqlite3.OperationalError as e:
        print("ℹ️ metodo_pago ya existe:", e)

    conexion.commit()
    conexion.close()

def obtener_ruta_db():
    if getattr(sys, 'frozen', False):
        # Cuando es EXE
        base_path = os.path.dirname(sys.executable)
    else:
        # Cuando es Python normal
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, "parqueadero.db")

def actualizar_deuda_por_tiempo(placa, nuevo_total):
    con = sqlite3.connect(RUTA_DB)
    cur = con.cursor()

    cur.execute("""
        SELECT deuda, ultimo_total
        FROM vehiculos
        WHERE placa = ? AND estado='EN_PARQUEO'
    """, (placa,))

    fila = cur.fetchone()
    if not fila:
        con.close()
        return

    deuda_actual, ultimo_total = fila

    # SOLO SUMAMOS LA DIFERENCIA DE TIEMPO
    if nuevo_total > ultimo_total:
        diferencia = nuevo_total - ultimo_total

        cur.execute("""
            UPDATE vehiculos
            SET deuda = deuda + ?, ultimo_total = ?
            WHERE placa = ? AND estado='EN_PARQUEO'
        """, (diferencia, nuevo_total, placa))

        con.commit()

    con.close()


def obtener_deuda_actual(placa):
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT deuda
        FROM vehiculos
        WHERE placa = ? AND estado = 'EN_PARQUEO'
    """, (placa,))

    fila = cursor.fetchone()
    conexion.close()

    return fila[0] if fila else 0

def asegurar_columna_ultimo_total():
    con = sqlite3.connect(RUTA_DB)
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE vehiculos ADD COLUMN ultimo_total REAL DEFAULT 0")
        con.commit()
        print("✅ columna ultimo_total creada")
    except sqlite3.OperationalError:
        print("ℹ️ columna ultimo_total ya existe")
    con.close()

asegurar_columna_ultimo_total()


RUTA_DB = obtener_ruta_db()
print("👉 BASE DE DATOS USADA:", RUTA_DB)

conexion = sqlite3.connect(RUTA_DB)
cursor = conexion.cursor()

# =========================
# CREAR TABLAS (INICIO)
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    tipo TEXT,
    codigo_barras TEXT,
    fecha_ingreso TEXT,
    hora_ingreso TEXT,
    nombre TEXT,
    telefono TEXT,
    cobro_adicional REAL,
    estado TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    fecha_salida TEXT,
    hora_salida TEXT,
    total_original REAL,
    ajuste REAL,
    total_final REAL,
    metodo_pago TEXT,
    cierre INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mensualidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    telefono TEXT,
    placa TEXT,
    tipo_vehiculo TEXT,
    valor REAL,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    estado TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cierres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    hora TEXT,
    total_efectivo REAL,
    total_transferencia REAL,
    total_general REAL
)
""")

conexion.commit()

# =========================
# FIN CREAR TABLAS
# =========================

def imprimir_logo(dc, y):
    ruta_logo = "logo.bmp"

    if not os.path.exists(ruta_logo):
        return y

    img = Image.open(ruta_logo)
    img = img.convert("1")  # CLAVE: nitidez térmica

    ancho_papel = 420      # 58mm
    ancho_logo = 400       # tamaño correcto

    alto_logo = int(img.height * (ancho_logo / img.width))
    x = (ancho_papel - ancho_logo) // 2

    dib = ImageWin.Dib(img)
    dib.draw(
        dc.GetHandleOutput(),
        (x, y, x + ancho_logo, y + alto_logo)
    )

    return y + alto_logo + 10





from datetime import datetime

def generar_codigo_ticket():
    return datetime.now().strftime("%Y%m%d%H%M%S")

# =========================
# TARIFAS POR BLOQUES
# =========================
TARIFAS = {
    "Moto": {
        "diurna": 3000,
        "nocturna": 5000
    },
    "Carro": {
        "diurna": 4000,
        "nocturna": 8000
    },
    "Camión": {
        "diurna": 5000,
        "nocturna": 9000
    },
    "Doble troque": {
        "diurna": 6000,
        "nocturna": 10000
    },
    "Mula": {
        "diurna": 7000,
        "nocturna": 14000
    }
}


IMPRESORA = "XP-58C"
# =========================
# FUNCIÓN IMPRESIÓN INGRESO
# =========================
def agregar_columna_codigo_ticket():
    try:
        cursor.execute("""
            ALTER TABLE ingresos
            ADD COLUMN codigo_ticket TEXT
        """)
        conexion.commit()
    except Exception:
        # La columna ya existe → no hacemos nada
        pass
    agregar_columna_codigo_ticket()

def imprimir_codigo_barras_raw(codigo):
    impresora = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(impresora)

    try:
        win32print.StartDocPrinter(hprinter, 1, ("Barcode", None, "RAW"))
        win32print.StartPagePrinter(hprinter)

        # Centrar
        win32print.WritePrinter(hprinter, b'\x1b\x61\x01')

        # Altura del código
        win32print.WritePrinter(hprinter, b'\x1d\x68\x60')

        # Ancho del código
        win32print.WritePrinter(hprinter, b'\x1d\x77\x02')

        # Imprimir Code128
        datos = codigo.encode("ascii")
        comando = b'\x1d\x6b\x49' + bytes([len(datos)]) + datos
        win32print.WritePrinter(hprinter, comando)

        # Salto de línea
        win32print.WritePrinter(hprinter, b'\n\n')

        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
    finally:
        win32print.ClosePrinter(hprinter)

def eliminar_mensualidad():
    seleccion = tabla_mensualidades.focus()
    if not seleccion:
        messagebox.showwarning("Atención", "Seleccione una mensualidad")
        return

    placa = tabla_mensualidades.item(seleccion)["values"][2]

    if not messagebox.askyesno(
        "Confirmar",
        f"¿Seguro que desea eliminar la mensualidad de la placa {placa}?"
    ):
        return

    try:
        con = sqlite3.connect(RUTA_DB, timeout=10)
        cur = con.cursor()

        cur.execute("""
            DELETE FROM mensualidades
            WHERE placa=?
        """, (placa,))

        con.commit()
        con.close()

        messagebox.showinfo(
            "Mensualidad eliminada",
            f"Mensualidad de la placa {placa} eliminada correctamente"
        )

        cargar_mensualidades()

    except sqlite3.OperationalError as e:
        messagebox.showerror(
            "Base de datos ocupada",
            "La base de datos está siendo usada.\n"
            "Cierre otras operaciones e intente nuevamente."
        )


def imprimir_ticket_ingreso(
    placa, tipo, codigo, fecha, hora,
    nombre, telefono, numero_recibo
 ):
    
    impresora = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(impresora)
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(impresora)

    dc.StartDoc("Ingreso Parqueadero")
    dc.StartPage()
   
    y = 10
    y = imprimir_logo(dc, y)


    
    salto = 28

    fuente = win32ui.CreateFont({
        "name": "Courier New",
        "height": 26,
        "weight": 700
    })
    dc.SelectObject(fuente)

    dc.TextOut(0, y, "PARQUEADERO EL EXITO J.B"); y += salto
    dc.TextOut(0, y, "NIT. 1049432244-4"); y += salto
    dc.TextOut(0, y, "DIAG. 97F BIS # 4 -45 ESTE"); y += salto
    dc.TextOut(0, y, "TEL. 3213432564"); y += salto * 2

    dc.TextOut(0, y, "PREFIJO: FV"); y += salto
    dc.TextOut(0, y, f"No RECIBO: {numero_recibo}"); y += salto * 2

    dc.TextOut(0, y, f"Nombre: {nombre}"); y += salto
    dc.TextOut(0, y, f"Telefono: {telefono}"); y += salto
    dc.TextOut(0, y, f"Placa: {placa}"); y += salto
    dc.TextOut(0, y, f"Tipo: {tipo}"); y += salto
    dc.TextOut(0, y, f"Codigo: {codigo}"); y += salto * 2

    dc.TextOut(0, y, f"Fecha ingreso: {fecha}"); y += salto
    dc.TextOut(0, y, f"Hora entrada: {hora}"); y += salto * 2

    dc.TextOut(0, y, "EL PARQUEADERO NO SE HACE"); y += salto
    dc.TextOut(0, y, "RESPONSABLE POR OBJETOS"); y += salto
    dc.TextOut(0, y, "PERSONALES DENTRO"); y += salto
    dc.TextOut(0, y, "DEL VEHICULO"); y += salto * 2

    dc.TextOut(0, y, "QUEJAS Y RECLAMOS ANTES"); y += salto
    dc.TextOut(0, y, "DE SACAR EL VEHICULO DEL"); y += salto
    dc.TextOut(0, y, "PARQUEADERO"); y += salto * 2

    dc.TextOut(0, y, "* GRACIAS POR SU VISITA *"); y += salto
    
    
    
    
    dc.TextOut(0, y, f"Ticket: {codigo}")


    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()
    win32print.ClosePrinter(hprinter)
    imprimir_codigo_barras_raw(codigo)

def obtener_numero_cierre():
    cursor.execute("SELECT MAX(id) FROM cierres")
    ultimo = cursor.fetchone()[0]
    return (ultimo + 1) if ultimo else 1


def imprimir_ticket_salida(
    placa, nombre, telefono, codigo,
    fecha_ingreso, hora_ingreso,
    fecha_salida, hora_salida,
    total_pagar, numero_recibo
 ):
    # 🔹 GENERAR CÓDIGO ÚNICO DEL TICKET
    codigo_ticket = generar_codigo_ticket()

    impresora = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(impresora)
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(impresora)

    dc.StartDoc("Salida Parqueadero")
    dc.StartPage()
   

    y = 10
    y = imprimir_logo(dc, y)

    salto = 28


    fuente = win32ui.CreateFont({
        "name": "Courier New",
        "height": 26,
        "weight": 700
    })
    dc.SelectObject(fuente)

    # Imprimir información del ticket
    dc.TextOut(0, y, "PARQUEADERO EL EXITO J.B"); y += salto
    dc.TextOut(0, y, "NIT. 1049432244-4"); y += salto
    dc.TextOut(0, y, "DIAG. 97F BIS # 4 -45 ESTE"); y += salto
    dc.TextOut(0, y, "TEL. 3213432564"); y += salto * 2

    dc.TextOut(0, y, "SALIDA VEHICULO"); y += salto
    dc.TextOut(0, y, "PREFIJO: FV"); y += salto
    dc.TextOut(0, y, f"No RECIBO: {numero_recibo}"); y += salto * 2

    dc.TextOut(0, y, f"Nombre: {nombre}"); y += salto
    dc.TextOut(0, y, f"Telefono: {telefono}"); y += salto
    dc.TextOut(0, y, f"Placa: {placa}"); y += salto
    dc.TextOut(0, y, f"Codigo: {codigo}"); y += salto * 2

    dc.TextOut(0, y, f"Fecha ingreso: {fecha_ingreso}"); y += salto
    dc.TextOut(0, y, f"Hora entrada: {hora_ingreso}"); y += salto
    dc.TextOut(0, y, f"Fecha salida: {fecha_salida}"); y += salto
    dc.TextOut(0, y, f"Hora salida: {hora_salida}"); y += salto * 2

    dc.TextOut(0, y, f"TOTAL COBRO: ${int(total_pagar):,}"); y += salto * 2

    dc.TextOut(0, y, "EL PARQUEADERO NO SE HACE"); y += salto
    dc.TextOut(0, y, "RESPONSABLE POR OBJETOS"); y += salto
    dc.TextOut(0, y, "PERSONALES DENTRO"); y += salto
    dc.TextOut(0, y, "DEL VEHICULO"); y += salto * 2

    dc.TextOut(0, y, "QUEJAS Y RECLAMOS ANTES"); y += salto
    dc.TextOut(0, y, "DE SACAR EL VEHICULO DEL"); y += salto
    dc.TextOut(0, y, "PARQUEADERO"); y += salto * 2

    dc.TextOut(0, y, "* GRACIAS POR SU VISITA *"); y += salto * 2

    # Imprimir número (opcional, debajo del código)
    dc.TextOut(0, y, codigo_ticket); y += salto * 2

   

    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()
    win32print.ClosePrinter(hprinter)

    # 🔥 IMPRIMIR CÓDIGO DE BARRAS REAL
    imprimir_codigo_barras_raw(codigo_ticket)


# =========================
# IMPRESION CIERRE DE CAJA
# =========================
def imprimir_cierre_caja(
    cierre_id,
    fecha,
    hora,
    total_efectivo,
    total_transferencia,
    mensualidades_efectivo,
    mensualidades_transferencia,
    total_general
 ):
    import win32print
    import win32ui

    codigo_ticket = f"CIERRE-{cierre_id}"

    impresora = win32print.GetDefaultPrinter()
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(impresora)

    dc.StartDoc("Cierre de Caja")
    dc.StartPage()

    fuente = win32ui.CreateFont({
        "name": "Arial",
        "height": 26,
        "weight": 400
    })
    dc.SelectObject(fuente)

    y = 0
    salto = 32

    # =========================
    # ENCABEZADO
    # =========================
    dc.TextOut(0, y, "PARQUEADERO EL EXITO J.B"); y += salto
    dc.TextOut(0, y, "NIT 1049432244-4"); y += salto
    dc.TextOut(0, y, "DIAG 97F BIS #4-45 ESTE"); y += salto
    dc.TextOut(0, y, "TEL 3213432564"); y += salto * 2

    dc.TextOut(0, y, "CIERRE DE CAJA"); y += salto
    dc.TextOut(0, y, f"N° CIERRE: {cierre_id}"); y += salto
    dc.TextOut(0, y, f"Fecha: {fecha}   Hora: {hora}"); y += salto * 2

    # =========================
    # PARQUEO DIARIO
    # =========================
    dc.TextOut(0, y, "---- PARQUEO DIARIO ----"); y += salto
    dc.TextOut(0, y, f"Efectivo: ${int(total_efectivo):,}"); y += salto
    dc.TextOut(0, y, f"Transferencia: ${int(total_transferencia):,}"); y += salto * 2

    # =========================
    # MENSUALIDADES
    # =========================
    dc.TextOut(0, y, "---- MENSUALIDADES ----"); y += salto
    dc.TextOut(0, y, f"Efectivo: ${int(mensualidades_efectivo):,}"); y += salto
    dc.TextOut(0, y, f"Transferencia: ${int(mensualidades_transferencia):,}"); y += salto * 2

    # =========================
    # TOTAL GENERAL
    # =========================
    dc.TextOut(0, y, "-" * 32); y += salto
    dc.TextOut(0, y, f"TOTAL GENERAL: ${int(total_general):,}"); y += salto * 2

    dc.TextOut(0, y, "CIERRE GENERADO POR SISTEMA"); y += salto
    dc.TextOut(0, y, f"Codigo cierre: {codigo_ticket}")

    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()

    imprimir_codigo_barras_raw(codigo_ticket)



def imprimir_lista_parqueo():
    cursor.execute("""
        SELECT placa, tipo, nombre, telefono,
               fecha_ingreso, hora_ingreso
        FROM vehiculos
        WHERE estado='EN_PARQUEO'
        ORDER BY fecha_ingreso, hora_ingreso
    """)
    filas = cursor.fetchall()

    if not filas:
        messagebox.showinfo("Parqueo", "No hay vehículos en parqueo")
        return

    impresora = win32print.GetDefaultPrinter()
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(impresora)

    hdc.StartDoc("Lista vehículos en parqueo")
    hdc.StartPage()

    fuente = win32ui.CreateFont({
        "name": "Courier New",
        "height": 28,
        "weight": 700   # NEGRITA
    })
    hdc.SelectObject(fuente)

    x = 0
    y = 0
    salto = 30

    hdc.TextOut(x, y, "LISTA VEHÍCULOS EN PARQUEO"); y += salto * 2
    hdc.TextOut(x, y, "PLACA  TIPO  FEC  HORA"); y += salto
    hdc.TextOut(x, y, "-" * 30); y += salto

    for placa, tipo, nombre, telefono, fecha, hora in filas:
        fecha_corta = datetime.strptime(
            fecha, "%Y-%m-%d"
        ).strftime("%d/%m")

        linea = f"{placa:<6} {tipo[:4]:<4} {fecha_corta:<5} {hora[:5]}"
        hdc.TextOut(x, y, linea)
        y += salto

        if y > 900:
            hdc.EndPage()
            hdc.StartPage()
            hdc.SelectObject(fuente)
            y = 0

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()

    messagebox.showinfo(
        "Impresión",
        "Listado de parqueo impreso correctamente"
    )

def actualizar_numero_cierre():
    cursor.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM cierres")
    siguiente = cursor.fetchone()[0]
    cierre_numero_var.set(siguiente)

    # =========================
    # PAGOS DIARIOS
    # =========================
    cursor.execute("""
        SELECT
            IFNULL(SUM(CASE WHEN metodo_pago='EFECTIVO' THEN total_final ELSE 0 END), 0),
            IFNULL(SUM(CASE WHEN metodo_pago='TRANSFERENCIA' THEN total_final ELSE 0 END), 0)
        FROM pagos
        WHERE cierre IS NULL
          AND total_original > 0
    """)
    diarios_efectivo, diario_transferencia = cursor.fetchone()

    # =========================
    # MENSUALIDADES
    # =========================
    cursor.execute("""
        SELECT
            IFNULL(SUM(CASE WHEN metodo_pago='EFECTIVO' THEN total_final ELSE 0 END), 0),
            IFNULL(SUM(CASE WHEN metodo_pago='TRANSFERENCIA' THEN total_final ELSE 0 END), 0)
        FROM pagos
        WHERE cierre IS NULL
          AND total_original = 0
    """)
    mensual_efectivo, mensual_transferencia = cursor.fetchone()

    # =========================
    # MOSTRAR EN PANTALLA
    # =========================
    cierre_efectivo_var.set(diario_efectivo)
    cierre_transferencia_var.set(diario_transferencia)

    cierre_mensualidades_efectivo_var.set(mensual_efectivo)
    cierre_mensualidades_transferencia_var.set(mensual_transferencia)

    total_general = (
        diario_efectivo +
        diario_transferencia +
        mensual_efectivo +
        mensual_transferencia
    )

    cierre_total_var.set(total_general)

  


from datetime import datetime, timedelta

def calcular_tarifa_bloques(tipo, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida):
    entrada = datetime.strptime(f"{fecha_ingreso} {hora_ingreso}", "%Y-%m-%d %H:%M:%S")
    salida = datetime.strptime(f"{fecha_salida} {hora_salida}", "%Y-%m-%d %H:%M:%S")

    tarifas = TARIFAS.get(tipo)
    if not tarifas:
        return 0

    tarifa_diurna = tarifas["diurna"]
    tarifa_nocturna = tarifas["nocturna"]

    total = 0
    entro_como = ""
    
    # ───────── INGRESO ─────────
    hora_ing = entrada.hour
    if 5 <= hora_ing < 15:  # Ingreso diurno (5 AM - 3 PM)
        total += tarifa_diurna
        entro_como = "DIA"
    else:  # Ingreso nocturno (3 PM - 5 AM)
        total += tarifa_nocturna
        entro_como = "NOCHE"

    # Variables de control para las tarifas acumuladas
    ultimo_dia = entrada.date() if entro_como == "DIA" else None

    ultima_noche = entrada.date() if entro_como == "NOCHE" else None

    actual = entrada  # Empezamos desde el momento de ingreso

    # ───────── SUMAR TARIFAS DURANTE LA PERMANENCIA ─────────
    while actual < salida:
        actual += timedelta(minutes=1)

        # ───── SUMAR TARIFA NOCTURNA (7 PM) ─────
        if actual.hour == 19 and actual.minute == 0:  # Cambio a tarifa nocturna a las 7 PM
            if ultima_noche != actual.date() and entro_como != "NOCHE":
                total += tarifa_nocturna
                ultima_noche = actual.date()

        # ───── SUMAR TARIFA DIURNA (11 AM) ─────
        if actual.hour == 11 and actual.minute == 0:  # Cambio a tarifa diurna a las 11 AM
            if ultimo_dia != actual.date():
                total += tarifa_diurna
                ultimo_dia = actual.date()
                entro_como = "DIA"

    return total




def imprimir_ticket_mensualidad(
    nombre,
    telefono,
    placa,
    tipo,
    valor,
    fecha_inicio,
    fecha_fin
):
    import win32print
    import win32ui

    codigo_ticket = generar_codigo_ticket()
    valor = float(valor)

    impresora = win32print.GetDefaultPrinter()
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(impresora)

    dc.StartDoc("Mensualidad Parqueadero")
    dc.StartPage()

    # LOGO
    y = 10
    y = imprimir_logo(dc, y)

    # FUENTE
    fuente = win32ui.CreateFont({
        "name": "Arial",
        "height": 28,
        "weight": 400
    })
    dc.SelectObject(fuente)

    x = 10
    salto = 35

    # TITULO
    dc.TextOut(0, y, "NIT. 1049432244-4"); y += salto
    dc.TextOut(0, y, "DIAG. 97F BIS # 4 -45 ESTE"); y += salto
    dc.TextOut(0, y, "TEL. 3213432564"); y += salto * 2
    dc.TextOut(x, y, "MENSUALIDAD"); y += salto * 2

    # DATOS CLIENTE
    dc.TextOut(x, y, f"Nombre: {nombre}"); y += salto
    dc.TextOut(x, y, f"Telefono: {telefono}"); y += salto
    dc.TextOut(x, y, f"Placa: {placa}"); y += salto
    dc.TextOut(x, y, f"Tipo: {tipo}"); y += salto * 2

    # FECHAS
    dc.TextOut(x, y, f"Fecha inicio: {fecha_inicio}"); y += salto
    dc.TextOut(x, y, f"Fecha vencimiento: {fecha_fin}"); y += salto * 2

    # VALOR
    dc.TextOut(x, y, f"VALOR MENSUAL: ${int(valor):,}"); y += salto * 2

    # REGLAS
    dc.TextOut(x, y, "EL PARQUEADERO NO SE HACE"); y += salto
    dc.TextOut(x, y, "RESPONSABLE POR OBJETOS"); y += salto
    dc.TextOut(x, y, "PERSONALES DENTRO"); y += salto
    dc.TextOut(x, y, "DEL VEHICULO"); y += salto * 2

    dc.TextOut(x, y, "QUEJAS Y RECLAMOS ANTES"); y += salto
    dc.TextOut(x, y, "DE SACAR EL VEHICULO DEL"); y += salto
    dc.TextOut(x, y, "PARQUEADERO"); y += salto * 2

    dc.TextOut(x, y, "* GRACIAS POR SU VISITA *"); y += salto
    dc.TextOut(x, y, f"Ticket: {codigo_ticket}")

    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()

    imprimir_codigo_barras_raw(codigo_ticket)


# =========================
# FUNCION BUSCAR MENSUAL
# =========================

def buscar_mensualidad():
    placa = mensual_placa_buscar_var.get().strip().upper()

    if not placa:
        messagebox.showwarning("Aviso", "Ingrese una placa")
        return

    for fila in tabla_mensualidades.get_children():
        tabla_mensualidades.delete(fila)

    cursor.execute("""
        SELECT placa, nombre, tipo_vehiculo,
               valor, fecha_inicio, fecha_fin, estado
        FROM mensualidades
        WHERE placa = ?
    """, (placa,))

    resultados = cursor.fetchall()

    if not resultados:
        messagebox.showinfo("Resultado", "No se encontró la mensualidad")
        return

    for fila in resultados:
        tabla_mensualidades.insert("", tk.END, values=fila)

def cargar_mensualidades():
    for fila in tabla_mensualidades.get_children():
        tabla_mensualidades.delete(fila)

    cursor.execute("""
        SELECT placa, nombre, tipo_vehiculo,
               valor, fecha_inicio, fecha_fin, estado
        FROM mensualidades
        ORDER BY fecha_fin
    """)

    filas = cursor.fetchall()
    hoy = date.today()

    for placa, nombre, tipo, valor, inicio, fin, estado in filas:
        # convertir fecha
        fecha_fin = datetime.strptime(fin, "%Y-%m-%d").date()

        deuda = calcular_deuda(fecha_fin, valor)

        if deuda > 0:
            tag = "VENCIDA"
            estado = "VENCIDA"
        else:
            tag = "ACTIVA"
            estado = "ACTIVA"

        tabla_mensualidades.insert(
            "",
            tk.END,
            values=(
                placa,
                nombre,
                tipo,
                f"${int(valor):,}",
                inicio,
                fin,
                estado,
                f"${int(deuda):,}"
            ),
            tags=(tag,)
        )


def total_diarios(metodo):
    cursor.execute("""
        SELECT IFNULL(SUM(total_final), 0)
        FROM pagos
        WHERE metodo_pago=?
          AND total_original > 0
          AND cierre IS NULL
    """, (metodo,))
    return cursor.fetchone()[0]

def abonar_vehiculo():
    seleccion = tabla_parqueo.focus()
    if not seleccion:
        messagebox.showwarning("Atención", "Seleccione un vehículo")
        return

    placa = tabla_parqueo.item(seleccion)["values"][0]

    # 1️⃣ DATOS DEL VEHÍCULO
    cursor.execute("""
        SELECT tipo, fecha_ingreso, hora_ingreso, cobro_adicional
        FROM vehiculos
        WHERE placa=? AND estado='EN_PARQUEO'
    """, (placa,))
    fila = cursor.fetchone()

    if not fila:
        messagebox.showerror("Error", "Vehículo no encontrado")
        return

    tipo, fecha_ing, hora_ing, cobro_adic = fila

    # 2️⃣ TARIFA DE PARQUEO REAL
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%Y-%m-%d")
    hora_actual = ahora.strftime("%H:%M:%S")

    tarifa_parqueo = calcular_tarifa_bloques(
        tipo,
        fecha_ing,
        hora_ing,
        fecha_actual,
        hora_actual
    )

    # 3️⃣ TOTAL ABONADO
    cursor.execute("""
        SELECT IFNULL(SUM(total_final), 0)
        FROM pagos
        WHERE placa=?
          AND metodo_pago='ABONO'
    """, (placa,))
    total_abonado = cursor.fetchone()[0]

    # 4️⃣ DEUDA REAL
    deuda_real = tarifa_parqueo + (cobro_adic or 0) - total_abonado
    if deuda_real < 0:
        deuda_real = 0

    # 5️⃣ MOSTRAR DEUDA CORRECTA
    if deuda_real <= 0:
        messagebox.showinfo("Sin deuda", "Este vehículo no tiene deuda")
        return

    monto = simpledialog.askinteger(
        "Abonar",
        f"Tarifa parqueo: ${int(tarifa_parqueo):,}\n"
        f"Cobro adicional: ${int(cobro_adic or 0):,}\n"
        f"Abonado: ${int(total_abonado):,}\n\n"
        f"DEUDA ACTUAL: ${int(deuda_real):,}\n\n"
        "Ingrese monto a abonar:"
    )

    if monto is None:
        return

    if monto <= 0:
        messagebox.showerror("Error", "Monto inválido")
        return

    if monto > deuda_real:
        messagebox.showerror("Error", "El abono no puede ser mayor a la deuda")
        return

    # 6️⃣ REGISTRAR ABONO
    cursor.execute("""
        INSERT INTO pagos
        (placa, fecha_salida, hora_salida,
         total_original, ajuste, total_final, metodo_pago)
        VALUES (?, ?, ?, ?, 0, ?, 'ABONO')
    """, (
        placa,
        fecha_actual,
        hora_actual,
        monto,
        monto
    ))

    conexion.commit()

    messagebox.showinfo(
        "Abono registrado",
        f"Abono: ${monto:,}\n"
        f"Deuda restante: ${int(deuda_real - monto):,}"
    )

    cargar_parqueo()



# =========================
# FUNCION SUMAR MENSUALIDADES VENCIDAS
# =========================
from datetime import datetime, date

def total_mensualidades(metodo):
    cursor.execute("""
        SELECT IFNULL(SUM(total_final), 0)
        FROM pagos
        WHERE metodo_pago=?
          AND total_original = 0
          AND cierre IS NULL
    """, (metodo,))
    return cursor.fetchone()[0]

def calcular_meses_vencidos(fecha_fin):
    hoy = date.today()

    if hoy <= fecha_fin:
        return 0

    meses = (hoy.year - fecha_fin.year) * 12 + (hoy.month - fecha_fin.month)

    # SI PASÓ AL SIGUIENTE MES, CUENTA COMO OTRO
    if hoy.day > fecha_fin.day:
        meses += 1

    return meses



def calcular_deuda(fecha_fin, valor_mensual):
    hoy = date.today()

    # Si aún no ha vencido
    if hoy <= fecha_fin:
        return 0

    # Diferencia base de meses
    meses = (hoy.year - fecha_fin.year) * 12 + (hoy.month - fecha_fin.month)

    # Ajuste por día del mes
    if hoy.day >= fecha_fin.day:
        meses += 1

    # Seguridad: nunca negativo
    if meses < 0:
        meses = 0

    return meses * valor_mensual

def obtener_total_abonado(placa):
    cursor.execute("""
        SELECT IFNULL(SUM(total_final), 0)
        FROM pagos
        WHERE placa=?
          AND metodo_pago='ABONO'
    """, (placa,))
    return cursor.fetchone()[0]

def obtener_mensualidades_efectivo():
    cursor.execute("""
        SELECT IFNULL(SUM(total_final), 0)
        FROM pagos
        WHERE metodo_pago='EFECTIVO'
          AND total_original = 0
          AND cierre IS NULL
    """)
    return cursor.fetchone()[0]


def obtener_mensualidades_transferencia():
    cursor.execute("""
        SELECT IFNULL(SUM(total_final), 0)
        FROM pagos
        WHERE metodo_pago='TRANSFERENCIA'
          AND total_original = 0
          AND cierre IS NULL
    """)
    return cursor.fetchone()[0]







# =========================
# CONTROL DE SALIDA
# =========================
placa_actual = [None]

# =========================
# INGRESO
# =========================
def guardar_vehiculo():
    placa = placa_var.get().strip().upper()
    nombre = nombre_var.get().strip() or "SIN NOMBRE"
    telefono = telefono_var.get().strip() or "SIN TELÉFONO"
    tipo = tipo_vehiculo.get()
    cobro = cobro_var.get().strip()

    if not placa:
        messagebox.showerror("Error", "Debe ingresar la placa")
        return

    try:
        cobro = int(float(cobro)) if cobro else 0
    except:
        messagebox.showerror("Error", "Cobro adicional inválido")
        return

    cursor.execute(
        "SELECT 1 FROM vehiculos WHERE placa=? AND estado='EN_PARQUEO'",
        (placa,)
    )
    if cursor.fetchone():
        messagebox.showwarning("Duplicado", "La placa ya está en parqueo")
        return

    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    codigo = str(random.randint(1000000000000, 9999999999999))

    deuda_inicial = cobro

    cursor.execute("""
    INSERT INTO vehiculos (
        placa,
        tipo,
        codigo_barras,
        fecha_ingreso,
        hora_ingreso,
        nombre,
        telefono,
        cobro_adicional,
        deuda,
        ultimo_total,
        estado
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'EN_PARQUEO')
 """, (
    placa,
    tipo,
    codigo,
    fecha,
    hora,
    nombre,
    telefono,
    cobro,  # cobro_adicional
    cobro,  # deuda inicial
    cobro   # ultimo_total inicial
 ))



    numero_recibo = cursor.lastrowid
    conexion.commit()

    imprimir_ticket_ingreso(
        placa,
        tipo,
        codigo,
        fecha,
        hora,
        nombre,
        telefono,
        numero_recibo
    )


    messagebox.showinfo(
        "Ingreso",
        f"Vehículo ingresado\nPlaca: {placa}"
    )

    placa_var.set("")
    nombre_var.set("")
    telefono_var.set("")
    cobro_var.set("")
    entrada_placa.focus()

# =========================
# PARQUEO
# =========================
def cargar_parqueo():
    for fila in tabla_parqueo.get_children():
        tabla_parqueo.delete(fila)

    cursor.execute("""
        SELECT placa, nombre, telefono, tipo,
               fecha_ingreso, hora_ingreso,
               cobro_adicional, deuda
        FROM vehiculos
        WHERE estado='EN_PARQUEO'
        ORDER BY fecha_ingreso, hora_ingreso
    """)

    ahora = datetime.now()
    fecha_salida = ahora.strftime("%Y-%m-%d")
    hora_salida = ahora.strftime("%H:%M:%S")

    for (
        placa, nombre, telefono, tipo,
        fecha_ing, hora_ing,
        cobro_adic, deuda
    ) in cursor.fetchall():

        # 🔹 cálculo SOLO VISUAL (no se guarda)
        total_bloques = calcular_tarifa_bloques(
            tipo,
            fecha_ing,
            hora_ing,
            fecha_salida,
            hora_salida
        )

        total_teorico = total_bloques + cobro_adic

        tabla_parqueo.insert(
            "",
            tk.END,
            values=(
                placa,
                nombre,
                telefono,
                tipo,
                fecha_ing,
                hora_ing,
                deuda,          # 👈 deuda real (con abonos)
                total_teorico   # 👈 solo informativo
            )
        )





# =========================
# SALIDA - BUSCAR
# =========================
def buscar_salida_auto(event=None):
    """
    Se ejecuta automáticamente al escanear el código de barras
    (Enter del lector).
    Usa exactamente la misma lógica de buscar_salida().
    """
    codigo = codigo_salida_var.get().strip()

    if not codigo:
        return

    # Limpia placa manual para evitar conflictos
    placa_salida_var.set("")

    # Ejecuta la búsqueda normal
    buscar_salida()

def buscar_salida():
    placa = placa_salida_var.get().strip().upper()
    codigo = codigo_salida_var.get().strip()

    if not placa and not codigo:
        messagebox.showerror("Error", "Ingrese placa o código de barras")
        return

    if codigo:
        cursor.execute("""
            SELECT placa, tipo, fecha_ingreso, hora_ingreso,
                   cobro_adicional, deuda, ultimo_total
            FROM vehiculos
            WHERE codigo_barras=? AND estado='EN_PARQUEO'
        """, (codigo,))
    else:
        cursor.execute("""
            SELECT placa, tipo, fecha_ingreso, hora_ingreso,
                   cobro_adicional, deuda, ultimo_total
            FROM vehiculos
            WHERE placa=? AND estado='EN_PARQUEO'
        """, (placa,))

    fila = cursor.fetchone()
    if fila is None:
        messagebox.showerror("Error", "Vehículo no encontrado o ya salió")
        return

    placa_db, tipo, fecha_ing, hora_ing, cobro_adic, deuda_guardada, ultimo_total = fila

    # 🔥 CALCULAR TOTAL REAL POR TIEMPO
    ahora = datetime.now()
    fecha_salida = ahora.strftime("%Y-%m-%d")
    hora_salida = ahora.strftime("%H:%M:%S")

    total_actual = calcular_tarifa_bloques(
        tipo,
        fecha_ing,
        hora_ing,
        fecha_salida,
        hora_salida
    ) + (cobro_adic or 0)

    # 🔥 OBTENER ABONOS REALES
    total_abonado = obtener_total_abonado(placa_db)

    # 🔥 DEUDA REAL DEFINITIVA
    deuda_real = total_actual - total_abonado
    if deuda_real < 0:
        deuda_real = 0

    # 🔥 ACTUALIZAR BD (SIN REVIVIR DEUDA)
    cursor.execute("""
        UPDATE vehiculos
        SET deuda = ?, ultimo_total = ?
        WHERE placa=? AND estado='EN_PARQUEO'
    """, (deuda_real, total_actual, placa_db))

    conexion.commit()

    # ✅ MOSTRAR VALOR CORRECTO
    total_original_var.set(deuda_real)
    total_final_var.set(deuda_real)

    placa_actual[0] = placa_db
    actualizar_total_final()





def actualizar_total_final():
    try:
        descuento = float(descuento_var.get() or 0)
        recargo = float(recargo_var.get() or 0)
    except:
        return

    total = total_original_var.get() - descuento + recargo
    total_final_var.set(total)

    from datetime import date
    import calendar

def calcular_fecha_fin(fecha_inicio):
    año = fecha_inicio.year
    mes = fecha_inicio.month + 1

    if mes > 12:
        mes = 1
        año += 1

    # Último día del mes destino
    ultimo_dia_mes = calendar.monthrange(año, mes)[1]

    # Mantener el día si existe, si no usar el último
    dia = min(fecha_inicio.day, ultimo_dia_mes)

    return date(año, mes, dia)


# =========================
# MENSUALIDADES
# =========================
def guardar_mensualidad():
    nombre = mensual_nombre_var.get().strip()
    telefono = mensual_telefono_var.get().strip()
    placa = mensual_placa_var.get().strip().upper()
    tipo = mensual_tipo_var.get().strip()
    valor_texto = mensual_valor_var.get().strip()
    fecha_inicio = mensual_fecha_var.get().strip()

    # VALIDAR CAMPOS OBLIGATORIOS
    if not nombre or not placa or not valor_texto or not fecha_inicio:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    # VALIDAR Y LIMPIAR VALOR
    try:
        valor = float(
            valor_texto.replace("$", "").replace(",", "")
        )
    except ValueError:
        messagebox.showerror("Error", "Valor inválido")
        return

    if valor <= 0:
        messagebox.showerror("Error", "El valor debe ser mayor a 0")
        return

    # VALIDAR FECHA
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Fecha inválida (YYYY-MM-DD)")
        return

    # VALIDAR PLACA DUPLICADA
    cursor.execute("""
        SELECT 1
        FROM mensualidades
        WHERE placa = ? AND estado = 'ACTIVA'
    """, (placa,))

    if cursor.fetchone():
        messagebox.showerror(
            "Placa duplicada",
            f"La placa {placa} ya tiene una mensualidad activa"
        )
        return

    # CALCULAR FECHA FIN
    fecha_fin_dt = calcular_fecha_fin(fecha_inicio_dt)

    # =========================
    # 🔥 MÉTODO DE PAGO
    # =========================
    metodo = messagebox.askquestion(
        "Método de pago",
        "¿Cómo se realizó el pago?\n\nSí = EFECTIVO\nNo = TRANSFERENCIA"
    )

    if metodo == "yes":
        metodo_pago = "EFECTIVO"
    else:
        metodo_pago = "TRANSFERENCIA"

    # =========================
    # GUARDAR MENSUALIDAD
    # =========================
    cursor.execute("""
        INSERT INTO mensualidades
        (nombre, telefono, placa, tipo_vehiculo,
         valor, fecha_inicio, fecha_fin, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVA')
    """, (
        nombre,
        telefono,
        placa,
        tipo,
        valor,
        fecha_inicio_dt.strftime("%Y-%m-%d"),
        fecha_fin_dt.strftime("%Y-%m-%d")
    ))
    
    conexion.commit()

    # =========================
    # 🔥 REGISTRAR EN PAGOS (CIERRE DE CAJA)
    # =========================
    
    # =========================
    # 🔥 REGISTRAR PAGO EN PAGOS (MENSUALIDAD NUEVA)
    # =========================
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
    INSERT INTO pagos
    (placa, fecha_salida, hora_salida,
     total_original, ajuste, total_final, metodo_pago)
    VALUES (?, ?, ?, ?, ?, ?, ?)
 """, (
    placa,
    fecha,
    hora,
    0,          # 👈 CLAVE: mensualidad SIEMPRE 0
    0,
    valor,
    metodo_pago   # EFECTIVO o TRANSFERENCIA
 ))

    # IMPRIMIR TICKET
    try:
        imprimir_ticket_mensualidad(
            nombre,
            telefono,
            placa,
            tipo,
            valor,
            fecha_inicio_dt.strftime("%Y-%m-%d"),
            fecha_fin_dt.strftime("%Y-%m-%d")
        )
    except Exception as e:
        messagebox.showwarning(
            "Impresión",
            f"La mensualidad se guardó,\npero no se pudo imprimir:\n{e}"
        )

    # ACTUALIZAR TABLA
    cargar_mensualidades()

    # LIMPIAR CAMPOS
    mensual_nombre_var.set("")
    mensual_telefono_var.set("")
    mensual_placa_var.set("")
    mensual_tipo_var.set("")
    mensual_valor_var.set("")
    mensual_fecha_var.set("")

    # MENSAJE FINAL
    messagebox.showinfo(
        "Mensualidad creada",
        f"Placa: {placa}\n"
        f"Valor: ${valor:,.0f}\n"
        f"Vence: {fecha_fin_dt.strftime('%Y-%m-%d')}"
    )


def abrir_ventana_pago_mensualidad():
    seleccionado = tabla_mensualidades.focus()

    if not seleccionado:
        messagebox.showerror("Error", "Seleccione una mensualidad")
        return

    datos = tabla_mensualidades.item(seleccionado)["values"]
    placa = datos[0]

    # 🔎 CONSULTAR LA MENSUALIDAD REAL EN BD
    cursor.execute("""
        SELECT fecha_fin, valor, nombre, telefono
        FROM mensualidades
        WHERE placa=?
        ORDER BY id DESC
        LIMIT 1
    """, (placa,))

    fila = cursor.fetchone()
    if not fila:
        messagebox.showerror("Error", "No se encontró la mensualidad")
        return

    fecha_fin, valor, nombre, telefono = fila

    # =========================
    # CALCULAR MESES VENCIDOS
    # =========================
    hoy = date.today()
    fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

    meses = (hoy.year - fecha_fin_dt.year) * 12 + (hoy.month - fecha_fin_dt.month)

    if hoy.day >= fecha_fin_dt.day:
        meses += 1

    if meses < 1:
        meses = 1

    # =========================
    # PREGUNTAR MESES A PAGAR
    # =========================
    meses_pagados = simpledialog.askinteger(
        "Pago mensualidad",
        f"Meses vencidos: {meses}\n¿Cuántos meses desea pagar?",
        minvalue=1,
        maxvalue=meses
    )

    if not meses_pagados:
        return

    # =========================
    # VENTANA MÉTODO DE PAGO
    # =========================
    ventana = tk.Toplevel()
    ventana.title("Método de pago")
    ventana.geometry("300x200")
    ventana.grab_set()

    metodo_var = tk.StringVar()

    tk.Label(ventana, text="Seleccione método de pago").pack(pady=10)

    tk.Radiobutton(
        ventana, text="EFECTIVO",
        variable=metodo_var, value="EFECTIVO"
    ).pack()

    tk.Radiobutton(
        ventana, text="TRANSFERENCIA",
        variable=metodo_var, value="TRANSFERENCIA"
    ).pack()

    tk.Button(
        ventana,
        text="CONFIRMAR PAGO",
        bg="green",
        fg="white",
        command=lambda: confirmar_pago_mensualidad(
            placa,
            metodo_var.get(),
            meses_pagados,
            ventana
        )
    ).pack(pady=15)



def confirmar_pago_mensualidad(placa, metodo, meses_pagados, ventana):

   if not metodo:
        messagebox.showerror("Error", "Seleccione un método de pago")
        return


    # OBTENER ÚLTIMA MENSUALIDAD + DATOS CLIENTE
   cursor.execute("""
        SELECT valor, fecha_fin, nombre, telefono
        FROM mensualidades
        WHERE placa=?
        ORDER BY id DESC
        LIMIT 1
    """, (placa,))
   fila = cursor.fetchone()

   if not fila:
        messagebox.showerror("Error", "Mensualidad no encontrada")
        return

   valor, fecha_fin, nombre, telefono = fila

    # ASEGURAR DATE
   if isinstance(fecha_fin, str):
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
   elif isinstance(fecha_fin, datetime):
        fecha_fin_dt = fecha_fin.date()
   else:
        fecha_fin_dt = fecha_fin

   # CALCULAR MESES VENCIDOS
   meses_vencidos = calcular_meses_vencidos(fecha_fin_dt)

   if meses_vencidos <= 0:
    messagebox.showinfo("Sin deuda", "Esta mensualidad no tiene deuda")
    return

   # TOTAL A PAGAR
   total_pagar = meses_pagados * float(valor)

   # NUEVAS FECHAS
   nueva_inicio = fecha_fin_dt
   nueva_fin = fecha_fin_dt

   for _ in range(meses_pagados):
    nueva_fin = calcular_fecha_fin(nueva_fin)

   # 🔴 ESTADO CORRECTO
   meses_restantes = meses_vencidos - meses_pagados

   if meses_restantes > 0:
    nuevo_estado = "VENCIDA"
   else:
    nuevo_estado = "ACTIVA"

   # UPDATE
   cursor.execute("""
    UPDATE mensualidades
    SET fecha_inicio=?,
        fecha_fin=?,
        estado=?
    WHERE placa=?
 """, (
    nueva_inicio.strftime("%Y-%m-%d"),
    nueva_fin.strftime("%Y-%m-%d"),
    nuevo_estado,
    placa
 ))
    
    # 🔥 REGISTRAR PAGO DE MENSUALIDAD EN PAGOS
   cursor.execute("""
    INSERT INTO pagos
    (placa, fecha_salida, hora_salida,
     total_original, ajuste, total_final, metodo_pago)
    VALUES (?, ?, ?, ?, ?, ?, ?)
 """, (
    placa,
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%H:%M:%S"),
    0,              # 👈 CLAVE: mensualidad
    0,
    total_pagar,
    metodo
 ))


   conexion.commit()

    # IMPRIMIR RECIBO DE MENSUALIDAD
   imprimir_ticket_mensualidad(
        nombre=nombre,
        telefono=telefono,
        placa=placa,
        tipo="MENSUALIDAD",
        valor=total_pagar,
        fecha_inicio=nueva_inicio.strftime("%Y-%m-%d"),
        fecha_fin=nueva_fin.strftime("%Y-%m-%d")
    )

   ventana.destroy()
   cargar_mensualidades()

   messagebox.showinfo(
        "Pago registrado",
        f"Placa: {placa}\n"
        f"Meses pagados: {meses_pagados}\n"
        f"Total pagado: ${total_pagar:,.0f}\n"
        f"Método: {metodo}"
    )





# =========================
# CONFIRMAR SALIDA
# =========================
def confirmar_salida():
    if not placa_actual[0]:
        messagebox.showerror("Error", "Primero debe buscar el vehículo")
        return

    metodo = metodo_pago.get()
    if not metodo:
        messagebox.showerror(
            "Método de pago",
            "Debe seleccionar Efectivo o Transferencia"
        )
        return

    fecha_salida = datetime.now().strftime("%Y-%m-%d")
    hora_salida = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
        SELECT nombre, telefono, codigo_barras,
               fecha_ingreso, hora_ingreso,
               tipo, cobro_adicional, deuda, ultimo_total
        FROM vehiculos
        WHERE placa=? AND estado='EN_PARQUEO'
    """, (placa_actual[0],))

    resultado = cursor.fetchone()
    if not resultado:
        messagebox.showerror("Error", "No se pudieron obtener los datos del vehículo")
        return

    (
        nombre, telefono, codigo,
        fecha_ingreso, hora_ingreso,
        tipo, cobro_adic, deuda_actual, ultimo_total
    ) = resultado

    # 🔥 1. CALCULAR TOTAL REAL HASTA AHORA
    total_actual = calcular_tarifa_bloques(
        tipo,
        fecha_ingreso,
        hora_ingreso,
        fecha_salida,
        hora_salida
    ) + (cobro_adic or 0)

    # 🔥 2. CALCULAR SOLO EL INCREMENTO DESDE EL ÚLTIMO CÁLCULO
    incremento = total_actual - (ultimo_total or 0)
    if incremento < 0:
        incremento = 0

    # 🔥 3. SUMAR SOLO EL INCREMENTO A LA DEUDA (ABONOS SE RESPETAN)
    deuda_final = deuda_actual + incremento

    cursor.execute("""
        UPDATE vehiculos
        SET deuda=?, ultimo_total=?
        WHERE placa=? AND estado='EN_PARQUEO'
    """, (deuda_final, total_actual, placa_actual[0]))

    conexion.commit()

    # ✅ ESTE ES EL TOTAL CORRECTO (YA CON ABONOS)
    total_original = deuda_final
    total_original_var.set(total_original)

    # =========================
    # DESCUENTO Y RECARGO
    # =========================
    try:
        descuento = float(descuento_var.get() or 0)
    except ValueError:
        descuento = 0

    try:
        recargo = float(recargo_var.get() or 0)
    except ValueError:
        recargo = 0

    ajuste = recargo - descuento

    total_final = total_original + ajuste
    if total_final < 0:
        total_final = 0

    total_final_var.set(total_final)

    # =========================
    # GUARDAR PAGO
    # =========================
    cursor.execute("""
        INSERT INTO pagos
        (placa, fecha_salida, hora_salida,
         total_original, ajuste, total_final, metodo_pago)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        placa_actual[0],
        fecha_salida,
        hora_salida,
        total_original,
        ajuste,
        total_final,
        metodo
    ))

    numero_recibo = cursor.lastrowid

    # =========================
    # MARCAR COMO SALIDO
    # =========================
    cursor.execute("""
        UPDATE vehiculos
        SET estado='SALIDO'
        WHERE placa=? AND estado='EN_PARQUEO'
    """, (placa_actual[0],))

    conexion.commit()

    if messagebox.askyesno("Imprimir recibo", "¿Desea imprimir el recibo de salida?"):
        imprimir_ticket_salida(
            placa_actual[0],
            nombre,
            telefono,
            codigo,
            fecha_ingreso,
            hora_ingreso,
            fecha_salida,
            hora_salida,
            total_final,
            numero_recibo
        )

    messagebox.showinfo(
        "Salida confirmada",
        f"Vehículo {placa_actual[0]} dado de salida\n"
        f"TOTAL PAGADO: ${total_final:,.0f}"
    )

    # =========================
    # LIMPIAR
    # =========================
    placa_salida_var.set("")
    codigo_salida_var.set("")
    descuento_var.set(0)
    recargo_var.set(0)
    total_original_var.set(0)
    total_final_var.set(0)
    placa_actual[0] = None

    cargar_parqueo()
    cargar_salidas()


def reimprimir_ingreso():
    placa = buscar_placa_parqueo_var.get().strip().upper()


    if not placa:
        messagebox.showerror("Error", "Ingrese una placa")
        return

    cursor.execute("""
        SELECT
            placa,
            tipo,
            codigo_barras,
            fecha_ingreso,
            hora_ingreso,
            nombre,
            telefono,
            id
        FROM vehiculos
        WHERE placa=? AND estado='EN_PARQUEO'
    """, (placa,))

    fila = cursor.fetchone()

    if not fila:
        messagebox.showerror(
            "No encontrado",
            "La placa no está en parqueo"
        )
        return

    placa, tipo, codigo, fecha, hora, nombre, telefono, numero_recibo = fila

    try:
        imprimir_ticket_ingreso(
            placa,
            tipo,
            codigo,
            fecha,
            hora,
            nombre,
            telefono,
            numero_recibo
        )
        messagebox.showinfo(
            "Reimpresión",
            f"Recibo de ingreso reimpreso\nPlaca: {placa}"
        )
    except Exception as e:
        messagebox.showerror(
            "Error impresión",
            f"No se pudo imprimir:\n{e}"
        )


# 🔽 Notebook
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# =========================
# CALCULAR CIERRE DE CAJA
# =========================
def calcular_cierre_caja():

    # =========================
    # PAGOS DIARIOS (INCLUYE ABONOS)
    # =========================
    cursor.execute("""
        SELECT
            IFNULL(SUM(
                CASE 
                    WHEN metodo_pago IN ('EFECTIVO', 'ABONO') 
                    THEN total_final 
                    ELSE 0 
                END
            ), 0),
            IFNULL(SUM(
                CASE 
                    WHEN metodo_pago = 'TRANSFERENCIA' 
                    THEN total_final 
                    ELSE 0 
                END
            ), 0)
        FROM pagos
        WHERE cierre IS NULL
          AND total_original > 0
    """)
    diario_efectivo, diario_transferencia = cursor.fetchone()

    # =========================
    # MENSUALIDADES (INFORMATIVO)
    # =========================
    cursor.execute("""
        SELECT
            IFNULL(SUM(
                CASE 
                    WHEN metodo_pago IN ('EFECTIVO', 'ABONO') 
                    THEN total_final 
                    ELSE 0 
                END
            ), 0),
            IFNULL(SUM(
                CASE 
                    WHEN metodo_pago = 'TRANSFERENCIA' 
                    THEN total_final 
                    ELSE 0 
                END
            ), 0)
        FROM pagos
        WHERE cierre IS NULL
          AND total_original = 0
    """)
    mensual_efectivo, mensualidades_transferencia = cursor.fetchone()

    # =========================
    # TOTALES
    # =========================
    total_diarios = diario_efectivo + diario_transferencia
    total_mensualidades = mensual_efectivo + mensualidades_transferencia
    total_general = total_diarios + total_mensualidades

    # =========================
    # MOSTRAR EN PANTALLA
    # =========================
    cierre_efectivo_var.set(diario_efectivo)
    cierre_transferencia_var.set(diario_transferencia)

    cierre_mensualidades_efectivo_var.set(mensual_efectivo)
    cierre_mensualidades_transferencia_var.set(mensualidades_transferencia)

    cierre_total_var.set(total_general)

    messagebox.showinfo(
        "Cierre de caja",
        "Cierre calculado correctamente"
    )


def reimprimir_mensualidad():
    placa = mensual_placa_buscar_var.get().strip().upper()

    if not placa:
        messagebox.showerror("Error", "Ingrese una placa")
        return

    cursor.execute("""
        SELECT nombre, telefono, placa, tipo_vehiculo,
               valor, fecha_inicio, fecha_fin
        FROM mensualidades
        WHERE placa=?
        ORDER BY id DESC
        LIMIT 1
    """, (placa,))

    fila = cursor.fetchone()

    if not fila:
        messagebox.showerror(
            "No encontrado",
            "No existe mensualidad para esta placa"
        )
        return

    nombre, telefono, placa, tipo, valor, fecha_inicio, fecha_fin = fila

    try:
        imprimir_ticket_mensualidad(
            nombre,
            telefono,
            placa,
            tipo,
            valor,
            fecha_inicio,
            fecha_fin
        )
        messagebox.showinfo(
            "Reimpresión",
            f"Mensualidad reimpresa\nPlaca: {placa}"
        )
    except Exception as e:
        messagebox.showerror(
            "Error impresión",
            f"No se pudo imprimir:\n{e}"
        )

# =========================
# CARGAR SALIDAS
# =========================
def cargar_salidas():
    # 🔄 REFRESCAR TABLA (no duplicar)
    tabla_salidas.delete(*tabla_salidas.get_children())

    cursor.execute("""
        SELECT
            placa,
            fecha_salida,
            hora_salida,
            total_final,
            metodo_pago
        FROM pagos
        ORDER BY id DESC
    """)

    for fila in cursor.fetchall():
        tabla_salidas.insert("", tk.END, values=fila)

    # =========================
    # TOTALES PAGOS DIARIOS
    # =========================
    cursor.execute("""
        SELECT
            IFNULL(SUM(CASE WHEN metodo_pago='EFECTIVO' THEN total_final ELSE 0 END), 0),
            IFNULL(SUM(CASE WHEN metodo_pago='TRANSFERENCIA' THEN total_final ELSE 0 END), 0)
        FROM pagos
        WHERE cierre IS NULL
    """)
    efectivo, transferencia = cursor.fetchone()

    # =========================
    # TOTALES MENSUALIDADES
    # =========================
    cursor.execute("""
        SELECT
            IFNULL(SUM(CASE WHEN metodo_pago='EFECTIVO' THEN valor ELSE 0 END), 0),
            IFNULL(SUM(CASE WHEN metodo_pago='TRANSFERENCIA' THEN valor ELSE 0 END), 0)
        FROM mensualidades
        WHERE estado='ACTIVA'
    """)
    ef_m, tr_m = cursor.fetchone()

    # =========================
    # SUMAR TODO
    # =========================
    total_efectivo = efectivo + ef_m
    total_transferencia = transferencia + tr_m
    total_general = total_efectivo + total_transferencia

    cierre_efectivo_var.set(total_efectivo)
    cierre_transferencia_var.set(total_transferencia)
    cierre_total_var.set(total_general)


def confirmar_cierre_caja():
    # VALIDAR QUE HAYA ALGO PARA CERRAR
    total_general = cierre_total_var.get()

    if total_general <= 0:
        messagebox.showerror(
            "Cierre de caja",
            "No hay valores para realizar el cierre"
        )
        return

    if not messagebox.askyesno(
        "Confirmar cierre",
        "¿Está seguro de realizar el cierre de caja?\n\n"
        "Esta acción no se puede deshacer."
    ):
        return

    # DATOS DEL CIERRE
    cierre_id = cierre_numero_var.get()
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")

    diario_efectivo = cierre_efectivo_var.get()
    diario_transferencia = cierre_transferencia_var.get()
    mensual_efectivo = cierre_mensualidades_efectivo_var.get()
    mensual_transferencia = cierre_mensualidades_transferencia_var.get()
    total_general = cierre_total_var.get()

    # MARCAR PAGOS COMO CERRADOS
    cursor.execute("""
        UPDATE pagos
        SET cierre=?
        WHERE cierre IS NULL
    """, (cierre_id,))

    # GUARDAR REGISTRO DEL CIERRE
    cursor.execute("""
    INSERT INTO cierres (
        fecha,
        hora,
        diario_efectivo,
        diario_transferencia,
        mensualidades_efectivo,
        mensualidades_transferencia,
        total_general
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
 """, (
    fecha,
    hora,
    diario_efectivo,
    diario_transferencia,
    mensual_efectivo,          # ✅ CORRECTO
    mensual_transferencia,     # ✅ CORRECTO
    total_general
 ))



    conexion.commit()

    imprimir_cierre_caja(
    cierre_numero_var.get(),
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%H:%M:%S"),

    cierre_efectivo_var.get(),                    # parqueo diario efectivo
    cierre_transferencia_var.get(),               # parqueo diario transferencia
    cierre_mensualidades_efectivo_var.get(),      # mensualidades efectivo
    cierre_mensualidades_transferencia_var.get(), # mensualidades transferencia
    cierre_total_var.get()                        # total general
 )


    # LIMPIAR VARIABLES
    cierre_efectivo_var.set(0)
    cierre_transferencia_var.set(0)
    cierre_mensualidades_efectivo_var.set(0)
    cierre_mensualidades_transferencia_var.set(0)
    cierre_total_var.set(0)

    # NUEVO NÚMERO DE CIERRE
    nuevo_cierre = obtener_numero_cierre()
    cierre_numero_var.set(nuevo_cierre)

    messagebox.showinfo(
    "Cierre realizado",
    "El cierre se guardó correctamente"
 )



def reiniciar_cierre():
    cierre_efectivo_var.set(0)
    cierre_transferencia_var.set(0)
    cierre_mensualidades_efectivo_var.set(0)
    cierre_mensualidades_transferencia_var.set(0)
    cierre_total_var.set(0)

    # 🔥 ACTUALIZAR NÚMERO DEL SIGUIENTE CIERRE (LA VARIABLE CORRECTA)
    cursor.execute("SELECT IFNULL(MAX(id), 0) + 1 FROM cierres")
    siguiente_cierre = cursor.fetchone()[0]
    cierre_numero_var.set(siguiente_cierre)






# =========================
# PESTAÑAS
# =========================

# ---------- INGRESO ----------
tab_ingreso = ttk.Frame(notebook)
notebook.add(tab_ingreso, text="Ingreso")

# ---------- VEHÍCULOS EN PARQUEO ----------
tab_parqueo = ttk.Frame(notebook)
notebook.add(tab_parqueo, text="Vehículos en Parqueo")

# ---------- VEHÍCULOS CON SALIDA ----------
tab_salidas = ttk.Frame(notebook)
notebook.add(tab_salidas, text="Vehículos con Salida")

# ---------- SALIDA ----------
tab_salida = ttk.Frame(notebook)
notebook.add(tab_salida, text="Salida")

# ---------- MENSUALIDADES ----------
tab_mensualidades = ttk.Frame(notebook)
notebook.add(tab_mensualidades, text="Mensualidades")

# =========================
# VARIABLES CIERRE DE CAJA
# =========================

# Obtener número de cierre ANTES
numero_cierre = obtener_numero_cierre()

# Variables Tkinter
cierre_numero_var = tk.IntVar(value=numero_cierre)

cierre_efectivo_var = tk.DoubleVar(value=0)
cierre_transferencia_var = tk.DoubleVar(value=0)

cierre_mensualidades_efectivo_var = tk.DoubleVar(value=0)
cierre_mensualidades_transferencia_var = tk.DoubleVar(value=0)

cierre_total_var = tk.DoubleVar(value=0)


# ---------- CIERRE DE CAJA ----------
tab_cierre = ttk.Frame(notebook)
notebook.add(tab_cierre, text="Cierre de Caja")

frame_cierre = tk.Frame(tab_cierre, bg="#f4f6f7")
frame_cierre.pack(pady=30, padx=40)

# =========================
# TÍTULO PRINCIPAL
# =========================
tk.Label(
    frame_cierre,
    text="CIERRE DE CAJA",
    font=("Arial", 20, "bold"),
    bg="#f4f6f7",
    fg="#2c3e50"
).grid(row=0, column=0, columnspan=2, pady=(0, 15))

# =========================
# NÚMERO DE CIERRE
# =========================
tk.Label(
    frame_cierre,
    text="N° Cierre:",
    font=("Arial", 11),
    bg="#f4f6f7"
).grid(row=1, column=0, sticky="e", padx=5)

tk.Label(
    frame_cierre,
    textvariable=cierre_numero_var,
    font=("Arial", 12, "bold"),
    bg="#f4f6f7"
).grid(row=1, column=1, sticky="w")

# =========================
# SECCIÓN PARQUEO DIARIO
# =========================
tk.Label(
    frame_cierre,
    text="PARQUEO DIARIO",
    font=("Arial", 13, "bold"),
    bg="#f4f6f7",
    fg="#1f618d"
).grid(row=2, column=0, columnspan=2, pady=(15, 5))

tk.Label(frame_cierre, text="Efectivo:", bg="#f4f6f7").grid(row=3, column=0, sticky="e")
tk.Label(
    frame_cierre,
    textvariable=cierre_efectivo_var,
    font=("Arial", 12, "bold"),
    bg="#f4f6f7"
).grid(row=3, column=1, sticky="w")

tk.Label(frame_cierre, text="Transferencia:", bg="#f4f6f7").grid(row=4, column=0, sticky="e")
tk.Label(
    frame_cierre,
    textvariable=cierre_transferencia_var,
    font=("Arial", 12, "bold"),
    bg="#f4f6f7"
).grid(row=4, column=1, sticky="w")

# =========================
# SECCIÓN MENSUALIDADES
# =========================
tk.Label(
    frame_cierre,
    text="MENSUALIDADES",
    font=("Arial", 13, "bold"),
    bg="#f4f6f7",
    fg="#117a65"
).grid(row=5, column=0, columnspan=2, pady=(15, 5))

tk.Label(frame_cierre, text="Efectivo:", bg="#f4f6f7").grid(row=6, column=0, sticky="e")
tk.Label(
    frame_cierre,
    textvariable=cierre_mensualidades_efectivo_var,
    font=("Arial", 12, "bold"),
    bg="#f4f6f7"
).grid(row=6, column=1, sticky="w")

tk.Label(frame_cierre, text="Transferencia:", bg="#f4f6f7").grid(row=7, column=0, sticky="e")
tk.Label(
    frame_cierre,
    textvariable=cierre_mensualidades_transferencia_var,
    font=("Arial", 12, "bold"),
    bg="#f4f6f7"
).grid(row=7, column=1, sticky="w")

# =========================
# TOTAL GENERAL
# =========================
tk.Label(
    frame_cierre,
    text="TOTAL GENERAL",
    font=("Arial", 14, "bold"),
    bg="#f4f6f7",
    fg="#922b21"
).grid(row=8, column=0, sticky="e", pady=(20, 5))

tk.Label(
    frame_cierre,
    textvariable=cierre_total_var,
    font=("Arial", 16, "bold"),
    bg="#f4f6f7",
    fg="#922b21"
).grid(row=8, column=1, sticky="w")

# =========================
# BOTONES
# =========================
tk.Button(
    frame_cierre,
    text="CALCULAR CIERRE",
    bg="#3498db",
    fg="white",
    font=("Arial", 12, "bold"),
    width=20,
    command=calcular_cierre_caja
).grid(row=9, column=0, columnspan=2, pady=(15, 5))

tk.Button(
    frame_cierre,
    text="CONFIRMAR CIERRE",
    bg="#27ae60",
    fg="white",
    font=("Arial", 12, "bold"),
    width=20,
    command=confirmar_cierre_caja
).grid(row=10, column=0, columnspan=2, pady=(5, 0))



# =========================
# VARIABLES INGRESO
# =========================
placa_var = tk.StringVar()
nombre_var = tk.StringVar()
telefono_var = tk.StringVar()
cobro_var = tk.StringVar()
tipo_vehiculo = tk.StringVar(value="Carro")

# =========================
# VARIABLES MENSUALIDADES
# =========================
mensual_nombre_var = tk.StringVar()
mensual_telefono_var = tk.StringVar()
mensual_placa_var = tk.StringVar()
mensual_tipo_var = tk.StringVar()
mensual_valor_var = tk.StringVar()
mensual_fecha_var = tk.StringVar()
mensual_placa_buscar_var = tk.StringVar()

# =========================
# VARIABLES BUSCAR PARQUEO
# =========================
buscar_placa_parqueo_var = tk.StringVar()




# =========================
# INGRESO
# =========================
frame_ingreso = tk.Frame(tab_ingreso, bg="#F2F2F2")
frame_ingreso.pack(pady=20)

# --- Nombre
ttk.Label(frame_ingreso, text="Nombre", font=("Arial", 13, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
tk.Entry(
    frame_ingreso,
    textvariable=nombre_var,
    font=("Arial", 14),
    width=18,
    bg="lightyellow",
    bd=3,
    relief="solid"
).grid(row=1, column=1, padx=10, pady=10)

# --- Teléfono
ttk.Label(frame_ingreso, text="Teléfono", font=("Arial", 13, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="e")
tk.Entry(
    frame_ingreso,
    textvariable=telefono_var,
    font=("Arial", 14),
    width=18,
    bg="lightyellow",
    bd=3,
    relief="solid"
).grid(row=2, column=1, padx=10, pady=10)

# --- Tipo vehículo
ttk.Label(frame_ingreso, text="Tipo", font=("Arial", 13, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="e")
tipo_combo = ttk.Combobox(
    frame_ingreso,
    textvariable=tipo_vehiculo,
    values=["Moto", "Carro", "Camión", "Doble troque", "Mula"],
    state="readonly",
    font=("Arial", 13),
    width=16
)
tipo_combo.grid(row=3, column=1, padx=10, pady=10)
tipo_combo.current(0)

# --- Cobro adicional
ttk.Label(frame_ingreso, text="Cobro adicional", font=("Arial", 13, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="e")
tk.Entry(
    frame_ingreso,
    textvariable=cobro_var,
    font=("Arial", 14),
    width=18,
    bg="lightyellow",
    bd=3,
    relief="solid"
).grid(row=4, column=1, padx=10, pady=10)

# --- Botón placa
entrada_placa = tk.Entry(
    frame_ingreso,
    textvariable=placa_var,
    bg="yellow",
    font=("Arial", 18, "bold"),
    width=18
)
entrada_placa.grid(row=0, column=1)

# --- Botón principal
tk.Button(
    tab_ingreso,
    text="INGRESAR VEHÍCULO",
    command=guardar_vehiculo,
    font=("Arial", 15, "bold"),
    bg="#2ECC71",
    fg="white",
    activebackground="#27AE60",
    height=2,
    width=25
).pack(pady=25)



# =========================
# VEHÍCULOS EN PARQUEO
# =========================
tk.Button(
    tab_parqueo,
    text="Actualizar",
    command=cargar_parqueo,
    font=("Arial", 12, "bold"),
    bg="#3498DB",
    fg="white",
    width=15
).pack(pady=5)

frame_buscar_parqueo = tk.Frame(tab_parqueo)
frame_buscar_parqueo.pack(pady=5)

tk.Label(
    frame_buscar_parqueo,
    text="Buscar placa",
    font=("Arial", 12, "bold")
).pack(side="left", padx=5)

tk.Entry(
    frame_buscar_parqueo,
    textvariable=buscar_placa_parqueo_var,
    width=15,
    font=("Arial", 12)
).pack(side="left", padx=5)

tk.Button(
    frame_buscar_parqueo,
    text="Reimprimir ingreso",
    command=reimprimir_ingreso,
    font=("Arial", 11),
    bg="#F1C40F"
).pack(side="left", padx=5)

tk.Button(
    tab_parqueo,
    text="IMPRIMIR LISTA DE PARQUEO",
    command=imprimir_lista_parqueo,
    font=("Arial", 12, "bold"),
    bg="#9B59B6",
    fg="white"
).pack(pady=5)

tk.Button(
    tab_parqueo,
    text="ABONAR",
    font=("Arial", 12, "bold"),
    bg="#3498DB",
    fg="white",
    width=14,
    command=abonar_vehiculo
).pack(pady=5)


# --- Tabla
columnas_parqueo = (
    "Placa", "Nombre", "Teléfono", "Tipo",
    "Fecha ingreso", "Hora ingreso", "Adicional"
)

tabla_parqueo = ttk.Treeview(
    tab_parqueo,
    columns=columnas_parqueo,
    show="headings",
    height=12
)

for col in columnas_parqueo:
    tabla_parqueo.heading(col, text=col)
    tabla_parqueo.column(col, anchor="center", width=130)

tabla_parqueo.pack(expand=True, fill="both", padx=10, pady=10)





# =========================
# VEHÍCULOS SALIDOS
# =========================
columnas_salidas = (
    "Placa",
    "Fecha salida",
    "Hora salida",
    "Total cobrado",
    "Método pago"
)

tabla_salidas = ttk.Treeview(
    tab_salidas,
    columns=columnas_salidas,
    show="headings",
    height=8
)

for col in columnas_salidas:
    tabla_salidas.heading(col, text=col)
    tabla_salidas.column(col, anchor="center", width=120)

tabla_salidas.pack(expand=True, fill="both", padx=10, pady=10)

# Botón de actualización con estilo
tk.Button(
    tab_salidas,
    text="Actualizar",
    command=cargar_salidas,
    font=("Arial", 12, "bold"),
    bg="#3498DB",
    fg="white",
    activebackground="#2980B9",
    width=15
).pack(pady=15)



# =========================
# SALIDA - FORMULARIO
# =========================
frame_salida = tk.Frame(tab_salida)
frame_salida.pack(pady=10)

# Variables
placa_salida_var = tk.StringVar()
codigo_salida_var = tk.StringVar()
descuento_var = tk.StringVar()
recargo_var = tk.StringVar()
metodo_pago = tk.StringVar(value="")

total_original_var = tk.DoubleVar(value=0)
total_final_var = tk.DoubleVar(value=0)

# =========================
# CODIGO DE BARRAS (ARRIBA)
# =========================
tk.Label(
    frame_salida,
    text="Código de barras",
    font=("Arial", 12, "bold")
).grid(row=0, column=0, sticky="e", padx=10, pady=5)

entry_codigo_salida = tk.Entry(
    frame_salida,
    textvariable=codigo_salida_var,
    font=("Arial", 14),
    width=18,
    bg="lightyellow",
    bd=3,
    relief="solid"
)
entry_codigo_salida.grid(row=0, column=1, padx=10, pady=5)

entry_codigo_salida.focus()

# 🔥 BUSCAR AUTOMÁTICO AL ESCANEAR
entry_codigo_salida.bind("<Return>", buscar_salida_auto)

# =========================
# PLACA
# =========================
tk.Label(
    frame_salida,
    text="Placa (opcional)",
    font=("Arial", 12, "bold")
).grid(row=1, column=0, sticky="e", padx=10, pady=5)

tk.Entry(
    frame_salida,
    textvariable=placa_salida_var,
    font=("Arial", 13),
    width=16,
    bg="lightyellow",
    bd=2,
    relief="solid"
).grid(row=1, column=1, padx=10, pady=5)

tk.Button(
    frame_salida,
    text="Buscar",
    command=buscar_salida,
    font=("Arial", 12, "bold"),
    bg="#2ECC71",
    fg="white",
    width=12
).grid(row=2, column=0, columnspan=2, pady=10)

# =========================
# TOTAL ORIGINAL
# =========================
tk.Label(
    frame_salida,
    text="Total original",
    font=("Arial", 12, "bold")
).grid(row=3, column=0, columnspan=2, pady=5)

tk.Label(
    frame_salida,
    textvariable=total_original_var,
    font=("Arial", 13, "bold"),
    fg="#27AE60"
).grid(row=4, column=0, columnspan=2)

# =========================
# COLUMNA DERECHA
# =========================
tk.Label(
    frame_salida,
    text="Descuento",
    font=("Arial", 12, "bold")
).grid(row=0, column=2, sticky="e", padx=10, pady=5)

tk.Entry(
    frame_salida,
    textvariable=descuento_var,
    font=("Arial", 13),
    width=14,
    bg="lightyellow",
    bd=2,
    relief="solid"
).grid(row=0, column=3, padx=10, pady=5)

tk.Label(
    frame_salida,
    text="Recargo",
    font=("Arial", 12, "bold")
).grid(row=1, column=2, sticky="e", padx=10, pady=5)

tk.Entry(
    frame_salida,
    textvariable=recargo_var,
    font=("Arial", 13),
    width=14,
    bg="lightyellow",
    bd=2,
    relief="solid"
).grid(row=1, column=3, padx=10, pady=5)

tk.Label(
    frame_salida,
    text="Método de pago",
    font=("Arial", 12, "bold")
).grid(row=2, column=2, columnspan=2, pady=5)

tk.Radiobutton(
    frame_salida,
    text="Efectivo",
    variable=metodo_pago,
    value="EFECTIVO",
    font=("Arial", 12)
).grid(row=3, column=2, columnspan=2, sticky="w", padx=20)

tk.Radiobutton(
    frame_salida,
    text="Transferencia",
    variable=metodo_pago,
    value="TRANSFERENCIA",
    font=("Arial", 12)
).grid(row=4, column=2, columnspan=2, sticky="w", padx=20)

# =========================
# TOTALES Y BOTONES
# =========================
tk.Button(
    tab_salida,
    text="Calcular Total",
    command=actualizar_total_final,
    font=("Arial", 13, "bold"),
    bg="#F39C12",
    fg="white",
    width=18
).pack(pady=10)

tk.Label(
    tab_salida,
    text="TOTAL A PAGAR",
    font=("Arial", 14, "bold")
).pack()

tk.Label(
    tab_salida,
    textvariable=total_final_var,
    font=("Arial", 16, "bold"),
    fg="#E74C3C"
).pack(pady=5)

tk.Button(
    tab_salida,
    text="CONFIRMAR SALIDA",
    command=confirmar_salida,
    font=("Arial", 14, "bold"),
    bg="#2ECC71",
    fg="white",
    width=22,
    height=2
).pack(pady=15)



# =========================
# MENSUALIDADES - FORMULARIO
# =========================
frame_m = tk.Frame(tab_mensualidades)
frame_m.pack(pady=10)
frame_botones_mensualidades = tk.Frame(tab_mensualidades)
frame_botones_mensualidades.pack(pady=5)

tk.Label(frame_m, text="Nombre").grid(row=0, column=0)
tk.Entry(frame_m, textvariable=mensual_nombre_var).grid(row=0, column=1)

tk.Label(frame_m, text="Teléfono").grid(row=1, column=0)
tk.Entry(frame_m, textvariable=mensual_telefono_var).grid(row=1, column=1)

tk.Label(frame_m, text="Placa").grid(row=2, column=0)
tk.Entry(frame_m, textvariable=mensual_placa_var).grid(row=2, column=1)

tk.Label(frame_m, text="Tipo vehículo").grid(row=3, column=0)
tk.Entry(frame_m, textvariable=mensual_tipo_var).grid(row=3, column=1)

tk.Label(frame_m, text="Valor mensual").grid(row=4, column=0)
tk.Entry(frame_m, textvariable=mensual_valor_var).grid(row=4, column=1)

tk.Label(frame_m, text="Fecha inicio").grid(row=5, column=0)

DateEntry(
    frame_m,
    textvariable=mensual_fecha_var,
    date_pattern="yyyy-mm-dd",
    width=18,
    background="darkblue",
    foreground="white",
    borderwidth=2
).grid(row=5, column=1)





tk.Button(
    tab_mensualidades,
    text="GUARDAR MENSUALIDAD",
    command=guardar_mensualidad
).pack(pady=10)

frame_botones = ttk.Frame(tab_mensualidades)
frame_botones.pack(pady=10)

btn_eliminar_mensualidad = ttk.Button(
    frame_botones,
    text="🗑 Eliminar mensualidad",
    command=eliminar_mensualidad
)
btn_eliminar_mensualidad.pack(side="left", padx=5)

# =========================
# MENSUALIDADES - TABLA
# =========================
columnas_m = (
    "Placa", "Nombre", "Tipo", "Valor",
    "Inicio", "Vence", "Estado", "Deuda"
)

tabla_mensualidades = ttk.Treeview(
    tab_mensualidades,
    columns=columnas_m,
    show="headings"
)

# COLORES DE ESTADO
tabla_mensualidades.tag_configure(
    "vencida",
    background="#ffcccc",   # rojo suave
    foreground="black"
)

tabla_mensualidades.tag_configure(
    "activa",
    background="#ccffcc",   # verde suave
    foreground="black"
)

tabla_mensualidades.heading("Placa", text="Placa")
tabla_mensualidades.column("Placa", width=100, anchor="center")

tabla_mensualidades.heading("Nombre", text="Nombre")
tabla_mensualidades.column("Nombre", width=150)

tabla_mensualidades.heading("Tipo", text="Tipo")
tabla_mensualidades.column("Tipo", width=100, anchor="center")

tabla_mensualidades.heading("Valor", text="Valor")
tabla_mensualidades.column("Valor", width=120, anchor="center")

tabla_mensualidades.heading("Inicio", text="Fecha Inicio")
tabla_mensualidades.column("Inicio", width=120, anchor="center")

tabla_mensualidades.heading("Vence", text="Fecha Vencimiento")
tabla_mensualidades.column("Vence", width=120, anchor="center")

tabla_mensualidades.heading("Estado", text="Estado")
tabla_mensualidades.column("Estado", width=100, anchor="center")

tabla_mensualidades.pack(expand=True, fill="both", padx=10, pady=10)

tabla_mensualidades.heading("Deuda", text="Deuda")
tabla_mensualidades.column("Deuda", width=120, anchor="center")  

# =========================
# BUSCAR / REIMPRIMIR / RENOVAR MENSUALIDAD
# =========================
frame_buscar_mensual = tk.Frame(tab_mensualidades)
frame_buscar_mensual.pack(pady=10)

tk.Label(
    frame_buscar_mensual,
    text="Buscar placa"
).pack(side="left", padx=5)

tk.Entry(
    frame_buscar_mensual,
    textvariable=mensual_placa_buscar_var,
    width=25
).pack(side="left", padx=5)

tk.Button(
    frame_buscar_mensual,
    text="Buscar",
    command=buscar_mensualidad
).pack(side="left", padx=5)

tk.Button(
    frame_buscar_mensual,
    text="Reimprimir mensualidad",
    command=reimprimir_mensualidad
).pack(side="left", padx=5)

tk.Button(
    frame_botones_mensualidades,
    text="PAGAR MENSUALIDAD",
    command=abrir_ventana_pago_mensualidad
).pack(side="left", padx=5)



tabla_mensualidades.tag_configure(
    "VENCIDA",
    foreground="red"
)

for c in columnas_m:
    tabla_mensualidades.heading(c, text=c)
    tabla_mensualidades.column(c, anchor="center")

tabla_mensualidades.pack(expand=True, fill="both", padx=10, pady=10)

tk.Button(
    tab_mensualidades,
    text="Actualizar",
    command=cargar_mensualidades
).pack(pady=5) 

# =========================
# INICIO DEL PROGRAMA
# =========================
crear_tablas()

reparar_tabla_pagos()
reparar_tabla_mensualidades()

cargar_salidas()
cargar_mensualidades()
cargar_parqueo()


root.mainloop()
