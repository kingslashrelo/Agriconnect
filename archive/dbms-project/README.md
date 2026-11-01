# AgriConnect — Setup

1. Create a project at [neon.tech](https://neon.tech) (free, no card) and copy the connection string.
2. `cp .env.example .env` and paste your connection string in as `NEON_DATABASE_URL`.
3. `pip install -r requirements.txt`
4. `python run_sql_file.py schema.sql`
5. `python run_sql_file.py seed_data.sql` (optional — loads demo data)
6. `streamlit run app.py`

`.env` is git-ignored — never commit it.
