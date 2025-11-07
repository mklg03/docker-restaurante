import os
import sys
import requests
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPExceptionError
from datetime import datetime

# Variables de entorno
BASE_URL = os.getenv("ORDERS_URL", "http://localhost:5000")
LDAP_HOST = os.getenv("LDAP_HOST", "ldap://localhost")
LDAP_BASE = os.getenv("LDAP_BASE", "dc=restaurante,dc=local")

def ldap_login(username, password):
    dn = f"uid={username},ou=People,{LDAP_BASE}"
    server = Server(LDAP_HOST, get_info=ALL)
    try:
        conn = Connection(server, user=dn, password=password, auto_bind=True)
        print(f"Login exitoso: {username}")
        return True
    except LDAPExceptionError as e:
        print("Credenciales inválidas o error de LDAP:", e)
        return False

def list_orders():
    try:
        r = requests.get(f"{BASE_URL}/orders", timeout=5)
        if r.status_code == 200:
            orders = r.json()
            if not orders:
                print("No hay órdenes registradas.")
                return
            print("\nÓrdenes:")
            for o in orders:
                print(f"ID: {o['id']} | Plato: {o['item']} | Estado: {o['status']}")
        else:
            print("Error al obtener órdenes:", r.status_code, r.text)
    except Exception as e:
        print("Error de conexión:", e)

def filter_by_status():
    status = input("Estado a filtrar (pending/ready/sent/delivered): ").strip()
    try:
        r = requests.get(f"{BASE_URL}/orders", timeout=5)
        if r.status_code == 200:
            filtered = [o for o in r.json() if o.get("status") == status]
            if not filtered:
                print("No hay órdenes con ese estado.")
                return
            for o in filtered:
                print(f"ID: {o['id']} | Plato: {o['item']} | Estado: {o['status']}")
        else:
            print("Error al obtener órdenes:", r.status_code, r.text)
    except Exception as e:
        print("Error de conexión:", e)

def menu():
    while True:
        print("\n=== CLI Administración ===")
        print("1) Ver todas las órdenes")
        print("2) Filtrar por estado")
        print("3) Salir")
        op = input("> ").strip()
        if op == "1":
            list_orders()
        elif op == "2":
            filter_by_status()
        elif op == "3":
            print("Saliendo...")
            sys.exit(0)
        else:
            print("Opción inválida")

if __name__ == "__main__":
    print("=== Login LDAP (Gerente) ===")
    user = input("Usuario: ").strip()
    pwd = input("Password: ").strip()
    if ldap_login(user, pwd):
        menu()
    else:
        print("Acceso denegado.")
        sys.exit(1)