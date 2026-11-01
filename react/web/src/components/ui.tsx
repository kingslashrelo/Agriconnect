import type { CSSProperties, ReactNode } from "react";

export const inputStyle: CSSProperties = {
  width: "100%",
  padding: "0.7rem 0.9rem",
  borderRadius: "12px",
  border: "1px solid var(--agri-border)",
  background: "rgba(255,255,255,0.9)",
  color: "var(--agri-text)",
  fontSize: "0.95rem",
  outline: "none",
};

export const btnPrimary: CSSProperties = {
  padding: "0.72rem 1.1rem",
  borderRadius: "12px",
  border: "none",
  background: "linear-gradient(135deg, var(--agri-green), var(--agri-lime))",
  color: "#fff",
  fontWeight: 600,
  cursor: "pointer",
  boxShadow: "0 10px 24px rgba(5, 150, 105, 0.24)",
};

export const btnGhost: CSSProperties = {
  padding: "0.55rem 0.9rem",
  borderRadius: "999px",
  border: "1px solid var(--agri-border)",
  background: "rgba(255,255,255,0.7)",
  color: "var(--agri-green-deep)",
  fontWeight: 600,
  cursor: "pointer",
  fontSize: "0.88rem",
};

export const cardStyle: CSSProperties = {
  border: "1px solid var(--glass-border)",
  borderRadius: "18px",
  background: "var(--glass-bg-strong)",
  backdropFilter: "var(--glass-blur)",
  WebkitBackdropFilter: "var(--glass-blur)",
  boxShadow: "0 18px 44px -30px rgba(5, 150, 105, 0.55)",
  padding: "1.4rem",
};

export function PageHeader({ title, subtitle, right }: { title: string; subtitle?: string; right?: ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", marginBottom: "1.4rem" }}>
      <div>
        <h1 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "1.9rem", fontWeight: 700, color: "var(--agri-green-deep)", margin: 0 }}>{title}</h1>
        {subtitle && <p style={{ color: "var(--agri-muted)", margin: "0.35rem 0 0", fontSize: "0.95rem" }}>{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}

export function Stat({ label, value, icon }: { label: string; value: ReactNode; icon?: string }) {
  return (
    <div style={{ ...cardStyle, padding: "1rem 1.2rem", display: "flex", alignItems: "center", gap: "0.8rem" }}>
      {icon && <span style={{ fontSize: "1.4rem" }}>{icon}</span>}
      <div>
        <div style={{ fontSize: "1.45rem", fontWeight: 700, color: "var(--agri-green-deep)", lineHeight: 1.1 }}>{value}</div>
        <div style={{ color: "var(--agri-muted)", fontSize: "0.82rem" }}>{label}</div>
      </div>
    </div>
  );
}

const TONES: Record<string, { bg: string; fg: string }> = {
  pending: { bg: "#FEF3C7", fg: "#92400E" },
  confirmed: { bg: "#DBEAFE", fg: "#1D4ED8" },
  delivered: { bg: "#D1FAE5", fg: "#047857" },
  paid: { bg: "#A7F3D0", fg: "#065F46" },
  cancelled: { bg: "#FEE2E2", fg: "#B91C1C" },
  available: { bg: "#D1FAE5", fg: "#047857" },
  sold_out: { bg: "#F3F4F6", fg: "#4B5563" },
  yes: { bg: "#D1FAE5", fg: "#047857" },
  no: { bg: "#FEE2E2", fg: "#B91C1C" },
};

export function Badge({ children, tone }: { children: ReactNode; tone?: string }) {
  const t = TONES[String(tone ?? "").toLowerCase()] ?? { bg: "rgba(5,150,105,0.1)", fg: "var(--agri-green-deep)" };
  return (
    <span style={{ display: "inline-block", padding: "0.2rem 0.6rem", borderRadius: "999px", background: t.bg, color: t.fg, fontSize: "0.76rem", fontWeight: 700, textTransform: "capitalize" }}>
      {children}
    </span>
  );
}

export type Column = { key: string; label: string; render?: (row: any, index: number) => ReactNode; align?: "left" | "right" | "center" };

export function DataTable({ columns, rows, empty = "Nothing to show yet", maxHeight }: { columns: Column[]; rows: any[]; empty?: string; maxHeight?: number }) {
  if (!rows.length) {
    return <div style={{ padding: "1.6rem", textAlign: "center", color: "var(--agri-muted)", fontSize: "0.9rem" }}>{empty}</div>;
  }
  return (
    <div className={maxHeight ? "agri-table-scroll" : undefined} style={{ overflowX: "auto", ...(maxHeight ? { maxHeight, overflowY: "auto" as const } : {}) }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} style={{ textAlign: c.align ?? "left", padding: "0.55rem 0.6rem", borderBottom: "1px solid var(--agri-border)", color: "var(--agri-muted)", fontWeight: 600, fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.04em", whiteSpace: "nowrap" }}>
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.id ?? row.key ?? i}>
              {columns.map((c) => (
                <td key={c.key} style={{ padding: "0.6rem", borderBottom: "1px solid rgba(230,235,232,0.7)", textAlign: c.align ?? "left", verticalAlign: "middle" }}>
                  {c.render ? c.render(row, i) : row[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Note({ children, tone = "info" }: { children: ReactNode; tone?: "info" | "warn" | "error" | "success" }) {
  const map = {
    info: { bg: "rgba(5,150,105,0.08)", bd: "rgba(5,150,105,0.25)", fg: "var(--agri-green-deep)" },
    warn: { bg: "rgba(245,158,11,0.12)", bd: "rgba(245,158,11,0.35)", fg: "#92400E" },
    error: { bg: "rgba(239,68,68,0.1)", bd: "rgba(239,68,68,0.3)", fg: "#B91C1C" },
    success: { bg: "rgba(16,185,129,0.12)", bd: "rgba(16,185,129,0.3)", fg: "#047857" },
  }[tone];
  return <div style={{ padding: "0.8rem 1rem", borderRadius: "12px", background: map.bg, border: `1px solid ${map.bd}`, color: map.fg, fontSize: "0.9rem" }}>{children}</div>;
}

export const inr = (n: number | null | undefined) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(n) || 0);

export const CROP_EMOJI: Record<string, string> = {
  coconut: "🥥", rubber: "🌳", "rubber sheet": "🌳", pepper: "🌶️", "black pepper": "🌶️", banana: "🍌", "nendran banana": "🍌",
  cardamom: "🌿", rice: "🌾", paddy: "🌾", maize: "🌽", groundnut: "🥜", soybean: "🫘", cotton: "🧵", areca: "🌴",
  "areca nut": "🌴", coffee: "☕", tea: "🍵", ginger: "🫚", turmeric: "🟡", tapioca: "🥔", mango: "🥭",
  tomato: "🍅", onion: "🧅", vegetables: "🥬", "green gram": "🫛", "black gram": "🫘", sesame: "🌾",
};

export const cropEmoji = (name: string) => CROP_EMOJI[(name || "").toLowerCase()] ?? "🌱";
