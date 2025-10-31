
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "./db/orders.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    item = data.get("item")
    if not item:
        return jsonify({"error": "Item is required"}), 400
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO orders (item, status) VALUES (?, ?)", (item, "pending"))
    conn.commit()
    order_id = c.lastrowid
    conn.close()
    return jsonify({"id": order_id, "item": item, "status": "pending"}), 201

@app.route("/orders", methods=["GET"])
def list_orders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, item, status FROM orders")
    orders = [{"id": row[0], "item": row[1], "status": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(orders)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)