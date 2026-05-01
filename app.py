from flask import Flask, render_template, request, redirect, send_file
from openpyxl import Workbook
from datetime import datetime
import psycopg2
import os
import io

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            datetime TEXT,
            shift TEXT,
            machine TEXT,
            operator TEXT,
            status TEXT,
            problem TEXT,
            actiontaken TEXT,
            remarks TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def read_logs():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT datetime, shift, machine, operator, status, problem, actiontaken, remarks
        FROM logs
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.route("/")
def index():
    init_db()
    logs = read_logs()
    return render_template("index.html", logs=logs)

@app.route("/add", methods=["GET", "POST"])
def add():
    init_db()

    if request.method == "POST":
        dt = datetime.now().strftime("%m-%d-%Y %H:%M:%S")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO logs
            (datetime, shift, machine, operator, status, problem, actiontaken, remarks)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            dt,
            request.form.get("shift", ""),
            request.form.get("machine", ""),
            request.form.get("operator", ""),
            request.form.get("status", ""),
            request.form.get("problem", ""),
            request.form.get("actiontaken", ""),
            request.form.get("remarks", "")
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/")

    return render_template("add.html")

@app.route("/export")
def export():
    init_db()
    logs = read_logs()

    wb = Workbook()
    ws = wb.active
    ws.title = "LogBook"

    ws.append([
        "DateTime",
        "Shift",
        "Machine",
        "Operator",
        "Status",
        "Problem",
        "ActionTaken",
        "Remarks"
    ])

    for row in logs:
        ws.append(list(row))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="LogBook.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)