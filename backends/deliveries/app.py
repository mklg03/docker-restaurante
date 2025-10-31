from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Variables de entorno para la conexión (coinciden con docker-compose.yml)
DB_HOST = os.getenv("DB_HOST", "db")
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
    # Crear tabla solo si no existe, con la columna correcta 'costumer'
    cur.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id SERIAL PRIMARY KEY,
            customer TEXT NOT NULL,
            address TEXT NOT NULL,
            item TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route("/deliveries", methods=["POST"])
def create_delivery():
    data = request.json
    customer = data.get("customer_name")  # El JSON puede seguir usando 'customer_name'
    address = data.get("address")
    item = data.get("item")

    if not customer or not address or not item:
        return jsonify({"error": "customer_name, address and item are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    # Insertar en la columna real 'costumer'
    cur.execute(
        "INSERT INTO deliveries (customer, address, item, status) VALUES (%s, %s, %s, %s) RETURNING id",
        (customer, address, item, "pending")
    )
    delivery_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": delivery_id,
        "customer": customer,
        "address": address,
        "item": item,
        "status": "pending"
    }), 201

@app.route("/deliveries", methods=["GET"])
def list_deliveries():
    conn = get_connection()
    cur = conn.cursor()
    # Seleccionar la columna correcta
    cur.execute("SELECT id, customer, address, item, status FROM deliveries")
    deliveries = [
        {"id": r[0], "customer": r[1], "address": r[2], "item": r[3], "status": r[4]}
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return jsonify(deliveries)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)
