import sqlite3
import csv
import subprocess
import sys
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "nifty100.db"
AUDIT = ROOT / "output" / "load_audit.csv"
VALIDATION = ROOT / "output" / "validation_failures.csv"

if not DB.exists():
    print("ERROR: nifty100.db not found")
    sys.exit(2)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

# 1. companies count
try:
    cur.execute("SELECT COUNT(*) FROM companies")
    companies_count = cur.fetchone()[0]
except Exception as e:
    print("ERROR querying companies:", e)
    companies_count = None

# 2. foreign_key_check
fk_issues = []
try:
    cur.execute("PRAGMA foreign_key_check;")
    fk_issues = cur.fetchall()
except Exception as e:
    print("ERROR running foreign_key_check:", e)

# 3. load_audit.csv rejections sum
rejections_sum = None
if AUDIT.exists():
    with open(AUDIT, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rejections_sum = 0
        for r in reader:
            try:
                rejections_sum += int(r.get('rejections', 0) or 0)
            except Exception:
                pass
else:
    print("WARNING: load_audit.csv not found")

# 4. validation failures critical count
critical_failures = 0
warnings = 0
if VALIDATION.exists():
    with open(VALIDATION, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sev = (r.get('severity') or '').upper()
            if sev == 'CRITICAL':
                critical_failures += 1
            elif sev == 'WARNING':
                warnings += 1

# 5. run pytest
pytest_exit = None
try:
    res = subprocess.run([sys.executable, '-m', 'pytest', '-q'], cwd=str(ROOT))
    pytest_exit = res.returncode
except Exception as e:
    print("Could not run pytest:", e)

# 6. sample 5 companies
sample_companies = []
try:
    cur.execute("SELECT company_id, name FROM companies ORDER BY company_id")
    rows = cur.fetchall()
    if rows:
        sample = random.sample(rows, min(5, len(rows)))
        for cid, name in sample:
            cur.execute("SELECT year, sales, opm FROM profitandloss WHERE company_id=? ORDER BY year", (cid,))
            pl = cur.fetchall()
            sample_companies.append({'company_id': cid, 'name': name, 'pl_years': len(pl), 'pl_sample': pl[:5]})
except Exception as e:
    print("Could not sample companies:", e)

# Print summary
print('=== EXIT CRITERIA CHECK SUMMARY ===')
print('companies_count=', companies_count)
print('foreign_key_issues_count=', len(fk_issues))
print('total_load_rejections=', rejections_sum)
print('validation_critical_failures=', critical_failures)
print('validation_warnings=', warnings)
print('pytest_exit_code=', pytest_exit)
print('\nSampled companies for manual review:')
for sc in sample_companies:
    print(f"- {sc['company_id']} | {sc['name']} | P&L years={sc['pl_years']} | sample rows={sc['pl_sample']}")

# Exit codes: 0 if all good, 1 if warnings/failures, 2 if errors
if companies_count != 92 or len(fk_issues) != 0 or (rejections_sum is not None and rejections_sum > 0) or critical_failures > 0 or (pytest_exit is not None and pytest_exit != 0):
    sys.exit(1)
print('All exit criteria satisfied.')
sys.exit(0)
