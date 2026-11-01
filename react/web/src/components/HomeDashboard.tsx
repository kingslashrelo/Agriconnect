"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { cardStyle } from "@/components/ui";

const TEAM = [
  { name: "Joseph Boby", initials: "JB" },
  { name: "Kuriakose Sebastian", initials: "KS" },
  { name: "Sujith S", initials: "SS" },
  { name: "Niranjana S Kummar", initials: "NK" },
];

const FEATURES = [
  { icon: "📋", title: "Marketplace", desc: "Farmers list produce with quantity, unit, price and harvest date. Buyers browse, search and filter the live inventory." },
  { icon: "📦", title: "Order lifecycle", desc: "Orders move through pending, confirmed, delivered and paid states, with buyers able to cancel before dispatch." },
  { icon: "📊", title: "Reports & analytics", desc: "Monthly sales, most active buyers, farmer ratings, inventory levels and low-stock alerts generated from database views." },
  { icon: "🌱", title: "Crop advisor", desc: "Recommendations ranked by soil, season and water conditions, with expected revenue and market outlook." },
  { icon: "🧮", title: "Profit calculator", desc: "Estimate input costs, transport and margin before a crop is sown or a lot is sold." },
  { icon: "🏛️", title: "Scheme explorer", desc: "Each farmer sees the government schemes and subsidies linked to their own account and eligibility." },
];

const STACK = ["Next.js", "React", "FastAPI", "PostgreSQL", "Supabase", "Python"];

export function HomeDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    api.getMarketplaceStats().then(setStats).catch(() => {});
  }, []);

  const statCards = [
    { label: "Farmers", val: stats.farmers },
    { label: "Buyers", val: stats.buyers },
    { label: "Listings", val: stats.listings },
    { label: "Orders", val: stats.orders },
  ];

  return (
    <div>
      <div style={{ padding: "clamp(1.5rem, 4vw, 2.6rem) clamp(1.25rem, 4vw, 2.4rem)", borderRadius: "24px", border: "1px solid var(--agri-border)", background: "radial-gradient(120% 160% at 0% 0%, #ECFDF5 0%, #FFFFFF 62%)", boxShadow: "0 2px 10px rgba(15, 23, 42, 0.06)", marginBottom: "2rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.7rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          <span style={{ display: "inline-block", padding: "0.28rem 0.75rem", borderRadius: "999px", background: "rgba(5, 150, 105, 0.12)", color: "var(--agri-green-deep)", fontWeight: 700, fontSize: "0.72rem", letterSpacing: "0.12em", textTransform: "uppercase" }}>DBMS Course Project</span>
          {user && <span style={{ fontSize: "0.82rem", color: "var(--agri-muted)" }}>Browsing as <strong style={{ color: "var(--agri-green-deep)" }}>{user.name}</strong></span>}
        </div>
        <h1 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "clamp(2rem, 8vw, 2.6rem)", fontWeight: 700, color: "var(--agri-green-deep)", margin: 0, lineHeight: 1.1 }}>AgriConnect</h1>
        <p style={{ color: "var(--agri-text)", margin: "0.9rem 0 0", fontSize: "1.05rem", maxWidth: 760, lineHeight: 1.65 }}>
          A farm-to-market marketplace that connects farmers directly with buyers — no middlemen. Farmers publish
          produce, buyers place and track orders, and both sides get live reports on sales, stock and earnings.
        </p>
        <p style={{ color: "var(--agri-muted)", margin: "0.6rem 0 0", fontSize: "0.95rem", maxWidth: 760, lineHeight: 1.6 }}>
          Built on a normalized PostgreSQL schema with views and stored procedures, served by a FastAPI backend and a
          Next.js interface. Use the dock at the bottom to move between the marketplace and the analysis tools.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem", marginBottom: "2.2rem" }}>
        {statCards.map((s) => (
          <div key={s.label} style={{ ...cardStyle, padding: "1.2rem", textAlign: "center" }}>
            <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--agri-green-deep)", lineHeight: 1.1 }}>{s.val ?? "—"}</div>
            <div style={{ color: "var(--agri-muted)", fontSize: "0.86rem", marginTop: "0.2rem" }}>{s.label}</div>
          </div>
        ))}
      </div>

      <section style={{ marginBottom: "2.2rem" }}>
        <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.5rem", fontWeight: 700, color: "var(--agri-green-deep)", margin: "0 0 0.3rem" }}>About the project</h2>
        <p style={{ color: "var(--agri-muted)", margin: "0 0 1.2rem", fontSize: "0.95rem", maxWidth: 760, lineHeight: 1.6 }}>
          AgriConnect digitises the local produce supply chain. The database stores farmers, buyers, listings, orders,
          payments, ratings, schemes and market prices, and exposes them through reports and role-aware screens.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem" }}>
          {FEATURES.map((f) => (
            <div key={f.title} style={{ ...cardStyle, display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              <div style={{ fontSize: "1.5rem" }}>{f.icon}</div>
              <h3 style={{ fontFamily: "var(--agri-font-heading)", fontWeight: 700, fontSize: "1rem", margin: 0, color: "var(--agri-green-deep)" }}>{f.title}</h3>
              <p style={{ color: "var(--agri-muted)", margin: 0, fontSize: "0.88rem", lineHeight: 1.55 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: "2.2rem" }}>
        <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.5rem", fontWeight: 700, color: "var(--agri-green-deep)", margin: "0 0 0.3rem" }}>Project teammates</h2>
        <p style={{ color: "var(--agri-muted)", margin: "0 0 1.2rem", fontSize: "0.95rem" }}>Department of Electronics &amp; Computer Engineering, SJCET Palai.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
          {TEAM.map((m) => (
            <div key={m.name} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: "0.9rem", padding: "1.1rem 1.2rem" }}>
              <div style={{ width: 46, height: 46, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(135deg, var(--agri-green), var(--agri-lime))", color: "#fff", fontWeight: 700, fontSize: "1rem", flexShrink: 0 }}>
                {m.initials}
              </div>
              <div style={{ fontFamily: "var(--agri-font-heading)", fontWeight: 700, color: "var(--agri-green-deep)", lineHeight: 1.25 }}>{m.name}</div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.5rem", fontWeight: 700, color: "var(--agri-green-deep)", margin: "0 0 0.8rem" }}>Built with</h2>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {STACK.map((t) => (
            <span key={t} style={{ padding: "0.4rem 0.85rem", borderRadius: "999px", border: "1px solid var(--agri-border)", background: "rgba(255,255,255,0.72)", color: "var(--agri-green-deep)", fontWeight: 600, fontSize: "0.84rem" }}>{t}</span>
          ))}
        </div>
      </section>
    </div>
  );
}
