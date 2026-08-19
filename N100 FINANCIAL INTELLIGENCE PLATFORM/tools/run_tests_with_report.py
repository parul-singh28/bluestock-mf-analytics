"""Run pytest and always write reports/pytest_report.html."""
from __future__ import annotations

import html
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "pytest_report.html"


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout or ""
    status = "PASSED" if completed.returncode == 0 else "FAILED"
    REPORT.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html><head><meta charset=\"utf-8\"><title>Pytest Report</title>",
                "<style>body{font-family:Arial,sans-serif;margin:32px;}pre{background:#f6f8fa;padding:16px;white-space:pre-wrap;} .passed{color:#16703a}.failed{color:#b42318}</style>",
                "</head><body>",
                "<h1>Pytest Report</h1>",
                f"<p>Status: <strong class=\"{status.lower()}\">{status}</strong></p>",
                f"<p>Generated: {html.escape(datetime.now().isoformat(timespec='seconds'))}</p>",
                f"<pre>{html.escape(output)}</pre>",
                "</body></html>",
            ]
        ),
        encoding="utf-8",
    )
    print(output, end="")
    print(f"\nWrote {REPORT.relative_to(ROOT)}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
