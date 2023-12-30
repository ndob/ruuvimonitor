# Start Flask-instance
#    - per sensor page
#        - history range
#

from flask import Flask, g, render_template, jsonify, request, redirect
from flask import g
import sqlite3

DATABASE_NAME = "file:readings.db"

app = Flask(__name__,
    static_folder="webui/static",
    template_folder="webui/templates")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_NAME + "?mode=ro", uri=True, timeout=10)
    return db

def get_db_mutable():
    db = getattr(g, '_database_mutable', None)
    if db is None:
        db = g._database_mutable = sqlite3.connect(DATABASE_NAME, uri=True, timeout=10)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def query_db_script(query):
    cur = get_db().executescript(query)
    rv = cur.fetchall()
    cur.close()
    return rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    macs = query_db("SELECT DISTINCT mac FROM reading_newest");
    return render_template("index.html", data=[row[0] for row in macs])

@app.route("/detail/<sensormac>")
def detail(sensormac):
    row = query_db("SELECT name FROM sensor_metadata WHERE mac=?", [sensormac]);
    return render_template("detail.html", data=(sensormac, row[0][0] if row else ""))

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/api/sensor/<sensormac>")
def sensor_single(sensormac):
    return jsonify(query_db("SELECT reading.*, sensor_metadata.name FROM reading, reading_newest LEFT JOIN sensor_metadata ON reading.mac = sensor_metadata.mac WHERE reading.rowid=reading_newest.reading_id AND reading.mac=?", [sensormac], True))

@app.route("/api/sensor")
def sensors():
    return jsonify(query_db("SELECT reading.*, sensor_metadata.name FROM reading, reading_newest LEFT JOIN sensor_metadata ON reading.mac = sensor_metadata.mac WHERE reading.rowid=reading_newest.reading_id"))

@app.route("/api/sensor/<sensormac>/history/today")
def history_today(sensormac):
    return jsonify(query_db("SELECT * FROM reading WHERE mac=? AND DATE(timestamp) == DATE('now')", [sensormac]))

@app.route("/api/sensor/<sensormac>/history/week")
def history_week(sensormac):
    return jsonify(query_db("SELECT mac, DATE(timestamp), AVG(temperature), MIN(temperature), MAX(temperature), AVG(humidity), MIN(humidity), MAX(humidity), AVG(pressure), MIN(pressure), MAX(pressure) FROM reading WHERE mac=? AND DATE(timestamp) > DATE('now', '-7 days') GROUP BY DATE(timestamp)", [sensormac]))

@app.route("/api/sensor/name", methods=["POST"])
def save_name():
    mac = request.form["sensorMac"]
    sensor_name = request.form["sensorName"]
    
    db = get_db_mutable()
    db.cursor().execute("INSERT INTO sensor_metadata (mac, name) VALUES (?, ?) ON CONFLICT(mac) DO UPDATE SET name=?", [mac, sensor_name, sensor_name])
    db.commit()
    return redirect("/detail/" + mac)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")