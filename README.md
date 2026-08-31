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

This creates the tables, the quantity-decrement trigger, the reporting views, and the revenue function.

## 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-service-role-key
```

`.env` is git-ignored — never commit it.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the app

```bash
streamlit run app.py
```

---

### If you need to grant the anon key access instead

The app works best with the service role key. If you would rather use the anon key, enable Row Level Security on each table and add policies, or temporarily disable RLS for the tables.
