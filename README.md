# AgriConnect — Database (Supabase)

This repo contains the **database layer** of AgriConnect. It defines and seeds the entire Supabase backend. The Streamlit UI lives in a separate part of the project (maintained by the UI team).

The database runs on **Supabase** (PostgreSQL) and is accessed via the `supabase-py` REST client (PostgREST) and SQL RPC functions.

## Contents

- **`schema.sql`** — full schema: tables, trigger, reporting views, RPC functions, and RLS policies.
- **`seed_data.sql`** — demo data (farmers, buyers, listings, orders, payments, ratings, schemes, price history, and the crop advisor knowledge base).
- **`.env.example`** — environment variable template.
- **`requirements.txt`** — Python deps for the data layer.
- **`README.md`** — this file.

## 1. Create your Supabase project

1. Sign up / log in at [supabase.com](https://supabase.com).
2. Create a new project (free tier works). Note your **Project URL** (e.g. `https://xyzcompany.supabase.co`) and your **secret key** (the new `sb_secret_...` key, which replaces the old `service_role` key).

> The secret key bypasses Row Level Security, so all read/write works out of the box. It's safe for a learning project because it lives only on the server (in `.env` / Streamlit secrets), never exposed to the browser.

## 2. Create the database schema

Either run the SQL in the **Supabase SQL Editor** (Dashboard → SQL Editor → New query → paste → Run), or run it directly:

1. Open the **SQL Editor** and paste the contents of `schema.sql`, then click **Run**.
2. (Optional demo data) Paste `seed_data.sql` in a new query and click **Run**.

Or, from a machine with `psql` and the database connection string:

```bash
psql "postgresql://postgres.giojbgyqcpkuvkrnthou:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres" -f schema.sql
psql "postgresql://postgres.giojbgyqcpkuvkrnthou:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres" -f seed_data.sql
```

## 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-secret-key
```

`.env` is git-ignored — never commit it.

## Database features (`schema.sql`)

### Tables
- **farmers / buyers** — registered users, each with:
  - `user_id` (optional) linking to Supabase Auth.
  - **`aadhaar_hash`** — a one-way SHA-256 hash of the user's 12-digit Aadhaar. The raw Aadhaar
    number is **never stored or returned**; it is only used for login (see RPCs below).
- **listings** — produce for sale (crop, quantity, unit, price).
- **orders** — purchase orders with a status lifecycle (`pending → confirmed → delivered`, plus `cancelled` / `paid`).
- **payments, ratings, schemes, price_history** — payment tracking, buyer feedback, subsidy schemes, and market prices.
- **order_status_history** — audit trail of every order status change.
- **crops** — the crop advisor's agronomy knowledge base (12 crops).

### Trigger
- **`update_listing_after_order`** — on order insert, decrements the listing's quantity and auto-flags it `sold_out` when it reaches 0.

### RPC functions (call from the app via `supabase.rpc(...)`)
- **`recommend_crops`** — scores each crop against soil parameters (pH, moisture, N/P/K, temperature, season) and returns ranked matches with estimated revenue and market outlook.
- **`update_order_status`** — advances an order to a new status, enforcing valid transitions and writing to the audit trail.
- **`get_farmer_revenue`** — returns a farmer's total paid revenue.
- **`get_most_active_buyers`** — report: buyers with highest total order volume.
- **`get_farmer_ratings`** — report: average rating per farmer.
- **Aadhaar login (secure)** — `set_farmer_aadhaar`, `set_buyer_aadhaar` (register/hash on
  signup), and `aadhaar_farmer_login` / `aadhaar_buyer_login` (verify and return `id` + `name`
  only). The raw Aadhaar is never exposed.

### Reporting views
- `active_listings_view` — available produce with farmer details.
- `most_active_buyers_view`, `unsold_stock_view`, `farmer_avg_rating_view`, `pending_payments_view`.
- `inventory_view` — current stock per listing.
- `low_stock_view` — running-low alerts.
- `monthly_sales_summary_view` — orders / quantity / value per month.
- `order_history_view` — full order context (buyer/farmer/crop/value).
- `order_status_audit_view` — the order transition log.

### Auth & Row Level Security
- `farmers.user_id` / `buyers.user_id` link rows to Supabase Auth users.
- RLS policies restrict per-user access. These only apply when the anon/publishable key is used; the secret key bypasses them.

## UI requirements (for the Streamlit app)

The app must use a **farm/green glassmorphism** theme, and must surface every DB feature above.
A dedicated guide for the hosting/UI agent is in **`AGENTS.md`** (it is auto-read by coding
agents on every repo access). See it for the full feature checklist, the Aadhaar login flow, and
the known UI bugs to fix (theme-toggle glitch and left-panel nav layout).
