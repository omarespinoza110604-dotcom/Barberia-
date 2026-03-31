from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

# 🔹 Crear base de datos
def init_db():
    con = sqlite3.connect("barberia.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cortes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barbero TEXT,
        precio REAL,
        fecha DATE
    )
    """)
    con.commit()
    con.close()

init_db()

# 🏠 INICIO
@app.route("/")
def index():
    return render_template("index.html")

# ➕ AGREGAR CORTE
@app.route("/agregar", methods=["POST"])
def agregar():
    barbero = request.form["barbero"].strip().title()  # 🔥 NORMALIZA NOMBRE
    precio = float(request.form["precio"])
    fecha = date.today()

    con = sqlite3.connect("barberia.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO cortes (barbero, precio, fecha) VALUES (?, ?, ?)",
        (barbero, precio, fecha)
    )
    con.commit()
    con.close()

    return redirect("/")

# 📊 REPORTE COMPLETO
@app.route("/reporte")
def reporte():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")

    con = sqlite3.connect("barberia.db")
    cur = con.cursor()

    # 🔹 FILTRO POR FECHA
    if desde and hasta:
        cur.execute(
            "SELECT barbero, precio, fecha FROM cortes WHERE fecha BETWEEN ? AND ?",
            (desde, hasta)
        )
    else:
        cur.execute("SELECT barbero, precio, fecha FROM cortes")

    cortes = cur.fetchall()

    # 🔥 AGRUPAR POR BARBERO
    data = {}
    total_general = 0

    for nombre, precio, fecha in cortes:
        total_general += precio

        if nombre not in data:
            data[nombre] = {
                "cortes": [],
                "total": 0
            }

        data[nombre]["cortes"].append(precio)
        data[nombre]["total"] += precio

    # 🔹 FORMATEAR
    barberos = []

    for nombre, info in data.items():
        barberos.append({
            "nombre": nombre,
            "cortes": info["cortes"],
            "total": info["total"],
            "ganancia": info["total"] * 0.5
        })

    # 🔹 BARBERÍA
    ganancia_barberia = total_general * 0.5
    ganancia_por_socio = ganancia_barberia / 4 if ganancia_barberia else 0

    con.close()

    return render_template(
        "reporte.html",
        total=total_general,
        barberos=barberos,
        ganancia_barberia=ganancia_barberia,
        ganancia_por_socio=ganancia_por_socio,
        desde=desde,
        hasta=hasta
    )

# 🚀 EJECUTAR
if __name__ == "__main__":
    app.run()
