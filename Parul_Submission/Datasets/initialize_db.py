from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
SCHEMA_PATH = Path(__file__).resolve().with_name("schema.sql")

if DB_PATH.exists():
    DB_PATH.unlink()

print(f"Connecting and initializing database: {DB_PATH}...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"Reading database blueprints from {SCHEMA_PATH}...")
with SCHEMA_PATH.open("r", encoding="utf-8") as sql_file:
    sql_script = sql_file.read()

print("Executing SQL blueprints to set up empty tables...")
cursor.executescript(sql_script)

conn.commit()
conn.close()

print(f"🎉 Success! Your layout is ready. '{DB_PATH.name}' has been created.")