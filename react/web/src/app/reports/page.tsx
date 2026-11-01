"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { Badge, cardStyle, DataTable, inr, Note, PageHeader, Stat } from "@/components/ui";

export default function ReportsPage() {
  const { user } = useAuth();
  const [monthly, setMonthly] = useState<any[]>([]);
  const [buyers, setBuyers] = useState<any[]>([]);
  const [ratings, setRatings] = useState<any[]>([]);
  const [inventory, setInventory] = useState<any[]>([]);
  const [lowStock, setLowStock] = useState<any[]>([]);
  const [revenue, setRevenue] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    const tasks: Promise<any>[] = [
      api.getMonthlySales(),
      api.getMostActiveBuyers(),
      api.getFarmerRatings(),
      api.getInventory(),
      api.getLowStock(),
    ];
    if (user.role === "farmer" && user.id) tasks.push(api.getFarmerRevenue(user.id));

    Promise.allSettled(tasks)
      .then((results) => {
        const val = (i: number) => (results[i]?.status === "fulfilled" ? (results[i] as PromiseFulfilledResult<any>).value : []);
        setMonthly(Array.isArray(val(0)) ? val(0) : []);
        setBuyers(Array.isArray(val(1)) ? val(1) : []);
        setRatings(Array.isArray(val(2)) ? val(2) : []);
        setInventory(Array.isArray(val(3)) ? val(3) : []);
        setLowStock(Array.isArray(val(4)) ? val(4) : []);
        if (results[5]?.status === "fulfilled") {
          const r = (results[5] as PromiseFulfilledResult<any>).value;
          setRevenue(Array.isArray(r) ? r[0] : r);
        }
        if (results.every((r) => r.status === "rejected")) setError("Could not load report data.");
      })
      .finally(() => setLoading(false));
  }, [user]);

  const totals = useMemo(() => {
    const orders = monthly.reduce((s, m) => s + Number(m.total_orders || 0), 0);
    const value = monthly.reduce((s, m) => s + Number(m.sales_value || 0), 0);
    const topBuyer = [...buyers].sort((a, b) => Number(b.total_orders || 0) - Number(a.total_orders || 0))[0];
    const avgRating = ratings.length ? ratings.reduce((s, r) => s + Number(r.avg_rating || 0), 0) / ratings.length : 0;
    return { orders, value, topBuyer, avgRating };
  }, [monthly, buyers, ratings]);

  const maxSales = Math.max(1, ...monthly.map((m) => Number(m.sales_value || 0)));

  if (!user) return <LandingPage />;

  return (
    <div>
      <PageHeader title="Reports" subtitle="Marketplace performance at a glance" />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.8rem", marginBottom: "1.2rem" }}>
        <Stat label="Total sales" value={inr(totals.value)} icon="💰" />
        <Stat label="Orders tracked" value={totals.orders} icon="📦" />
        <Stat label="Top buyer" value={totals.topBuyer?.name ?? "—"} icon="🛒" />
        <Stat label="Avg farmer rating" value={totals.avgRating ? `${totals.avgRating.toFixed(1)} ★` : "—"} icon="⭐" />
        {revenue && <Stat label="Your revenue" value={inr(revenue.total_revenue)} icon="🌾" />}
      </div>

      {error && <div style={{ marginBottom: "1rem" }}><Note tone="error">{error}</Note></div>}
      {loading && <div style={{ color: "var(--agri-muted)", padding: "1rem 0 2rem" }}>Loading reports…</div>}

      {!loading && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(320px, 100%), 1fr))", gap: "1rem" }}>
          <div style={cardStyle}>
            <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.1rem", margin: "0 0 0.8rem", color: "var(--agri-green-deep)" }}>Monthly sales</h2>
            <DataTable
              columns={[
                { key: "month", label: "Month" },
                { key: "total_orders", label: "Orders", align: "right" as const },
                { key: "total_quantity", label: "Quantity", align: "right" as const, render: (r: any) => Number(r.total_quantity).toFixed(1) },
                { key: "sales_value", label: "Value", align: "right" as const, render: (r: any) => inr(r.sales_value) },
              ]}
              rows={monthly}
              empty="No sales recorded yet."
            />
            {monthly.length > 0 && (
              <div style={{ display: "grid", gap: "0.45rem", marginTop: "1rem" }}>
                {monthly.slice(0, 6).map((m) => (
                  <div key={m.month} style={{ display: "grid", gridTemplateColumns: "70px 1fr 80px", alignItems: "center", gap: "0.6rem", fontSize: "0.78rem", color: "var(--agri-muted)" }}>
                    <span>{m.month}</span>
                    <div style={{ height: 8, borderRadius: 999, background: "rgba(5,150,105,0.1)", overflow: "hidden" }}>
                      <div style={{ width: `${Math.max(4, (Number(m.sales_value) / maxSales) * 100)}%`, height: "100%", borderRadius: 999, background: "linear-gradient(90deg, var(--agri-green), var(--agri-lime))" }} />
                    </div>
                    <span style={{ textAlign: "right" }}>{inr(m.sales_value)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={cardStyle}>
            <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.1rem", margin: "0 0 0.8rem", color: "var(--agri-green-deep)" }}>Most active buyers</h2>
            <DataTable
              columns={[
                { key: "name", label: "Buyer" },
                { key: "total_orders", label: "Orders", align: "right" as const },
                { key: "total_volume", label: "Volume", align: "right" as const, render: (r: any) => Number(r.total_volume).toFixed(1) },
              ]}
              rows={buyers}
              empty="No buyer activity yet."
            />
          </div>

          <div style={cardStyle}>
            <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.1rem", margin: "0 0 0.8rem", color: "var(--agri-green-deep)" }}>Farmer ratings</h2>
            <DataTable
              columns={[
                { key: "name", label: "Farmer" },
                { key: "avg_rating", label: "Rating", align: "right" as const, render: (r: any) => `${Number(r.avg_rating).toFixed(1)} ★` },
                { key: "num_ratings", label: "Ratings", align: "right" as const },
              ]}
              rows={ratings}
              empty="No ratings yet."
            />
          </div>

          <div style={{ ...cardStyle, gridColumn: "1 / -1", height: 400, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.1rem", margin: "0 0 0.8rem", color: "var(--agri-green-deep)", textAlign: "center" }}>Inventory</h2>
            <div style={{ flex: 1, minHeight: 0 }}>
              <DataTable
                columns={[
                  { key: "crop_name", label: "Crop" },
                  { key: "farmer_name", label: "Farmer" },
                  { key: "quantity", label: "Qty", align: "right" as const, render: (r: any) => `${r.quantity} ${r.unit}` },
                  { key: "price_per_unit", label: "Price", align: "right" as const, render: (r: any) => inr(r.price_per_unit) },
                  { key: "status", label: "Status", render: (r: any) => <Badge tone={r.status}>{r.status}</Badge> },
                ]}
                rows={inventory}
                empty="No inventory rows."
                maxHeight={300}
              />
            </div>
          </div>

          <div style={{ ...cardStyle, gridColumn: "1 / -1" }}>
            <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.1rem", margin: "0 0 0.8rem", color: "var(--agri-green-deep)" }}>Low stock alerts</h2>
            <DataTable
              columns={[
                { key: "crop_name", label: "Crop" },
                { key: "farmer_name", label: "Farmer" },
                { key: "quantity", label: "Remaining", align: "right" as const, render: (r: any) => `${r.quantity} ${r.unit}` },
                { key: "status", label: "Status", render: (r: any) => <Badge tone={r.status}>{r.status}</Badge> },
              ]}
              rows={lowStock}
              empty="No low-stock items — inventory looks healthy."
            />
          </div>
        </div>
      )}
    </div>
  );
}
