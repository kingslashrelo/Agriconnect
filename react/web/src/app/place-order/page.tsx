"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { btnGhost, btnPrimary, cardStyle, cropEmoji, inr, inputStyle, Note, PageHeader } from "@/components/ui";

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

function PlaceOrderForm() {
  const { user } = useAuth();
  const params = useSearchParams();
  const preset = params.get("listing");

  const [listings, setListings] = useState<Listing[]>([]);
  const [listingId, setListingId] = useState<string>(preset ?? "");
  const [quantity, setQuantity] = useState("");
  const [address, setAddress] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [placed, setPlaced] = useState<any>(null);

  useEffect(() => {
    if (!user) return;
    api
      .getActiveListings()
      .then((data) => {
        const rows = Array.isArray(data) ? data : [];
        setListings(rows);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [user]);

  useEffect(() => {
    if (preset) setListingId(String(preset));
    else if (listings[0]) setListingId(String(listings[0].listing_id));
  }, [preset, listings]);

  const selected = useMemo(() => listings.find((l) => String(l.listing_id) === listingId), [listings, listingId]);
  const qty = Number(quantity) || 0;
  const total = selected ? qty * selected.price_per_unit : 0;
  const canBuy = user?.role === "buyer";
  const overStock = selected ? qty > selected.quantity : false;

  if (!user) return <LandingPage />;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected || !canBuy || qty <= 0 || overStock) return;
    setSubmitting(true);
    setError("");
    try {
      const order = await api.createOrder({
        listing_id: selected.listing_id,
        buyer_id: user.id,
        quantity: qty,
        delivery_address: address || undefined,
        notes: notes || undefined,
      });
      setPlaced({ ...order, listing: selected, quantity: qty });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (placed) {
    return (
      <div>
        <PageHeader title="Order placed" subtitle="The farmer will confirm your order shortly" />
        <div style={{ ...cardStyle, maxWidth: 560 }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.4rem" }}>✅</div>
          <h2 style={{ fontFamily: "var(--agri-font-heading)", margin: "0 0 0.8rem", color: "var(--agri-green-deep)" }}>
            Order #{placed.order_id}
          </h2>
          <div style={{ display: "grid", gap: "0.45rem", fontSize: "0.95rem" }}>
            <div><strong>Crop:</strong> {placed.listing.crop_name}</div>
            <div><strong>Quantity:</strong> {placed.quantity} {placed.listing.unit}</div>
            <div><strong>Order value:</strong> {inr(placed.quantity * placed.listing.price_per_unit)}</div>
            <div><strong>Farmer:</strong> {placed.listing.farmer_name}{placed.listing.village ? ` · ${placed.listing.village}` : ""}</div>
            {address && <div><strong>Delivery:</strong> {address}</div>}
            <div><strong>Status:</strong> pending</div>
          </div>
          <div style={{ display: "flex", gap: "0.6rem", marginTop: "1.2rem", flexWrap: "wrap" }}>
            <Link href="/tracker" style={{ ...btnPrimary, textDecoration: "none" }}>Track order</Link>
            <button onClick={() => { setPlaced(null); setQuantity(""); setNotes(""); }} style={btnGhost}>Place another order</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Place Order" subtitle="Buy produce directly from a farmer" />

      {!canBuy && (
        <div style={{ marginBottom: "1rem" }}>
          <Note tone="warn">
            You are signed in as <strong>{user.role}</strong>. Only buyer accounts can place orders — log out from the top bar to sign in with a buyer Aadhaar.
          </Note>
        </div>
      )}

      <div className="agri-split">
        <form onSubmit={submit} style={{ ...cardStyle, display: "grid", gap: "0.9rem" }}>
          <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
            Listing
            <select value={listingId} onChange={(e) => setListingId(e.target.value)} style={inputStyle} disabled={loading}>
              {listings.map((l) => (
                <option key={l.listing_id} value={l.listing_id}>
                  {l.crop_name} — {l.farmer_name} — {inr(l.price_per_unit)}/{l.unit}
                </option>
              ))}
            </select>
          </label>

          <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
            Quantity {selected ? `(${selected.unit})` : ""}
            <input
              type="number"
              min="0"
              step="any"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder={selected ? `Max ${selected.quantity}` : "Enter quantity"}
              style={inputStyle}
            />
          </label>

          <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
            Delivery address
            <textarea value={address} onChange={(e) => setAddress(e.target.value)} rows={2} placeholder="House, street, town" style={{ ...inputStyle, resize: "vertical" }} />
          </label>

          <label style={{ display: "grid", gap: "0.35rem", fontSize: "0.9rem", fontWeight: 600 }}>
            Notes for the farmer
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} placeholder="Optional" style={{ ...inputStyle, resize: "vertical" }} />
          </label>

          {overStock && <Note tone="warn">Only {selected?.quantity} {selected?.unit} available for this listing.</Note>}
          {error && <Note tone="error">{error}</Note>}

          <button type="submit" disabled={!canBuy || submitting || !selected || qty <= 0 || overStock} style={{ ...btnPrimary, opacity: !canBuy || submitting || !selected || qty <= 0 || overStock ? 0.55 : 1 }}>
            {submitting ? "Placing order…" : "Place order"}
          </button>
        </form>

        <div style={{ ...cardStyle, display: "grid", gap: "0.8rem" }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--agri-green-dark)" }}>Order summary</div>
          {selected ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: "0.7rem" }}>
                <span style={{ fontSize: "2rem" }}>{cropEmoji(selected.crop_name)}</span>
                <div>
                  <div style={{ fontWeight: 700, color: "var(--agri-green-deep)" }}>{selected.crop_name}</div>
                  <div style={{ fontSize: "0.84rem", color: "var(--agri-muted)" }}>{selected.farmer_name}{selected.village ? ` · ${selected.village}` : ""}</div>
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.92rem" }}>
                <span style={{ color: "var(--agri-muted)" }}>Rate</span>
                <span>{inr(selected.price_per_unit)} / {selected.unit}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.92rem" }}>
                <span style={{ color: "var(--agri-muted)" }}>Available</span>
                <span>{selected.quantity} {selected.unit}</span>
              </div>
              <div style={{ borderTop: "1px dashed var(--agri-border)", paddingTop: "0.7rem", display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: "1.1rem", color: "var(--agri-green-deep)" }}>
                <span>Total</span>
                <span>{inr(total)}</span>
              </div>
            </>
          ) : (
            <div style={{ color: "var(--agri-muted)", fontSize: "0.9rem" }}>{loading ? "Loading listings…" : "Choose a listing to begin."}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PlaceOrderPage() {
  return (
    <Suspense fallback={<div style={{ color: "var(--agri-muted)", padding: "2rem 0" }}>Loading…</div>}>
      <PlaceOrderForm />
    </Suspense>
  );
}
