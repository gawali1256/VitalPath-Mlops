export async function assessHealth(payload) {
  const response = await fetch("/api/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || "Assessment failed. Is the API running?");
  }
  return response.json();
}

export async function fetchModelInfo() {
  const response = await fetch("/api/model");
  if (!response.ok) {
    return null;
  }
  return response.json();
}
