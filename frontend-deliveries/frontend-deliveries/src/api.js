export async function createDelivery(data) {
  const res = await fetch("/deliveries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Error ${res.status}: ${errorText}`);
  }

  return await res.json();
}

export async function getDeliveryStatus(id) {
  const res = await fetch(`/deliveries/${id}`);

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Error ${res.status}: ${errorText}`);
  }

  return await res.json();
}