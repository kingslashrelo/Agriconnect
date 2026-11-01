const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

async function fetchJSON(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  health: () => fetchJSON("/health"),
  login: (aadhaar: string, role?: string) => fetchJSON("/api/auth/login", { method: "POST", body: JSON.stringify({ aadhaar, role }) }),
  register: (data: any) => fetchJSON("/api/auth/register", { method: "POST", body: JSON.stringify(data) }),
  getFarmers: () => fetchJSON("/api/farmers/"),
  getBuyers: () => fetchJSON("/api/buyers/"),
  getListings: () => fetchJSON("/api/listings/"),
  getActiveListings: () => fetchJSON("/api/listings/active"),
  createListing: (data: any) => fetchJSON("/api/listings/", { method: "POST", body: JSON.stringify(data) }),
  getFarmerListings: (id: number) => fetchJSON(`/api/listings/farmer/${id}`),
  getOrders: () => fetchJSON("/api/orders/"),
  getOrderHistory: () => fetchJSON("/api/orders/history"),
  createOrder: (data: any) => fetchJSON("/api/orders/", { method: "POST", body: JSON.stringify(data) }),
  updateOrderStatus: (data: any) => fetchJSON("/api/orders/status", { method: "POST", body: JSON.stringify(data) }),
  getOrderAudit: () => fetchJSON("/api/orders/audit"),
  getMostActiveBuyers: () => fetchJSON("/api/reports/most-active-buyers"),
  getFarmerRatings: () => fetchJSON("/api/reports/farmer-ratings"),
  getInventory: () => fetchJSON("/api/reports/inventory"),
  getLowStock: () => fetchJSON("/api/reports/low-stock"),
  getMonthlySales: () => fetchJSON("/api/reports/monthly-sales"),
  getFarmerRevenue: (id: number) => fetchJSON(`/api/reports/farmer-revenue/${id}`),
  recommendCrops: (data: any) => fetchJSON("/api/crop-advisor/recommend", { method: "POST", body: JSON.stringify(data) }),
  getCrops: () => fetchJSON("/api/crop-advisor/crops"),
  getSchemes: () => fetchJSON("/api/schemes/"),
  getFarmerSchemes: (id: number) => fetchJSON(`/api/schemes/farmer/${id}`),
  getWeather: (lat: number, lon: number) => fetchJSON(`/api/weather/forecast?lat=${lat}&lon=${lon}`),
  geocode: (q: string) => fetchJSON(`/api/geocode/search?q=${encodeURIComponent(q)}`),
  reverseGeocode: (lat: number, lon: number) => fetchJSON(`/api/geocode/reverse?lat=${lat}&lon=${lon}`),
  getMarketplaceStats: () => fetchJSON("/api/marketplace/stats"),
};
