"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export function TopDock() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="agri-top-dock">
      <Link href="/" className="agri-pill agri-brand-pill">
        <span className="agri-brand-logo">🌱</span>
        <div className="agri-brand-copy">
          <div className="agri-brand-name">AgriConnect</div>
          <div className="agri-brand-sub">Farm-to-market marketplace</div>
        </div>
      </Link>

      <div className="agri-pill agri-account-pill">
        <span className="agri-account-name">
          {user.name}
          <span className="agri-role"> · {user.role}</span>
        </span>
        <button className="agri-logout" onClick={logout}>Log out</button>
      </div>
    </div>
  );
}
