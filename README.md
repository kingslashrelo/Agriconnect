# AgriConnect — Setup

AgriConnect now uses **Supabase** as its backend (REST/PostgREST via `supabase-py`). Neon is no longer used.

## 1. Create your Supabase project

1. Sign up / log in at [supabase.com](https://supabase.com).
2. Create a new project (free tier works). Note your **Project URL** (e.g. `https://xyzcompany.supabase.co`) and your **service_role key**.

> The service role key bypasses Row Level Security, so all tables read/write work out of the box. Because this app runs server-side inside Streamlit (the key lives only in `.env`, never exposed to the browser), this is safe for a learning project.

## 2. Create the database schema

1. Open **SQL Editor** in the Supabase dashboard.
2. Paste the contents of `schema.sql` into a new query and click **Run**.
3. (Optional, demo data) Paste `seed_data.sql` into a new query and click **Run**.

This creates the tables, the quantity-decrement trigger, the reporting views, and the revenue function, plus the backend feature set below.

### Backend features (in `schema.sql`)

- **Order lifecycle** — `order_status_history` table + `update_order_status()` RPC enforces valid transitions (`pending → confirmed → delivered`, with `cancelled` / `paid`) and records an audit trail. `order_history_view` gives full buyer/farmer context; `order_status_audit_view` shows the transitions.
- **Crop engine** — `crops` agronomy table + `recommend_crops()` RPC scores each crop (ph, moisture, N/P/K, temperature, season) and returns ranked matches with estimated revenue and market outlook.
- **Inventory & sales** — `inventory_view` (current stock), `low_stock_view` (running-low alerts), and `monthly_sales_summary_view` (orders / quantity / value per month).
- **Revenue** — `get_farmer_revenue()` RPC returns a farmer's total paid revenue.
- **Auth & RLS** — `farmers.user_id` / `buyers.user_id` link rows to Supabase Auth users; RLS policies restrict access. The app runs on the secret key (bypasses RLS), so these matter only if you switch to anon/publishable keys.

## 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-secret-key
```

- `SUPABASE_URL` — your Project URL (Settings → API).
- `SUPABASE_KEY` — use your **secret key** (the new `sb_secret_...` key replaces the old `service_role` key). This key bypasses Row Level Security so all tables work out of the box. Because the app runs server-side inside Streamlit (the key lives only in `.env` / Streamlit secrets, never the browser), this is safe for a learning project.
- For a locally-hosted Supabase that still shows legacy keys, the old `service_role` key also works here.

`.env` is git-ignored — never commit it.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the app

```bash
streamlit run app.py
```

## Features

- **Crop Advisor** — enter soil parameters (pH, moisture, N/P/K, temperature, season) and get recommended crops with estimated revenue and market outlook from a built-in agronomy knowledge base.
- Farmer / buyer registration with input validation.
- Produce listings with automatic stock tracking (trigger decrements quantity on order).
- Order placement, active listings board, and analytics reports.

---

### If you need to grant the anon key access instead

The app works best with a secret / service role key. If you would rather use the anon/publishable key, enable Row Level Security on each table and add policies, or temporarily disable RLS for the tables.
