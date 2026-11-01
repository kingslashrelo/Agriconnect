"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { Badge, btnGhost, btnPrimary, cardStyle, cropEmoji, DataTable, inr, inputStyle, Note, PageHeader, Stat } from "@/components/ui";

type Listing = {
  listing_id: number;
  crop_name: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  harvest_date?: string;
  farmer_name?: string;
  village?: string;
};

export default function MarketplacePage() {
  const { user } = useAuth();
  const [listings, setListings] = useState<Listing[]>([]);
  const [stats, setStats] = useState<any>({});
  const [query, setQuery] = useState("");
  const [view, setView] = useState<"cards" | "table">("cards");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    Promise.all([api.getActiveListings(), api.getMarketplaceStats()])
      .then(([l, s]) => {
        setListings(Array.isArray(l) ? l : []);
        setStats(s || {});
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [user]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return listings;
    return listings.filter((l) =>
      [l.crop_name, l.farmer_name, l.village].filter(Boolean).some((v) => String(v).toLowerCase().includes(q))
    );
  }, [listings, query]);

  if (!user) return <LandingPage />;

  const canOrder = user.role !== "farmer";

  const columns = [
    { key: "crop_name", label: "Crop", render: (r: Listing) => <span>{cropEmoji(r.crop_name)} {r.crop_name}</span> },
    { key: "farmer_name", label: "Farmer" },
    { key: "village", label: "Village" },
    { key: "quantity", label: "Qty", align: "right" as const, render: (r: Listing) => `${r.quantity} ${r.unit}` },
    { key: "price_per_unit", label: "Price / unit", align: "right" as const, render: (r: Listing) => inr(r.price_per_unit) },
    { key: "harvest_date", label: "Harvest", render: (r: Listing) => r.harvest_date || "—" },
    ...(canOrder
      ? [{
          key: "action",
          label: "",
          align: "right" as const,
          render: (r: Listing) => (
            <Link href={`/place-order?listing=${r.listing_id}`} style={{ ...btnGhost, textDecoration: "none", padding: "0.4rem 0.8rem" }}>
              Order
            </Link>
          ),
        }]
      : []),
  ];

  return (
    <div>
      <PageHeader
        title="Active Listings"
        subtitle="Fresh produce listed directly by farmers"
        right={
          <div style={{ display: "flex", gap: "0.4rem" }}>
            <button onClick={() => setView("cards")} style={{ ...btnGhost, background: view === "cards" ? "var(--agri-green-light)" : "rgba(255,255,255,0.7)" }}>Cards</button>
            <button onClick={() => setView("table")} style={{ ...btnGhost, background: view === "table" ? "var(--agri-green-light)" : "rgba(255,255,255,0.7)" }}>Table</button>
          </div>
        }
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.8rem", marginBottom: "1.2rem" }}>
        <Stat label="Active listings" value={listings.length} icon="📋" />
        <Stat label="Farmers" value={stats.farmers ?? "—"} icon="👨‍🌾" />
        <Stat label="Buyers" value={stats.buyers ?? "—"} icon="🛒" />
        <Stat label="Orders placed" value={stats.orders ?? "—"} icon="📦" />
      </div>

      <div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap", marginBottom: "1.2rem" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search crop, farmer or village…"
          style={{ ...inputStyle, flex: "1 1 260px", maxWidth: 420 }}
        />
        <span style={{ alignSelf: "center", color: "var(--agri-muted)", fontSize: "0.88rem" }}>{filtered.length} result{filtered.length === 1 ? "" : "s"}</span>
      </div>

      {error && <Note tone="error">{error}</Note>}
      {loading && <div style={{ color: "var(--agri-muted)", padding: "2rem 0" }}>Loading listings…</div>}

      {!loading && !error && view === "cards" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(260px, 100%), 1fr))", gap: "1rem" }}>
          {filtered.map((l) => (
            <div key={l.listing_id} style={{ ...cardStyle, display: "flex", flexDirection: "column", gap: "0.7rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.8rem" }}>
                <span style={{ fontSize: "1.9rem" }}>{cropEmoji(l.crop_name)}</span>
                <div>
                  <div style={{ fontFamily: "var(--agri-font-heading)", fontWeight: 700, fontSize: "1.08rem", color: "var(--agri-green-deep)" }}>{l.crop_name}</div>
                  <div style={{ fontSize: "0.82rem", color: "var(--agri-muted)" }}>{l.farmer_name}{l.village ? ` · ${l.village}` : ""}</div>
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--agri-green-dark)" }}>{inr(l.price_per_unit)}<span style={{ fontSize: "0.78rem", fontWeight: 500, color: "var(--agri-muted)" }}> / {l.unit}</span></div>
                <Badge tone="available">{l.quantity} {l.unit}</Badge>
              </div>
              <div style={{ fontSize: "0.82rem", color: "var(--agri-muted)" }}>Harvest: {l.harvest_date || "—"}</div>
              {canOrder && (
                <Link href={`/place-order?listing=${l.listing_id}`} style={{ ...btnPrimary, textAlign: "center", textDecoration: "none", marginTop: "auto" }}>
                  Order now
                </Link>
              )}
            </div>
          ))}
          {!filtered.length && <div style={{ color: "var(--agri-muted)", padding: "1rem" }}>No listings match your search.</div>}
        </div>
      )}

      {!loading && !error && view === "table" && (
        <div style={cardStyle}>
          <DataTable columns={columns} rows={filtered} empty="No listings match your search." />
        </div>
      )}
    </div>
  );
}
