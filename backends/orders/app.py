from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Variables de entorno para la conexión
DB_HOST = os.getenv("DB_HOST", "db")        # nombre del servicio DB en docker-compose
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "restaurante")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            item TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    item = data.get("item")
    if not item:
        return jsonify({"error": "Item is required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (item, status) VALUES (%s, %s) RETURNING id",
        (item, "pending")
    )
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": order_id, "item": item, "status": "pending"}), 201

@app.route("/orders", methods=["GET"])
def list_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, item, status FROM orders")
    orders = [{"id": row[0], "item": row[1], "status": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(orders)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
