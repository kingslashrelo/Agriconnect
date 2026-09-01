# Supabase Connection Details (for AgriConnect UI/hosting)

Use these to connect the Streamlit app (or any client) to the AgriConnect Supabase database.

## Required secrets (add as Streamlit Cloud secrets)

| Name           | Value                                              |
|----------------|----------------------------------------------------|
| `SUPABASE_URL` | `https://giojbgyqcpkuvkrnthou.supabase.co`         |
| `SUPABASE_KEY` | `sb_secret_mRUmqKk6Db-l4Sf-m5IBwA_jYyAntdO`        |

## Connecting from Python (supabase-py)

```python
from supabase import create_client

SUPABASE_URL = "https://giojbgyqcpkuvkrnthou.supabase.co"
SUPABASE_KEY = "sb_secret_mRUmqKk6Db-l4Sf-m5IBwA_jYyAntdO"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Example queries
farmers = supabase.from_("farmers").select("*").execute()
recos = supabase.rpc("recommend_crops", {
    "p_ph": 6.5, "p_moisture": 50,
    "p_n": 3.0, "p_p": 3.0, "p_k": 3.0,
    "p_temp": 28, "p_season": "Kharif",
}).execute()
```

## Direct database connection (psql / SQL clients)

Session pooler (recommended):

```
postgresql://postgres.giojbgyqcpkuvkrnthou:[DB-PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres
```

Direct:

```
postgresql://postgres:[DB-PASSWORD]@db.giojbgyqcpkuvkrnthou.supabase.co:5432/postgres
```

> The `[DB-PASSWORD]` is the database password, kept separately — not committed to the repo. Only the `SUPABASE_URL` / `SUPABASE_KEY` (API) are needed for app read/write access; the direct connection is only needed to run SQL (schema/seed/admin).

## Important notes

- Use `SUPABASE_KEY` (the secret key) for the app — it bypasses Row Level Security so all reads/writes work.
- The secret key must stay **server-side only** (Streamlit secrets / `.env`), never in the browser.
- If RLS / per-user auth is ever turned on, the app should switch to a user's access token instead of the shared secret key.

## Database contents

- Tables: `farmers`, `buyers`, `listings`, `orders`, `payments`, `ratings`, `schemes`, `price_history`, `order_status_history`, `crops`.
- RPC functions: `recommend_crops(...)`, `update_order_status(...)`, `get_farmer_revenue(...)`.
- Views: `active_listings_view`, `inventory_view`, `low_stock_view`, `monthly_sales_summary_view`, `order_history_view`, `order_status_audit_view`, `most_active_buyers_view`, `unsold_stock_view`, `farmer_avg_rating_view`, `pending_payments_view`.

See `schema.sql` for the full definition and `README.md` for setup steps.
