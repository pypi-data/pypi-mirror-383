from __future__ import annotations

import argparse
import os

import pandas as pd

from src.fppull.join_reports import join_roster_and_stats


def load_stats_offline(season: int, week: int) -> pd.DataFrame:
    # simple offline sample so we avoid network until we wire real parsing
    sample_path = f"data/samples/week_{season}_{week:02d}_stats.csv"
    if not os.path.exists(sample_path):
        raise FileNotFoundError(
            f"Offline sample not found: {sample_path}. Create it or run with real fetch later."
        )
    return pd.read_csv(sample_path)


def main():
    ap = argparse.ArgumentParser(
        description="Build week report (offline sample for now)."
    )
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--out", default="data/processed/week_report.csv")
    args = ap.parse_args()

    stats_df = load_stats_offline(args.season, args.week)
    joined = join_roster_and_stats(args.season, stats_df)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    joined.to_csv(args.out, index=False)
    print(f"✅ wrote {args.out} ({len(joined)} rows)")


if __name__ == "__main__":
    main()
