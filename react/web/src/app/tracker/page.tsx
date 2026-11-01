"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { Badge, btnGhost, cardStyle, DataTable, inr, Note, PageHeader, Stat } from "@/components/ui";

type HistoryRow = {
  order_id: number;
  crop_name: string;
  farmer_name: string;
  buyer_name: string;
  buyer_type?: string;
  unit: string;
  quantity_ordered: number;
  order_value: number;
  order_date: string;
  status: string;
};

const STATUSES = ["all", "pending", "confirmed", "delivered", "paid", "cancelled"];

const ACTIONS: Record<string, Record<string, { label: string; next: string; danger?: boolean }[]>> = {
  farmer: {
    pending: [
      { label: "Confirm", next: "confirmed" },
      { label: "Decline", next: "cancelled", danger: true },
    ],
    confirmed: [
      { label: "Mark delivered", next: "delivered" },
      { label: "Cancel", next: "cancelled", danger: true },
    ],
    delivered: [{ label: "Mark paid", next: "paid" }],
  },
  buyer: {
    pending: [{ label: "Cancel", next: "cancelled", danger: true }],
    confirmed: [{ label: "Cancel", next: "cancelled", danger: true }],
  },
};

export default function TrackerPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryRow[]>([]);
  const [rawOrders, setRawOrders] = useState<any[]>([]);
  const [listings, setListings] = useState<any[]>([]);
  const [filter, setFilter] = useState("all");
  const [scope, setScope] = useState<"all" | "mine">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([api.getOrderHistory(), api.getOrders(), api.getListings()])
      .then(([h, o, l]) => {
        setHistory(Array.isArray(h) ? h : []);
        setRawOrders(Array.isArray(o) ? o : []);
        setListings(Array.isArray(l) ? l : []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (user) load();
  }, [user]);

  const listingById = useMemo(() => {
    const map: Record<number, any> = {};
    listings.forEach((l) => { map[l.listing_id] = l; });
    return map;
  }, [listings]);

  const rawById = useMemo(() => {
    const map: Record<number, any> = {};
    rawOrders.forEach((o) => { map[o.order_id] = o; });
    return map;
  }, [rawOrders]);

  const owns = (row: HistoryRow) => {
    if (!user || user.role === "guest") return false;
    const raw = rawById[row.order_id];
    if (!raw) return false;
    if (user.role === "farmer") {
      const listing = listingById[raw.listing_id];
      return Number(listing?.farmer_id) === Number(user.id);
    }
    return Number(raw.buyer_id) === Number(user.id);
  };

  const visible = history;
  const scoped = scope === "mine" ? visible.filter(owns) : visible;
  const filtered = filter === "all" ? scoped : scoped.filter((r) => r.status === filter);

  const counts = useMemo(() => {
    const c: Record<string, number> = {};
    scoped.forEach((r) => { c[r.status] = (c[r.status] || 0) + 1; });
    return c;
  }, [scoped]);

  if (!user) return <LandingPage />;

  const updateStatus = async (orderId: number, next: string) => {
    setBusy(orderId);
    setNotice("");
    setError("");
    try {
      await api.updateOrderStatus({ order_id: orderId, new_status: next, changed_by: user.name });
      setHistory((rows) => rows.map((r) => (r.order_id === orderId ? { ...r, status: next } : r)));
      setNotice(`Order #${orderId} updated to ${next}.`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(null);
    }
  };

  const columns = [
    { key: "order_id", label: "Order", render: (r: HistoryRow) => (
      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
        <strong>#{r.order_id}</strong>
        {owns(r) && <span style={{ fontSize: "0.68rem", fontWeight: 700, color: "var(--agri-green-deep)", background: "rgba(5,150,105,0.12)", padding: "0.1rem 0.4rem", borderRadius: "999px" }}>Mine</span>}
      </div>
    ) },
    { key: "crop_name", label: "Crop" },
    { key: "farmer_name", label: "Farmer" },
    { key: "buyer_name", label: "Buyer" },
    { key: "quantity_ordered", label: "Qty", align: "right" as const, render: (r: HistoryRow) => `${r.quantity_ordered} ${r.unit}` },
    { key: "order_value", label: "Value", align: "right" as const, render: (r: HistoryRow) => inr(r.order_value) },
    { key: "order_date", label: "Date" },
    { key: "status", label: "Status", render: (r: HistoryRow) => <Badge tone={r.status}>{r.status}</Badge> },
    {
      key: "actions",
      label: "",
      align: "right" as const,
      render: (r: HistoryRow) => {
        const actions = owns(r) ? ACTIONS[user.role]?.[r.status] ?? [] : [];
        if (!actions.length) return <span style={{ color: "var(--agri-light-muted)", fontSize: "0.8rem" }}>—</span>;
        return (
          <div style={{ display: "flex", gap: "0.35rem", justifyContent: "flex-end", flexWrap: "wrap" }}>
            {actions.map((a) => (
              <button
                key={a.next}
                onClick={() => updateStatus(r.order_id, a.next)}
                disabled={busy === r.order_id}
                style={{ ...btnGhost, padding: "0.32rem 0.65rem", fontSize: "0.78rem", borderColor: a.danger ? "rgba(239,68,68,0.4)" : undefined, color: a.danger ? "#B91C1C" : "var(--agri-green-deep)", opacity: busy === r.order_id ? 0.5 : 1 }}
              >
                {a.label}
              </button>
            ))}
          </div>
        );
      },
    },
  ];

  return (
    <div>
      <PageHeader title="Order Tracker" subtitle={user.role === "guest" ? "All orders across the marketplace (guest view)" : "All marketplace orders — you can manage the ones marked Mine"} />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.8rem", marginBottom: "1.2rem" }}>
        <Stat label="Total orders" value={scoped.length} icon="📦" />
        <Stat label="Pending" value={counts.pending || 0} icon="⏳" />
        <Stat label="Delivered" value={counts.delivered || 0} icon="🚚" />
        <Stat label="Paid" value={counts.paid || 0} icon="✅" />
      </div>

      <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginBottom: "1rem", alignItems: "center" }}>
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{ ...btnGhost, textTransform: "capitalize", background: filter === s ? "linear-gradient(135deg, var(--agri-green), var(--agri-lime))" : "rgba(255,255,255,0.7)", color: filter === s ? "#fff" : "var(--agri-green-deep)", borderColor: filter === s ? "transparent" : undefined }}
          >
            {s}
          </button>
        ))}
        {user.role !== "guest" && (
          <div style={{ display: "flex", gap: "0.4rem", marginLeft: "auto" }}>
            {(["all", "mine"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setScope(s)}
                style={{ ...btnGhost, background: scope === s ? "var(--agri-green-light)" : "rgba(255,255,255,0.7)", color: "var(--agri-green-deep)", borderColor: scope === s ? "var(--agri-green)" : undefined }}
              >
                {s === "all" ? "All orders" : "My orders"}
              </button>
            ))}
          </div>
        )}
      </div>

      {user.role === "guest" && (
        <div style={{ marginBottom: "1rem" }}>
          <Note>Guests can browse all orders. Sign in as a farmer or buyer to manage the ones that belong to you.</Note>
        </div>
      )}
      {notice && <div style={{ marginBottom: "1rem" }}><Note tone="success">{notice}</Note></div>}
      {error && <div style={{ marginBottom: "1rem" }}><Note tone="error">{error}</Note></div>}

      <div style={cardStyle}>
        {loading ? (
          <div style={{ color: "var(--agri-muted)", padding: "1rem" }}>Loading orders…</div>
        ) : (
          <DataTable columns={columns} rows={filtered} empty={scope === "mine" ? "No orders on your account yet." : "No orders in this filter."} />
        )}
      </div>
    </div>
  );
}
