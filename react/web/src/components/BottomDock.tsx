"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/marketplace", label: "📋 Active Listings" },
  { href: "/place-order", label: "📦 Place Order" },
  { href: "/tracker", label: "📦 Order/Listing Tracker" },
  { href: "/reports", label: "📊 Reports" },
  { href: "/profit", label: "🧮 Profit Calculator" },
  { href: "/schemes", label: "🏛️ Scheme Explorer" },
  { href: "/crop-advisor", label: "🌱 Crop Advisor" },
];

export function BottomDock() {
  const pathname = usePathname();
  const { user } = useAuth();

  if (!user) return null;

  const items = user.role === "farmer" ? navItems.filter((item) => item.href !== "/place-order") : navItems;

  return (
    <div style={{ position: "fixed", bottom: "0.8rem", left: "50%", transform: "translateX(-50%)", zIndex: 1000002, width: "fit-content", maxWidth: "calc(100% - 2rem)", display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.6rem 0.8rem", borderRadius: "999px", border: "1px solid var(--glass-border)", background: "var(--glass-bg-strong)", backdropFilter: "var(--glass-blur)", WebkitBackdropFilter: "var(--glass-blur)", boxShadow: "var(--glass-shadow)", overflowX: "auto" }}>
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link key={item.href} href={item.href} style={{ padding: "0.48rem 0.85rem", borderRadius: "999px", textDecoration: "none", fontWeight: 600, fontSize: "0.88rem", whiteSpace: "nowrap", color: active ? "#fff" : "var(--agri-text)", background: active ? "linear-gradient(135deg, var(--agri-green), var(--agri-lime))" : "transparent", boxShadow: active ? "0 8px 18px rgba(5, 150, 105, 0.22)" : "none" }}>
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}
