from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import get_companies, get_ratios, get_sectors

REPORT_ROOT = PROJECT_ROOT / "reports" / "sector"


def build_sector_report(sector: str, output_dir: str | Path = REPORT_ROOT) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    companies = get_companies()
    subset = companies[companies["broad_sector"] == sector]
    rows = [["Company", "Ticker", "ROE", "P/E", "P/B", "FCF", "D/E", "Score", "Pattern"]]
    for _, company in subset.iterrows():
        latest = get_ratios(company["ticker"], 2024).iloc[0]
        rows.append([company["name"], company["ticker"], f"{latest['roe']*100:.1f}%", f"{latest['pe_ratio']:.1f}", f"{latest['pb_ratio']:.1f}", f"{latest['fcf']:.0f}", f"{latest['debt_to_equity']:.2f}", f"{latest['composite_score']:.1f}", company["capital_pattern"]])
    pdf_path = output_path / f"{sector.replace(' ', '_')}_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    story = [Paragraph(f"<b>{sector} Sector Report</b>", styles["Title"]), Spacer(1, 12)]
    table = Table(rows, repeatRows=1, colWidths=[1.15 * inch, 0.8 * inch, 0.55 * inch, 0.55 * inch, 0.55 * inch, 0.75 * inch, 0.55 * inch, 0.65 * inch, 1.2 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B1F3A")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey), ("FONTSIZE", (0, 0), (-1, -1), 7), ("WORDWRAP", (0, 0), (-1, -1), "CJK")]))
    story.append(table)
    doc.build(story)
    return pdf_path


def build_all_sector_reports(output_dir: str | Path = REPORT_ROOT) -> list[Path]:
    return [build_sector_report(sector, output_dir) for sector in get_sectors()["sector"].tolist()]


if __name__ == "__main__":
    result = build_all_sector_reports()
    print(f"Wrote {len(result)} sector reports.")
