"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { Badge, btnPrimary, cardStyle, inputStyle, Note, PageHeader } from "@/components/ui";

type Scheme = {
  scheme_id: number;
  farmer_id: number;
  scheme_name: string;
  eligible: boolean;
  date_added?: string;
};

type SchemeAnswers = { land: number; income: number; livestock: boolean; organic: boolean };

const SCHEME_CATALOG: { name: string; desc: string; test: (a: SchemeAnswers) => boolean }[] = [
  { name: "PM-KISAN", desc: "₹6,000/year income support for small & marginal farmers.", test: (a) => 0 < a.land && a.land <= 2 },
  { name: "PM Fasal Bima Yojana", desc: "Subsidised crop insurance against crop loss.", test: (a) => a.land > 0 },
  { name: "Soil Health Card Scheme", desc: "Free soil testing and nutrient recommendations.", test: (a) => a.land > 0 },
  { name: "Kisan Credit Card", desc: "Cheap institutional credit for farming needs.", test: (a) => a.land > 0 || a.livestock },
  { name: "Paramparagat Krishi Vikas Yojana", desc: "Support for cluster-based organic farming.", test: (a) => a.organic && a.land > 0 },
  { name: "Agriculture Infrastructure Fund", desc: "Long-term credit for post-harvest infrastructure.", test: (a) => a.land >= 2 },
];

const labelStyle = { display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 };

function SchemeChecker({ storedNames }: { storedNames: string[] }) {
  const [land, setLand] = useState("1");
  const [income, setIncome] = useState("200000");
  const [livestock, setLivestock] = useState(false);
  const [organic, setOrganic] = useState(false);
  const [matches, setMatches] = useState<typeof SCHEME_CATALOG | null>(null);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const answers: SchemeAnswers = { land: Number(land) || 0, income: Number(income) || 0, livestock, organic };
    setMatches(SCHEME_CATALOG.filter((s) => s.test(answers)));
  };

  return (
    <div style={{ ...cardStyle, display: "grid", gap: "0.9rem" }}>
      <div>
        <div style={{ fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--agri-green-dark)" }}>Check your eligibility</div>
        <div style={{ color: "var(--agri-muted)", fontSize: "0.82rem", marginTop: "0.25rem" }}>Answer a few questions to see schemes you likely qualify for. Indicative only.</div>
      </div>

      <form onSubmit={submit}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.8rem" }}>
          <label style={labelStyle}>
            Land holding (hectares)
            <input type="number" min="0" step="0.5" value={land} onChange={(e) => setLand(e.target.value)} style={inputStyle} />
          </label>
          <label style={labelStyle}>
            Annual income (₹)
            <input type="number" min="0" step="1000" value={income} onChange={(e) => setIncome(e.target.value)} style={inputStyle} />
          </label>
          <label style={{ ...labelStyle, alignContent: "end" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontSize: "0.85rem", padding: "0.55rem 0" }}>
              <input type="checkbox" checked={livestock} onChange={(e) => setLivestock(e.target.checked)} /> I have livestock
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontSize: "0.85rem" }}>
              <input type="checkbox" checked={organic} onChange={(e) => setOrganic(e.target.checked)} /> Interested in organic farming
            </span>
          </label>
        </div>
        <div style={{ marginTop: "0.9rem" }}>
          <button type="submit" style={btnPrimary}>Check schemes</button>
        </div>
      </form>

      {matches && (
        <div style={{ display: "grid", gap: "0.6rem" }}>
          {matches.length ? matches.map((s) => {
            const registered = storedNames.map((n) => n.trim().toLowerCase()).includes(s.name.toLowerCase());
            return (
              <div key={s.name} style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "0.6rem", padding: "0.7rem 0.85rem", borderRadius: "12px", background: "rgba(255,255,255,0.7)", border: "1px solid var(--agri-border)" }}>
                <div>
                  <div style={{ fontFamily: "var(--agri-font-heading)", fontWeight: 700, fontSize: "0.95rem", color: "var(--agri-green-deep)" }}>{s.name}</div>
                  <div style={{ color: "var(--agri-muted)", fontSize: "0.82rem", marginTop: "0.15rem" }}>{s.desc}</div>
                </div>
                <Badge tone="yes">{registered ? "Already on your profile" : "You likely qualify"}</Badge>
              </div>
            );
          }) : <Note tone="warn">No schemes matched those answers. Try adjusting land holding or income.</Note>}
          <div style={{ color: "var(--agri-muted)", fontSize: "0.78rem" }}>Indicative check — not an official government determination.</div>
        </div>
      )}
    </div>
  );
}

export default function SchemesPage() {
  const { user } = useAuth();
  const [schemes, setSchemes] = useState<Scheme[]>([]);

  const isFarmer = user?.role === "farmer" && Number(user?.id) > 0;

  useEffect(() => {
    if (!user || !isFarmer) return;
    api.getFarmerSchemes(Number(user.id))
      .then((s) => setSchemes(Array.isArray(s) ? s : []))
      .catch(() => setSchemes([]));
  }, [user, isFarmer]);

  if (!user) return <LandingPage />;

  return (
    <div>
      <PageHeader title="Scheme Explorer" subtitle={isFarmer ? "Schemes and subsidies linked to your farm" : "Government schemes and subsidies"} />
      {!isFarmer && (
        <div style={{ marginBottom: "1.2rem" }}>
          <Note>Scheme eligibility is tracked per farmer account. Sign in with your farmer Aadhaar to link schemes to your farm.</Note>
        </div>
      )}
      <SchemeChecker storedNames={isFarmer ? schemes.map((s) => s.scheme_name) : []} />
    </div>
  );
}
