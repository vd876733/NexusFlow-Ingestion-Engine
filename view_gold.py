import glob
import os

import pandas as pd


GOLD_PATH = "lakehouse/gold/hourly_user_engagement"


def main():
    parquet_files = glob.glob(os.path.join(GOLD_PATH, "**", "*.parquet"), recursive=True)

    if not parquet_files:
        print("[ERROR] Gold layer records are missing. Please run gold_metrics.py first.")
        return

    print("=" * 80)
    print("NexusFlow Gold Layer Summary")
    print("=" * 80)

    frames = [pd.read_parquet(file) for file in parquet_files]
    df = pd.concat(frames, ignore_index=True)

    df = df.sort_values(by=["date", "hour"], ascending=[True, True]).reset_index(drop=True)

    total_events = int(df["total_events"].sum())
    peak_unique_users = int(df["unique_users"].max())

    print(f"Total Event Throughput: {total_events}")
    print(f"Peak Unique Active Users: {peak_unique_users}")
    print("-" * 80)
    print(df.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
