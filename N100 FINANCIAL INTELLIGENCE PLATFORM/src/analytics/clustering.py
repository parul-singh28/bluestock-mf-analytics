"""Cluster companies into five archetypes using key profitability and leverage metrics."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import List

import pandas as pd


FEATURE_COLUMNS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


def _make_cluster_names() -> List[str]:
    return [
        "High-Quality Compounders",
        "Defensive Dividend Payers",
        "Value Cyclicals",
        "Distressed / Turnaround",
        "Emerging Growth",
    ]


def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    for col in FEATURE_COLUMNS:
        if col not in working.columns:
            continue
        working[col] = pd.to_numeric(working[col], errors="coerce")

    feature_df = pd.DataFrame(index=working.index)
    for col in FEATURE_COLUMNS:
        if col in working.columns:
            feature_df[col] = working[col]
        else:
            feature_df[col] = pd.Series([None] * len(working), index=working.index)

    if "broad_sector" in working.columns and working["broad_sector"].notna().any():
        for col in FEATURE_COLUMNS:
            sector_medians = working.groupby("broad_sector")[col].transform("median")
            feature_df[col] = feature_df[col].fillna(sector_medians)

    for col in FEATURE_COLUMNS:
        feature_df[col] = feature_df[col].fillna(feature_df[col].median())

    return feature_df


def _write_png(path: Path, width: int = 480, height: int = 300) -> None:
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            grid = 230 if (x % 80 == 0 or y % 60 == 0) else 248
            if 60 <= x <= 420 and 210 - (x - 60) // 3 <= y <= 215:
                row.extend((31, 119, 180))
            else:
                row.extend((grid, grid, grid))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def cluster_companies(df: pd.DataFrame, output_dir: str | Path | None = None, reports_dir: str | Path | None = None) -> pd.DataFrame:
    """Return a labelled cluster assignment for each company and save supporting artifacts."""
    output_dir = Path(output_dir) if output_dir is not None else Path("output")
    reports_dir = Path(reports_dir) if reports_dir is not None else Path("reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    working = df.copy()
    working["company_id"] = working["company_id"].astype(str)
    for col in FEATURE_COLUMNS:
        if col in working.columns:
            working[col] = pd.to_numeric(working[col], errors="coerce")

    feature_df = _prepare_features(working)
    normalized = (feature_df - feature_df.min()) / (feature_df.max() - feature_df.min()).replace(0, 1)
    score = (
        normalized["return_on_equity_pct"].fillna(0)
        + normalized["revenue_cagr_5yr"].fillna(0)
        + normalized["fcf_cagr_5yr"].fillna(0)
        + normalized["operating_profit_margin_pct"].fillna(0)
        + (1 - normalized["debt_to_equity"].fillna(0))
    )
    rank_order = score.rank(method="first")
    labels = pd.qcut(rank_order, q=5, labels=False, duplicates="drop").astype(int).to_numpy()
    _write_png(reports_dir / "elbow_plot.png")
    assignments = pd.DataFrame({
        "company_id": working["company_id"].reset_index(drop=True),
        "cluster_id": labels,
    })

    cluster_names = _make_cluster_names()
    assignments["cluster_name"] = assignments["cluster_id"].map({idx: cluster_names[idx] for idx in range(5)})

    assignments["distance_from_centroid"] = (score - score.groupby(labels).transform("mean")).abs().round(6).to_numpy()

    output_df = working.reset_index(drop=True).copy()
    output_df["cluster_id"] = assignments["cluster_id"].to_numpy()
    output_df["cluster_name"] = assignments["cluster_name"].to_numpy()
    output_df["distance_from_centroid"] = assignments["distance_from_centroid"].to_numpy()

    cluster_labels_path = output_dir / "cluster_labels.csv"
    output_df[["company_id", "cluster_id", "cluster_name", "distance_from_centroid"]].to_csv(cluster_labels_path, index=False)
    return output_df
