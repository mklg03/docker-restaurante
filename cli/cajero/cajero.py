import requests

BASE_URL = "http://localhost:5000"

def create_order():
    item = input("Ingresa el nombre del plato: ")
    data = {"item": item}

    try:
        r = requests.post(f"{BASE_URL}/orders", json=data)
        print("Respuesta:", r.json())
    except Exception as e:
        print("Error conectando al servidor:", e)

def list_orders():
    try:
        r = requests.get(f"{BASE_URL}/orders")
        print("Órdenes:")
        for o in r.json():
            print(f"ID: {o['id']} | Plato: {o['item']} | Estado: {o['status']}")
    except Exception as e:
        print("Error conectando al servidor:", e)

def update_order():
    try:
        oid = input("ID de la orden: ")
        status = input("Nuevo estado (pending/preparing/delivered): ")

        r = requests.put(f"{BASE_URL}/orders/{oid}", json={"status": status})
        print("Respuesta:", r.json())
    except Exception as e:
        print("Error conectando al servidor:", e)

def menu():
    while True:
        print("\n=== CLI Restaurante ===")
        print("1) Crear orden")
        print("2) Listar órdenes")
        print("3) Actualizar orden")
        print("4) Salir")
        op = input("> ")

        if op == "1":
            create_order()
        elif op == "2":
            list_orders()
        elif op == "3":
            update_order()
        elif op == "4":
            print(" Saliendo...")
            break
        else:
            print(" Opción inválida")

if __name__ == "__main__":
    menu()

