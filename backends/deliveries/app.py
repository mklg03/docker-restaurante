from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "./db/deliveries.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            address TEXT NOT NULL,
            item TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/deliveries", methods=["POST"])
def create_delivery():
    data = request.json
    customer = data.get("customer_name")
    address = data.get("address")
    item = data.get("item")

    if not customer or not address or not item:
        return jsonify({"error": "customer_name, address and item are required"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO deliveries (customer_name, address, item, status) VALUES (?, ?, ?, ?)",
        (customer, address, item, "pending")
    )
    conn.commit()
    delivery_id = c.lastrowid
    conn.close()

    return jsonify({"id": delivery_id, "customer": customer, "address": address, "item": item, "status": "pending"}), 201

@app.route("/deliveries", methods=["GET"])
def list_deliveries():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, customer_name, address, item, status FROM deliveries")
    deliveries = [
        {"id": r[0], "customer": r[1], "address": r[2], "item": r[3], "status": r[4]}
        for r in c.fetchall()
    ]
    conn.close()
    return jsonify(deliveries)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)