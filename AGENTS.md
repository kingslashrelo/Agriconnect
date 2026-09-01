# AGENTS.md — Instructions for AI coding agents

This file is **auto-loaded by AI coding agents** (opencode, and others) every time they
access this repository. Read it fully before making any changes.

## Project: AgriConnect

AgriConnect is a **farm-to-market produce marketplace**.
- **Database layer (this repo)**: fully built on **Supabase** (PostgreSQL). Complete — do not
  re-architect it. It defines all tables, a quantity trigger, reporting views, and RPC
  functions. See `schema.sql`, `seed_data.sql`, and `SUPABASE_CONNECTION.md`.
- **UI layer**: a **Streamlit** app maintained separately (UI/hosting team). This repo is the
  source of truth for what the UI must surface.

## Division of work (IMPORTANT)

- **Database owner**: `kuri` — owns `schema.sql`, `seed_data.sql`, `.env.example`,
  `SUPABASE_CONNECTION.md`. All DB changes happen here.
- **UI owner**: `joseph` — owns the Streamlit `app.py` and hosting.
- An agent editing `app.py` (UI) must **NOT** modify the database schema, RPC functions, or
  connection details unless told otherwise. Conversely, database work must not depend on the
  UI code.

## Connection & keys

- The app connects with the **anon/publishable key** (public, safe to ship in the client).
- Keep DB credentials and the secret key out of the UI bundle. UI reads them from `.env` /
  Streamlit secrets only. Never log or display a secret key.
- Hosting runs on the user's NAS (Tailscale Funnel). The app is a Streamlit server; the DB
  stays on Supabase cloud. **Do not move the database to the NAS.**

## UI requirements the app MUST satisfy

These are requirements for `app.py` (the Streamlit UI), driven by the DB features available:

1. **Visual theme**
   - Use a **farm/green theme** throughout (greens, earthy accents).
   - Apply **glassmorphism** styling (frosted/blurred translucent cards) to panels and modals.
   - Fix the **theme toggle being glitchy** on top of the site — the toggle must not conflict
     with the hard-coded green styling. Pick one consistent theme.
   - Fix the **left panel / sidebar radio navigation layout** — it is currently laid out
     incorrectly. The page navigation must be clean and legible.
2. **Login / identification**
   - Provide a **login page**: farmer login and buyer login.
   - Login uses **Aadhaar (12-digit government ID)**. The number is used ONLY to log in and is
     verified against the database by a one-way hash — it must **never be displayed or logged**.
   - Call these RPCs to log in/register:
     - `aadhaar_farmer_login({p_aadhaar})` → returns `farmer_id`, `name` (or no row if wrong).
     - `aadhaar_buyer_login({p_aadhaar})` → returns `buyer_id`, `name`.
     - Register/set the hash on signup via `set_farmer_aadhaar({p_farmer_id,p_aadhaar})` and
       `set_buyer_aadhaar({p_buyer_id,p_aadhaar})`.
   - After login, the UI should also surface **government subsidies/pensions** for the logged-in
     farmer via the `schemes` table (eligibility flag, name, date added).
3. **Surface the full database** — the UI should expose these DB features (all exist and are
   tested). Currently the UI under-uses them; wire them up:
   - **Marketplace**: active listings (crop, quantity, unit, price) from the `listings` table +
     `active_listings_view`; place an order (the `after_order_insert` trigger auto-decrements
     stock).
   - **Purchase & order lifecycle**: create orders; update order status by calling
     `update_order_status({p_order_id,p_new_status,p_changed_by})` (valid transitions are
     enforced by the DB); show `order_history_view` and `order_status_audit_view`.
   - **Crop advisor**: call `recommend_crops({p_ph,p_moisture,p_n,p_p,p_k,p_temp,p_season})` to
     rank the best crops for given soil/weather and show estimated revenue + market outlook.
   - **Inventory & sales**: `inventory_view`, `low_stock_view`, `monthly_sales_summary_view`.
   - **Reports**: `get_most_active_buyers()`, `get_farmer_ratings()`, `get_farmer_revenue` views /
     RPCs. Build the "Reports" pages on these.
   - **Payments**: the `payments` table and `pending_payments_view`.
4. **Bug fixes already observed**: theme toggle glitch; left sidebar radio-nav layout. Fix these
   first.

## How to read the DB

Tables (public schema): `farmers`, `buyers`, `listings`, `orders`, `payments`, `ratings`,
`schemes`, `price_history`, `order_status_history`, `crops`.

Views: `active_listings_view`, `most_active_buyers_view`, `unsold_stock_view`,
`farmer_avg_rating_view`, `pending_payments_view`, `inventory_view`, `low_stock_view`,
`monthly_sales_summary_view`, `order_history_view`, `order_status_audit_view`.

RPC functions (call via `supabase.rpc(...)`):
`recommend_crops`, `update_order_status`, `get_farmer_revenue`, `get_most_active_buyers`,
`get_farmer_ratings`, `aadhaar_farmer_login`, `aadhaar_buyer_login`, `set_farmer_aadhaar`,
`set_buyer_aadhaar`.

Full schema + SQL is in `schema.sql`. Seed/demo data is in `seed_data.sql`. Connection details
(endpoints, pooler/direct strings) are in `SUPABASE_CONNECTION.md`.

## Non-goals (do NOT do)

- Do NOT create a new database or migrate away from Supabase.
- Do NOT store or log raw Aadhaar numbers anywhere.
- Do NOT expose the secret key in client code.
- Do NOT touch the "buildback" app on the NAS (different service on port 5001).

## Hosting note (UI owner)

The running app is deployed on the NAS (`/opt/agriconnect`, Streamlit on port 5002) and exposed
via Tailscale Funnel on port 8443 → `https://vault.tail7f289d.ts.net:8443`. After changing
`app.py`, the UI owner should redeploy/restart there (network is only reachable from the home
network).