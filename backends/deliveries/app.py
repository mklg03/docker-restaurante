from flask import Flask, request, jsonify
import psycopg2
import os
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Variables de entorno
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "restaurante")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
ORDERS_URL = os.getenv("ORDERS_URL", "http://orders_service:5000/orders")

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
    logging.info("Tabla deliveries verificada o creada.")

@app.route("/deliveries", methods=["POST"])
def create_delivery():
    data = request.json
    customer = data.get("customer_name")
    address = data.get("address")
    item = data.get("item")

    if not customer or not address or not item:
        logging.warning("Datos incompletos en POST /deliveries")
        return jsonify({"error": "customer_name, address and item are required"}), 400

    # Guardar en tabla local
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deliveries (customer, address, item, status) VALUES (%s, %s, %s, %s) RETURNING id",
        (customer, address, item, "pending")
    )
    delivery_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Nuevo pedido creado: {delivery_id}")

    # Reenviar al backend de órdenes
    try:
        response = requests.post(
            ORDERS_URL,
            json={"item": item},
            timeout=5
        )
        response.raise_for_status()
        logging.info(f"Pedido reenviado a órdenes: {response.status_code}")
    except Exception as e:
        logging.error(f"Error al reenviar pedido a órdenes: {e}")
        return jsonify({
            "id": delivery_id,
            "customer": customer,
            "address": address,
            "item": item,
            "status": "pending",
            "warning": "Pedido recibido pero no se pudo reenviar a cocina"
        }), 202

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
    cur.execute("SELECT id, customer, address, item, status FROM deliveries")
    deliveries = [
        {"id": r[0], "customer": r[1], "address": r[2], "item": r[3], "status": r[4]}
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    logging.info(f"{len(deliveries)} pedidos listados.")
    return jsonify(deliveries)

@app.route("/deliveries/<int:delivery_id>", methods=["GET"])
def get_delivery_status(delivery_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, customer, address, item, status FROM deliveries WHERE id = %s",
        (delivery_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        logging.info(f"Estado consultado para pedido {delivery_id}")
        return jsonify({
            "id": row[0],
            "customer": row[1],
            "address": row[2],
            "item": row[3],
            "status": row[4]
        }), 200
    else:
        logging.warning(f"Pedido {delivery_id} no encontrado")
        return jsonify({"error": "Pedido no encontrado"}), 404

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)