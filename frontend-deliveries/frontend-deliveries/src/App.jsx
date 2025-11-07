import { useState } from "react";
import { createDelivery, getDeliveryStatus } from "./api";

export default function App() {
  const [form, setForm] = useState({
    customer_name: "",
    address: "",
    item: "",
  });
  const [deliveryId, setDeliveryId] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const result = await createDelivery(form);
      if (result.id) {
        setDeliveryId(result.id);
        setStatus(result.status);
      } else {
        setError("Error al crear el pedido");
      }
    } catch (err) {
      console.error("Error al crear el pedido:", err);
      setError("No se pudo conectar al backend");
    }
  };

  const checkStatus = async () => {
    setError(null);
    try {
      const result = await getDeliveryStatus(deliveryId);
      if (result.status) {
        setStatus(result.status);
      } else {
        setError("Pedido no encontrado");
      }
    } catch (err) {
      console.error("Error al consultar estado:", err);
      setError("Error al consultar estado");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Pedidos a Domicilio</h1>
      <form onSubmit={handleSubmit}>
        <input
          placeholder="Nombre del cliente"
          value={form.customer_name}
          onChange={(e) =>
            setForm({ ...form, customer_name: e.target.value })
          }
        />
        <br />
        <input
          placeholder="Dirección"
          value={form.address}
          onChange={(e) => setForm({ ...form, address: e.target.value })}
        />
        <br />
        <input
          placeholder="Plato"
          value={form.item}
          onChange={(e) => setForm({ ...form, item: e.target.value })}
        />
        <br />
        <button type="submit">Enviar pedido</button>
      </form>

      {deliveryId && (
        <div style={{ marginTop: "1rem" }}>
          <p>Pedido creado con ID: {deliveryId}</p>
          <p>Estado actual: {status}</p>
          <button onClick={checkStatus}>Actualizar estado</button>
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}