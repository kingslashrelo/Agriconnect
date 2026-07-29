"""Run a .sql file against the Neon database. No psql install needed.

Usage:
    python run_sql_file.py schema.sql
    python run_sql_file.py seed_data.sql
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def run_file(path: str) -> None:
    with open(path, "r") as f:
        sql = f.read()

    with psycopg2.connect(os.environ["NEON_DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

    print(f"Ran {path} successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_sql_file.py <path/to/file.sql>")
        sys.exit(1)
    run_file(sys.argv[1])
