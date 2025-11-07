import os
import sys
import requests
from ldap3 import Server, Connection, ALL

BASE_URL = os.getenv("ORDERS_URL", "http://api_gateway")
LDAP_HOST = f"ldap://{os.getenv('LDAP_HOST', 'localhost')}:{os.getenv('LDAP_PORT', 389)}"
LDAP_BASE = os.getenv("LDAP_BASE", "dc=restaurante,dc=local")
LDAP_ADMIN_PASSWORD = os.getenv("LDAP_ADMIN_PASSWORD", "adminldap")
REQUIRED_ROLE = None  # Se llenará tras login


def get_role_from_ldap(uid, password):
    """
    Autentica al usuario y obtiene su grupo (rol) desde LDAP.
    """
    server = Server(LDAP_HOST, get_info=ALL)
    user_dn = f"uid={uid},ou=People,{LDAP_BASE}"


    try:
        Connection(server, user=user_dn, password=password, auto_bind=True)
    except:
        print("Usuario o contraseña incorrectos")
        return None

    admin_dn = f"cn=admin,{LDAP_BASE}"
    try:
        conn = Connection(server, user=admin_dn, password=LDAP_ADMIN_PASSWORD, auto_bind=True)
        conn.search(
            search_base=f"ou=Groups,{LDAP_BASE}",
            search_filter=f"(memberUid={uid})",
            attributes=["cn"]
        )
        if conn.entries:
            group_cn = conn.entries[0]["cn"].value
            return group_cn  # ej. "cajeros"
        else:
            print("⚠ Usuario no pertenece a ningún grupo LDAP")
            return None
    except Exception as e:
        print(" Error buscando grupos:", e)
        return None



def create_order():
    item = input("Producto: ").strip()
    qty = input("Cantidad: ").strip()
    notes = input("Notas: ").strip()
    if not item or not qty.isdigit():
        print("Datos inválidos")
        return
    payload = {"item": item, "quantity": int(qty), "notes": notes, "status": "pending"}
    try:
        r = requests.post(f"{BASE_URL}/orders", json=payload, timeout=5)
        print("✅ Pedido creado" if r.status_code == 201 else f"Error: {r.text}")
    except requests.RequestException as e:
        print("Error de conexión:", e)


def update_order():
    oid = input("ID: ").strip()
    status = input("Nuevo estado (pending/ready/sent/delivered): ").strip()
    if not oid.isdigit() or not status:
        print("Datos inválidos")
        return
    try:
        r = requests.put(f"{BASE_URL}/orders/{oid}", json={"status": status}, timeout=5)
        print("Actualizado" if r.status_code == 200 else f"Error: {r.text}")
    except requests.RequestException as e:
        print("Error de conexión:", e)


def list_orders(role):
    try:
        r = requests.get(f"{BASE_URL}/orders", timeout=5)
        orders = r.json()
        if not orders:
            print("No hay órdenes.")
            return
        for o in orders:
            oid = o.get('id','N/A')
            item = o.get('item','N/A')
            qty = o.get('quantity','N/A')
            status = o.get('status','N/A')
            print(f"ID:{oid} | {item} x{qty} | {status}") if role == "cajero" else print(f"ID:{oid} | {item} | {status}")
    except requests.RequestException as e:
        print("Error de conexión:", e)


def filter_by_status():
    status = input("Estado: ").strip()
    try:
        r = requests.get(f"{BASE_URL}/orders", timeout=5)
        for o in r.json():
            if o.get("status") == status:
                print(f"ID:{o['id']} | {o['item']} | {o['status']}")
    except requests.RequestException as e:
        print("Error de conexión:", e)


# --- Menús ---
def menu_caja():
    while True:
        print("\n=== CLI Cajero ===")
        print("1) Crear pedido")
        print("2) Ver pedidos")
        print("3) Salir")
        op = input("> ").strip()
        if op == "1": create_order()
        elif op == "2": list_orders("cajero")
        elif op == "3": sys.exit(0)

def menu_admin():
    while True:
        print("\n=== CLI Gerente ===")
        print("1) Ver todas las órdenes")
        print("2) Filtrar órdenes por estado")
        print("3) Salir")
        op = input("> ").strip()
        if op == "1":
            list_orders("gerente")
        elif op == "2":
            filter_by_status()
        elif op == "3":
            print("Saliendo...")
            sys.exit(0)
        else:
            print("Opción inválida")


def menu_cocina():
    while True:
        print("\n=== CLI Cocina ===")
        print("1) Listar órdenes")
        print("2) Actualizar orden")
        print("3) Salir")
        op = input("> ").strip()
        if op == "1": list_orders("cocina")
        elif op == "2": update_order()
        elif op == "3": sys.exit(0)


def menu_admin():
    while True:
        print("\n=== CLI Gerente ===")
        print("1) Ver órdenes")
        print("2) Filtrar por estado")
        print("3) Salir")
        op = input("> ").strip()
        if op == "1": list_orders("gerente")
        elif op == "2": filter_by_status()
        elif op == "3": sys.exit(0)

MENU_MAP = {
    "cajero": menu_caja,
    "cocinero": menu_cocina, 
    "cocina": menu_cocina,
    "gerente": menu_admin,
}




if __name__ == "__main__":
    user = input("Usuario: ").strip()
    pwd = input("Password: ").strip()

    role = get_role_from_ldap(user, pwd)
    if role:
        REQUIRED_ROLE = role
        print(f"[✔] Login exitoso: {user} — Rol: {REQUIRED_ROLE}")
        run_menu = MENU_MAP.get(REQUIRED_ROLE)
        if run_menu:
            run_menu()
        else:
            print("Rol no reconocido")
            sys.exit(1)
    else:
        print("Acceso denegado")
        sys.exit(1)
