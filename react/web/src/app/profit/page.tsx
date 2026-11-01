"use client";

import { useMemo, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { btnGhost, btnPrimary, cardStyle, inr, inputStyle, Note, PageHeader } from "@/components/ui";

const NUM = (v: string) => Number(v) || 0;

const CROPS = [
  "Nendran Banana",
  "Rubber Sheet",
  "Black Pepper",
  "Coconut",
  "Cardamom",
  "Tapioca",
  "Areca Nut",
  "Ginger",
  "Turmeric",
  "Coffee",
  "Tea",
  "Rice",
  "Maize",
  "Groundnut",
  "Soybean",
  "Cotton",
  "Vegetables",
];

export default function ProfitPage() {
  const { user } = useAuth();
  const [form, setForm] = useState({
    crop: "Nendran Banana",
    area: "1",
    yieldQ: "120",
    price: "4500",
    seed: "4000",
    fertilizer: "6000",
    labour: "12000",
    other: "3000",
  });

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm({ ...form, [k]: e.target.value });

  const calc = useMemo(() => {
    const area = NUM(form.area);
    const yieldQ = NUM(form.yieldQ);
    const price = NUM(form.price);
    const seed = NUM(form.seed);
    const fertilizer = NUM(form.fertilizer);
    const labour = NUM(form.labour);
    const other = NUM(form.other);
    const cost = seed + fertilizer + labour + other;
    const revenue = yieldQ * price;
    const profit = revenue - cost;
    const margin = revenue > 0 ? (profit / revenue) * 100 : 0;
    const perAcre = area > 0 ? profit / area : 0;
    return { area, yieldQ, price, seed, fertilizer, labour, other, cost, revenue, profit, margin, perAcre };
  }, [form]);

  if (!user) return <LandingPage />;

  const positive = calc.profit >= 0;
  const costParts = [
    { label: "Seed", value: calc.seed, color: "#34D399" },
    { label: "Fertilizer", value: calc.fertilizer, color: "#10B981" },
    { label: "Labour", value: calc.labour, color: "#059669" },
    { label: "Other", value: calc.other, color: "#065F46" },
  ];
  const costTotal = Math.max(1, calc.cost + Math.max(0, calc.profit));

  return (
    <div>
      <PageHeader title="Profit Calculator" subtitle="Estimate costs, revenue and margin for a crop season" />

      <div className="agri-split">
        <div style={{ ...cardStyle, display: "grid", gap: "0.9rem" }}>
          <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
            Crop
            <select value={form.crop} onChange={set("crop")} style={inputStyle}>
              {CROPS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.8rem" }}>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Area (acres)
              <input type="number" min="0" step="any" value={form.area} onChange={set("area")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Expected yield (quintals)
              <input type="number" min="0" step="any" value={form.yieldQ} onChange={set("yieldQ")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Selling price (₹ / quintal)
              <input type="number" min="0" step="any" value={form.price} onChange={set("price")} style={inputStyle} />
            </label>
          </div>

          <div style={{ fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--agri-green-dark)", marginTop: "0.3rem" }}>Costs (₹)</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.8rem" }}>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Seed / planting
              <input type="number" min="0" step="any" value={form.seed} onChange={set("seed")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Fertilizer / pesticide
              <input type="number" min="0" step="any" value={form.fertilizer} onChange={set("fertilizer")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Labour
              <input type="number" min="0" step="any" value={form.labour} onChange={set("labour")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
              Other costs
              <input type="number" min="0" step="any" value={form.other} onChange={set("other")} style={inputStyle} />
            </label>
          </div>

          <div style={{ display: "flex", gap: "0.6rem" }}>
            <button
              onClick={() => setForm({ crop: "Nendran Banana", area: "1", yieldQ: "120", price: "4500", seed: "4000", fertilizer: "6000", labour: "12000", other: "3000" })}
              style={btnGhost}
            >
              Reset example
            </button>
          </div>
        </div>

        <div style={{ ...cardStyle, display: "grid", gap: "0.9rem" }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--agri-green-dark)" }}>Result for {form.crop || "your crop"}</div>

          <div>
            <div style={{ color: "var(--agri-muted)", fontSize: "0.85rem" }}>Gross revenue</div>
            <div style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.8rem", fontWeight: 700, color: "var(--agri-green-deep)" }}>{inr(calc.revenue)}</div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.7rem" }}>
            <div style={{ padding: "0.7rem 0.8rem", borderRadius: "12px", background: "rgba(255,255,255,0.7)", border: "1px solid var(--agri-border)" }}>
              <div style={{ fontSize: "0.78rem", color: "var(--agri-muted)" }}>Total cost</div>
              <div style={{ fontWeight: 700 }}>{inr(calc.cost)}</div>
            </div>
            <div style={{ padding: "0.7rem 0.8rem", borderRadius: "12px", background: positive ? "#ECFDF5" : "#FEF2F2", border: `1px solid ${positive ? "#A7F3D0" : "#FECACA"}` }}>
              <div style={{ fontSize: "0.78rem", color: positive ? "#047857" : "#B91C1C" }}>Net profit</div>
              <div style={{ fontWeight: 700, color: positive ? "#047857" : "#B91C1C" }}>{inr(calc.profit)}</div>
            </div>
            <div style={{ padding: "0.7rem 0.8rem", borderRadius: "12px", background: "rgba(255,255,255,0.7)", border: "1px solid var(--agri-border)" }}>
              <div style={{ fontSize: "0.78rem", color: "var(--agri-muted)" }}>Margin</div>
              <div style={{ fontWeight: 700 }}>{calc.margin.toFixed(1)}%</div>
            </div>
            <div style={{ padding: "0.7rem 0.8rem", borderRadius: "12px", background: "rgba(255,255,255,0.7)", border: "1px solid var(--agri-border)" }}>
              <div style={{ fontSize: "0.78rem", color: "var(--agri-muted)" }}>Profit / acre</div>
              <div style={{ fontWeight: 700 }}>{inr(calc.perAcre)}</div>
            </div>
          </div>

          <div>
            <div style={{ display: "flex", height: 12, borderRadius: 999, overflow: "hidden", background: "rgba(5,150,105,0.08)" }}>
              {costParts.map((p) => (
                <div key={p.label} title={`${p.label}: ${inr(p.value)}`} style={{ width: `${(p.value / costTotal) * 100}%`, background: p.color }} />
              ))}
              {positive && <div title={`Profit: ${inr(calc.profit)}`} style={{ width: `${(calc.profit / costTotal) * 100}%`, background: "#A7F3D0" }} />}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.7rem", marginTop: "0.5rem", fontSize: "0.75rem", color: "var(--agri-muted)" }}>
              {costParts.map((p) => (
                <span key={p.label} style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
                  <span style={{ width: 8, height: 8, borderRadius: 4, background: p.color, display: "inline-block" }} /> {p.label}
                </span>
              ))}
              {positive && (
                <span style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
                  <span style={{ width: 8, height: 8, borderRadius: 4, background: "#A7F3D0", display: "inline-block" }} /> Profit
                </span>
              )}
            </div>
          </div>

          {calc.profit < 0 && <Note tone="error">Costs exceed revenue at these numbers — try a higher price or yield, or lower input costs.</Note>}
          {calc.profit >= 0 && calc.margin < 15 && <Note tone="warn">Margin is under 15%. Small cost changes could flip this season negative.</Note>}
        </div>
      </div>
    </div>
  );
}
