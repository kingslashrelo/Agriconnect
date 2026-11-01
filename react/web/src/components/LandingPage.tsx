"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { CodeSlots } from "@/components/CodeSlots";

export function LandingPage() {
  const { setUser } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [role, setRole] = useState<"farmer" | "buyer">("farmer");
  const [aadhaar, setAadhaar] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [village, setVillage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [slotsKey, setSlotsKey] = useState(0);

  const submitLogin = async (value: string) => {
    if (loading || value.length !== 12) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.login(value);
      setUser({ role: res.role, id: res.user.farmer_id || res.user.buyer_id, name: res.user.name, ...res.user });
      router.push("/");
    } catch (err: any) {
      setError(err.message);
      setAadhaar("");
      setSlotsKey((k) => k + 1);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    submitLogin(aadhaar);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await api.register({ role, aadhaar, name, phone, village });
      setUser({ role: res.role, id: res.user.farmer_id || res.user.buyer_id, name: res.user.name, ...res.user });
      router.push("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const guestLogin = () => {
    setUser({ role: "guest", id: null, name: "Guest" });
    router.push("/");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "2rem 1rem" }}>
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🌱</div>
        <h1 style={{ fontFamily: "var(--agri-font-heading)", fontSize: "2.2rem", fontWeight: 700, color: "var(--agri-green-deep)", margin: 0 }}>AgriConnect</h1>
        <p style={{ color: "var(--agri-muted)", marginTop: "0.4rem" }}>Farm-to-market marketplace</p>
      </div>
      <div style={{ width: "100%", maxWidth: "440px", border: "1px solid var(--glass-border)", borderRadius: "22px", background: "var(--glass-bg-strong)", backdropFilter: "var(--glass-blur)", WebkitBackdropFilter: "var(--glass-blur)", boxShadow: "var(--glass-shadow)", padding: "2rem" }}>
        <div style={{ fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--agri-green-dark)", marginBottom: "1rem" }}>{mode === "login" ? "Sign in" : "Register"}</div>
        <div style={{ display: "flex", gap: "6px", background: "rgba(5, 150, 105, 0.08)", padding: "4px", borderRadius: "999px", marginBottom: "1.5rem" }}>
          <button onClick={() => { setMode("login"); setAadhaar(""); setError(""); }} style={{ flex: 1, padding: "0.5rem", borderRadius: "999px", border: "none", background: mode === "login" ? "linear-gradient(135deg, var(--agri-green), var(--agri-lime))" : "transparent", color: mode === "login" ? "#fff" : "var(--agri-text)", fontWeight: 600, cursor: "pointer" }}>Log in</button>
          <button onClick={() => { setMode("register"); setAadhaar(""); setError(""); }} style={{ flex: 1, padding: "0.5rem", borderRadius: "999px", border: "none", background: mode === "register" ? "linear-gradient(135deg, var(--agri-green), var(--agri-lime))" : "transparent", color: mode === "register" ? "#fff" : "var(--agri-text)", fontWeight: 600, cursor: "pointer" }}>Register</button>
        </div>
        {mode === "login" ? (
          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label style={{ display: "block", fontWeight: 600, marginBottom: "0.6rem", fontSize: "0.9rem" }}>Aadhaar number (12 digits)</label>
              <CodeSlots
                key={slotsKey}
                length={12}
                onChange={(v) => { setAadhaar(v); if (error) setError(""); }}
                onComplete={(v) => submitLogin(v)}
                status={aadhaar.length === 12 ? "success" : "typing"}
                outcome={error ? "error" : null}
              />
            </div>
            {error && <div style={{ color: "#dc2626", fontSize: "0.88rem" }}>{error}</div>}
            <button type="submit" disabled={loading} style={{ padding: "0.75rem", borderRadius: "12px", border: "none", background: "linear-gradient(135deg, var(--agri-green), var(--agri-lime))", color: "#fff", fontWeight: 600, cursor: "pointer", boxShadow: "0 8px 22px rgba(5, 150, 105, 0.28)" }}>{loading ? "Signing in..." : "Log in"}</button>
          </form>
        ) : (
          <form onSubmit={handleRegister} style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
            <div style={{ display: "flex", gap: "6px", background: "rgba(5, 150, 105, 0.08)", padding: "4px", borderRadius: "999px" }}>
              <button type="button" onClick={() => setRole("farmer")} style={{ flex: 1, padding: "0.4rem", borderRadius: "999px", border: "none", background: role === "farmer" ? "var(--agri-green-light)" : "transparent", color: role === "farmer" ? "var(--agri-green-deep)" : "var(--agri-text)", fontWeight: 600, cursor: "pointer", fontSize: "0.88rem" }}>Farmer</button>
              <button type="button" onClick={() => setRole("buyer")} style={{ flex: 1, padding: "0.4rem", borderRadius: "999px", border: "none", background: role === "buyer" ? "var(--agri-green-light)" : "transparent", color: role === "buyer" ? "var(--agri-green-deep)" : "var(--agri-text)", fontWeight: 600, cursor: "pointer", fontSize: "0.88rem" }}>Buyer</button>
            </div>
            <input type="text" value={aadhaar} onChange={(e) => setAadhaar(e.target.value)} maxLength={12} placeholder="Aadhaar number (12 digits)" style={{ padding: "0.7rem 1rem", borderRadius: "12px", border: "1px solid var(--agri-border)" }} />
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" style={{ padding: "0.7rem 1rem", borderRadius: "12px", border: "1px solid var(--agri-border)" }} />
            <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Phone number" style={{ padding: "0.7rem 1rem", borderRadius: "12px", border: "1px solid var(--agri-border)" }} />
            <input type="text" value={village} onChange={(e) => setVillage(e.target.value)} placeholder="Village / Location" style={{ padding: "0.7rem 1rem", borderRadius: "12px", border: "1px solid var(--agri-border)" }} />
            {error && <div style={{ color: "#dc2626", fontSize: "0.88rem" }}>{error}</div>}
            <button type="submit" disabled={loading} style={{ padding: "0.75rem", borderRadius: "12px", border: "none", background: "linear-gradient(135deg, var(--agri-green), var(--agri-lime))", color: "#fff", fontWeight: 600, cursor: "pointer" }}>{loading ? "Registering..." : "Register"}</button>
          </form>
        )}
        <button onClick={guestLogin} style={{ width: "100%", marginTop: "0.8rem", padding: "0.65rem", borderRadius: "12px", border: "1px solid var(--agri-border)", background: "transparent", color: "var(--agri-green-deep)", fontWeight: 600, cursor: "pointer" }}>Skip — browse as guest</button>
      </div>
    </div>
  );
}
