from flask import Flask, render_template, request, redirect
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

app = Flask(__name__)

# Load credentials from environment variable
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Open your sheet
sheet = client.open("PublicLogBook").sheet1

@app.route("/")
def index():
    data = sheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    rows.reverse()
    return render_template("index.html", headers=headers, rows=rows)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        sheet.append_row([
            datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
            request.form.get("Plant"),
            request.form.get("Shift"),
            request.form.get("Machine"),
            request.form.get("Department"),
            request.form.get("Person Attended"),
            request.form.get("status"),
            request.form.get("problem"),
            request.form.get("actiontaken"),
            request.form.get("remarks")
        ])
        return redirect("/")

    return render_template("add.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)