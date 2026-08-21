from pathlib import Path
import pandas as pd
from advanced_analytics import load_data, recommend_funds


def main() -> None:
    fund_master, _, _, performance = load_data()
    risk_appetite = input("Enter risk appetite (Low / Moderate / High): ").strip()
    recommendations = recommend_funds(risk_appetite, fund_master, performance, top_n=3)
    print("\nTop 3 fund recommendations")
    print(recommendations[["scheme_name", "fund_house", "risk_category", "risk_grade", "sharpe_ratio", "return_3yr_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
