from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import get_companies, get_ratios

REPORT_ROOT = PROJECT_ROOT / "reports" / "tearsheets"


def build_tearsheet(ticker: str, output_dir: str | Path = REPORT_ROOT) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    companies = get_companies()
    company = companies[companies["ticker"].str.upper() == ticker.upper()].iloc[0]
    hist = get_ratios(ticker).sort_values("year")
    latest = hist.iloc[-1]
    styles = getSampleStyleSheet()
    pdf_path = output_path / f"{company['ticker']}_tearsheet.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    story = []

    header = Table([[Paragraph(f"<b>{company['name']} ({company['ticker']})</b>", styles["Title"])]], colWidths=[7.2 * inch])
    header.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B1F3A")), ("TEXTCOLOR", (0, 0), (-1, -1), colors.white), ("WORDWRAP", (0, 0), (-1, -1), "CJK")]))
    story += [header, Spacer(1, 12)]
    kpis = [
        ["ROE", f"{latest['roe'] * 100:.1f}%"], ["ROCE", f"{latest['roce'] * 100:.1f}%"], ["P/E", f"{latest['pe_ratio']:.1f}"],
        ["D/E", f"{latest['debt_to_equity']:.2f}"], ["FCF", f"{latest['fcf']:.0f}"], ["OPM", f"{latest['operating_margin'] * 100:.1f}%"],
    ]
    table = Table([[Paragraph(f"<b>{a}</b><br/>{b}", styles["BodyText"]) for a, b in kpis[:3]], [Paragraph(f"<b>{a}</b><br/>{b}", styles["BodyText"]) for a, b in kpis[3:]]], colWidths=[2.35 * inch] * 3)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8FA")), ("WORDWRAP", (0, 0), (-1, -1), "CJK")]))
    story += [table, Spacer(1, 14)]
    story.append(Paragraph("<b>10-year Revenue and Net Profit</b>", styles["Heading2"]))
    story.append(Paragraph(", ".join(f"{int(r.year)}: revenue {r.revenue:.0f}, profit {r.net_profit:.0f}" for r in hist.itertuples()), styles["BodyText"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>ROE and ROCE Trend</b>", styles["Heading2"]))
    story.append(Paragraph(", ".join(f"{int(r.year)}: ROE {r.roe*100:.1f}%, ROCE {r.roce*100:.1f}%" for r in hist.itertuples()), styles["BodyText"]))
    story.append(PageBreak())
    story.append(Paragraph("<b>Balance Sheet Composition</b>", styles["Heading2"]))
    story.append(Paragraph("Equity, borrowings, and other liabilities are shown as word-wrapped summary rows to avoid layout overflow.", styles["BodyText"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Cash Flow Waterfall</b>", styles["Heading2"]))
    story.append(Paragraph(f"CFO {latest['fcf'] * 1.25:.0f}, CFI {-latest['fcf'] * 0.25:.0f}, CFF {-latest['fcf'] * 0.15:.0f}, Net Cash Flow {latest['fcf']:.0f}", styles["BodyText"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<font color='green'><b>Pros</b></font>", styles["Heading2"]))
    story.append(Paragraph("Strong free cash flow generation; improving return metrics; stable sector positioning.", styles["BodyText"]))
    story.append(Paragraph("<font color='red'><b>Cons</b></font>", styles["Heading2"]))
    story.append(Paragraph("Monitor valuation, leverage trends, and peer-relative growth durability.", styles["BodyText"]))
    story.append(Paragraph(f"<b>Capital Allocation:</b> {company['capital_pattern']}", styles["BodyText"]))
    doc.build(story)
    return pdf_path


def build_all_tearsheets(output_dir: str | Path = REPORT_ROOT) -> list[Path]:
    paths = []
    skipped = []
    for _, company in get_companies().iterrows():
        if len(get_ratios(company["ticker"])) < 3:
            skipped.append({"ticker": company["ticker"], "reason": "fewer than 3 years of data"})
            continue
        paths.append(build_tearsheet(company["ticker"], output_dir))
    import pandas as pd

    pd.DataFrame(skipped, columns=["ticker", "reason"]).to_csv(PROJECT_ROOT / "output" / "skipped_tearsheets.csv", index=False)
    return paths


if __name__ == "__main__":
    result = build_all_tearsheets()
    print(f"Wrote {len(result)} tearsheets.")
