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

def list_orders():
    """
    Obtiene y muestra todas las órdenes del backend de orders
    """
    try:
        r = requests.get(f"{BASE_URL}/orders", timeout=5)
    except requests.RequestException as e:
        print("Error de conexión al backend:", e)
        return
    if r.status_code == 200:
        orders = r.json()
        if not orders:
            print("No hay órdenes.")
            return
        print("\nÓrdenes:")
        for o in orders:
            print(f"ID: {o.get('id')} | Item: {o.get('item')} | Estado: {o.get('status')}")
    else:
        print("Error al obtener órdenes:", r.status_code, r.text)

def update_order():
    """
    Actualiza el estado de una orden por ID
    """
    order_id = input("ID de la orden a actualizar: ").strip()
    if not order_id.isdigit():
        print("ID inválido")
        return
    new_status = input("Nuevo estado (pending/ready/sent/delivered): ").strip()
    if not new_status:
        print("Se requiere estado")
        return
    payload = {"status": new_status}
    try:
        r = requests.put(f"{BASE_URL}/orders/{order_id}", json=payload, timeout=5)
    except requests.RequestException as e:
        print("Error de conexión al backend:", e)
        return
    if r.status_code == 200:
        print("Estado actualizado correctamente.")
    elif r.status_code == 404:
        print("Orden no encontrada.")
    else:
        print("Error actualizando:", r.status_code, r.text)

def menu():
    """
    Menú principal de la CLI de cocina
    """
    while True:
        print("\n=== CLI de Cocina ===")
        print("1) Listar órdenes")
        print("2) Actualizar orden")
        print("3) Salir")
        choice = input("> ").strip()
        if choice == "1":
            list_orders()
        elif choice == "2":
            update_order()
        elif choice == "3":
            sys.exit(0)
        else:
            print("Opción inválida")

if __name__ == "__main__":
    print("=== Login LDAP (Cocina) ===")
    user = input("Usuario: ").strip()
    pwd = input("Password: ").strip()

    if ldap_login(user, pwd):
        menu()
    else:
        print("Acceso denegado.")
        sys.exit(1)
