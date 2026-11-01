"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { btnPrimary, cardStyle, cropEmoji, inputStyle, Note, PageHeader } from "@/components/ui";

type Recommendation = {
  crop_name: string;
  match_score: number;
  match_pct: number;
  revenue?: string;
  market_outlook?: string;
};

const SEASONS = ["Kharif", "Rabi", "Zaid", "Perennial"];

export default function CropAdvisorPage() {
  const { user } = useAuth();
  const [form, setForm] = useState({ ph: "6.5", moisture: "50", n: "3", p: "3", k: "3", temp: "28", season: SEASONS[0] });
  const [results, setResults] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [ran, setRan] = useState(false);

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm({ ...form, [k]: e.target.value });

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setRan(true);
    try {
      const data = await api.recommendCrops({
        ph: Number(form.ph),
        moisture: Number(form.moisture),
        n: Number(form.n),
        p: Number(form.p),
        k: Number(form.k),
        temp: Number(form.temp),
        season: form.season,
      });
      if (Array.isArray(data)) {
        setResults(data);
      } else {
        setResults([]);
        setError(data?.error || "Could not generate recommendations.");
      }
    } catch (err: any) {
      setResults([]);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return <LandingPage />;

  return (
    <div>
      <PageHeader title="Crop Advisor" subtitle="Match crops to your soil, climate and season" />

      <div className="agri-split">
        <form onSubmit={submit} style={{ ...cardStyle, display: "grid", gap: "0.9rem" }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--agri-green-dark)" }}>Soil & climate</div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "0.8rem" }}>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
              pH
              <input type="number" step="0.1" min="0" max="14" value={form.ph} onChange={set("ph")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
              Moisture (%)
              <input type="number" step="1" min="0" max="100" value={form.moisture} onChange={set("moisture")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
              Temperature (°C)
              <input type="number" step="0.5" value={form.temp} onChange={set("temp")} style={inputStyle} />
            </label>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.8rem" }}>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
              Nitrogen (N)
              <input type="number" step="0.1" min="0" value={form.n} onChange={set("n")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
              Phosphorus (P)
              <input type="number" step="0.1" min="0" value={form.p} onChange={set("p")} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
              Potassium (K)
              <input type="number" step="0.1" min="0" value={form.k} onChange={set("k")} style={inputStyle} />
            </label>
          </div>

          <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.85rem", fontWeight: 600 }}>
            Season
            <select value={form.season} onChange={set("season")} style={inputStyle}>
              {SEASONS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>

          <button type="submit" disabled={loading} style={{ ...btnPrimary, opacity: loading ? 0.6 : 1 }}>
            {loading ? "Analysing soil…" : "Recommend crops"}
          </button>

          <div style={{ fontSize: "0.78rem", color: "var(--agri-muted)" }}>
            Tip: N, P and K are soil-test values on a 0–10 scale. If you don’t have a soil report, the defaults are a safe starting point.
          </div>
        </form>

        <div style={{ ...cardStyle, display: "grid", gap: "0.8rem" }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--agri-green-dark)" }}>Recommendations</div>

          {!ran && <div style={{ color: "var(--agri-muted)", fontSize: "0.9rem" }}>Enter your soil values and press <strong>Recommend crops</strong>.</div>}
          {loading && <div style={{ color: "var(--agri-muted)", fontSize: "0.9rem" }}>Comparing your field against the crop database…</div>}
          {error && <Note tone="error">{error}</Note>}
          {ran && !loading && !error && !results.length && <Note>No crops matched. Try adjusting pH, moisture or nutrient values.</Note>}

          {results.map((r, i) => (
            <div key={`${r.crop_name}-${i}`} style={{ padding: "0.8rem 0.9rem", borderRadius: "14px", border: "1px solid var(--agri-border)", background: "rgba(255,255,255,0.72)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.6rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}>
                  <span style={{ fontSize: "1.3rem" }}>{cropEmoji(r.crop_name)}</span>
                  <div>
                    <div style={{ fontWeight: 700, color: "var(--agri-green-deep)" }}>{r.crop_name}</div>
                    {r.revenue && <div style={{ fontSize: "0.78rem", color: "var(--agri-muted)" }}>{r.revenue}</div>}
                  </div>
                </div>
                <div style={{ fontWeight: 700, color: "var(--agri-green-dark)", fontSize: "0.95rem" }}>{Math.round(r.match_pct)}%</div>
              </div>
              <div style={{ height: 7, borderRadius: 999, background: "rgba(5,150,105,0.1)", overflow: "hidden", marginTop: "0.55rem" }}>
                <div style={{ width: `${Math.max(4, Math.min(100, r.match_pct))}%`, height: "100%", borderRadius: 999, background: "linear-gradient(90deg, var(--agri-green), var(--agri-lime))" }} />
              </div>
              {r.market_outlook && <div style={{ fontSize: "0.78rem", color: "var(--agri-muted)", marginTop: "0.45rem" }}>{r.market_outlook}</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
