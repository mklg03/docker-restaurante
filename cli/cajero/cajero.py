import os
import sys
import requests
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPExceptionError

# URLs y variables LDAP
BASE_URL = os.getenv("ORDERS_URL", "http://api_gateway")
LDAP_HOST = f"ldap://{os.getenv('LDAP_HOST', 'localhost')}:{os.getenv('LDAP_PORT', 389)}"
LDAP_BASE = os.getenv("LDAP_BASE", "dc=restaurante,dc=local")

def ldap_login(username, password):
    """
    Autenticación simple contra LDAP.
    Devuelve True si login exitoso, False si falla.
    """
    dn = f"uid={username},ou=People,{LDAP_BASE}"
    server = Server(LDAP_HOST, get_info=ALL)
    try:
        conn = Connection(server, user=dn, password=password, auto_bind=True)
        print(f"[✔] Login exitoso: {username}")
        return True
    except LDAPExceptionError as e:
        print("[✖] Credenciales inválidas o error de LDAP:", e)
        return False

def create_order():
    """
    Permite al cajero crear un nuevo pedido
    """
    item = input("Nombre del producto: ").strip()
    quantity = input("Cantidad: ").strip()
    notes = input("Notas adicionales (opcional): ").strip()

    if not item or not quantity.isdigit():
        print("Producto o cantidad inválida")
        return

    payload = {
        "item": item,
        "quantity": int(quantity),
        "notes": notes,
        "status": "pending"  # Todos los pedidos nuevos inician como pending
    }

    try:
        r = requests.post(f"{BASE_URL}/orders", json=payload, timeout=5)
    except requests.RequestException as e:
        print("Error de conexión al backend:", e)
        return

    if r.status_code == 201:
        print(f"Pedido creado correctamente: {r.json().get('id')}")
    else:
        print("Error al crear pedido:", r.status_code, r.text)

def list_orders():
    """
    Permite al cajero ver los pedidos que ha enviado
    """
    try:
        r = requests.get(f"{BASE_URL}/orders", timeout=5)
    except requests.RequestException as e:
        print("Error de conexión al backend:", e)
        return

    if r.status_code == 200:
        orders = r.json()
        if not orders:
            print("No hay pedidos.")
            return
        print("\nPedidos enviados:")
        for o in orders:
            print(f"ID: {o.get('id')} | Item: {o.get('item')} | Cantidad: {o.get('quantity')} | Estado: {o.get('status')}")
    else:
        print("Error al obtener pedidos:", r.status_code, r.text)

def menu():
    """
    Menú principal de la CLI de cajero
    """
    while True:
        print("\n=== CLI de Cajero ===")
        print("1) Crear nuevo pedido")
        print("2) Listar pedidos enviados")
        print("3) Salir")
        choice = input("> ").strip()
        if choice == "1":
            create_order()
        elif choice == "2":
            list_orders()
        elif choice == "3":
            sys.exit(0)
        else:
            print("Opción inválida")

if __name__ == "__main__":
    print("=== Login LDAP (Cajero) ===")
    user = input("Usuario: ").strip()
    pwd = input("Password: ").strip()

    if ldap_login(user, pwd):
        menu()
    else:
        print("Acceso denegado.")
        sys.exit(1)
