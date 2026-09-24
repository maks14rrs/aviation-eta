from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/raw/opensky/extracted")


def analyze_file(file: Path):
    print(f"\n{'=' * 70}")
    print(f"FILE: {file.name}")
    print(f"{'=' * 70}")

    df = pd.read_csv(file)

    df["datetime"] = pd.to_datetime(
        df["time"],
        unit="s",
        utc=True,
    )

    print(f"Shape: {df.shape}")

    print("\nTime range:")
    print(
        df["datetime"].agg(["min", "max"])
    )

    print(f"\nUnique aircraft: {df['icao24'].nunique()}")

    print("\nMissing values:")
    print(df.isna().sum())

    # Только записи с основными параметрами движения
    trajectory_df = df.dropna(
        subset=[
            "lat",
            "lon",
            "velocity",
            "heading",
            "baroaltitude",
        ]
    )

    # Только самолёты в воздухе
    trajectory_df = trajectory_df[
        trajectory_df["onground"] == False
    ]

    # Сортируем траектории по времени
    trajectory_df = trajectory_df.sort_values(
        ["icao24", "datetime"]
    )

    # Интервалы между соседними точками
    trajectory_df["dt_seconds"] = (
        trajectory_df.groupby("icao24")["datetime"]
        .diff()
        .dt.total_seconds()
    )

    gaps = trajectory_df["dt_seconds"].dropna()

    print("\nTrajectory data:")
    print(f"Usable points: {len(trajectory_df)}")
    print(f"Aircraft: {trajectory_df['icao24'].nunique()}")

    if not gaps.empty:
        print("\nTime gap statistics:")
        print(gaps.describe())

        print("\nMost common gaps:")
        print(
            gaps.round()
            .value_counts()
            .sort_index()
            .head(10)
        )

        print(f"\nGaps > 30 sec: {(gaps > 30).sum()}")
        print(f"Gaps > 60 sec: {(gaps > 60).sum()}")

    points = trajectory_df.groupby("icao24").size()

    print("\nAircraft with enough points:")
    print(f">= 100: {(points >= 100).sum()}")
    print(f">= 200: {(points >= 200).sum()}")
    print(f">= 300: {(points >= 300).sum()}")

        # Непрерывные участки траекторий.
    # Новый участок начинается после разрыва больше 20 секунд.
    trajectory_df["segment"] = (
        trajectory_df["dt_seconds"]
        .gt(20)
        .groupby(trajectory_df["icao24"])
        .cumsum()
    )

    segments = (
        trajectory_df
        .groupby(["icao24", "segment"])
        .size()
    )

    print("\nContinuous trajectory segments:")
    print(f"Segments: {len(segments):,}")

    print("\nSegment length statistics:")
    print(segments.describe())

    print("\nSegments with enough points:")
    print(f">= 60 points  (10 min): {(segments >= 60).sum():,}")
    print(f">= 120 points (20 min): {(segments >= 120).sum():,}")
    print(f">= 180 points (30 min): {(segments >= 180).sum():,}")
    print(f">= 300 points (50 min): {(segments >= 300).sum():,}")
    
    return {
        "file": file.name,
        "rows": len(df),
        "aircraft": df["icao24"].nunique(),
        "usable_points": len(trajectory_df),
        "aircraft_100": (points >= 100).sum(),
        "aircraft_200": (points >= 200).sum(),
        "aircraft_300": (points >= 300).sum(),
    }


def main():
    files = sorted(DATA_DIR.glob("states_*.csv"))

    print(f"Found {len(files)} CSV files.")

    if not files:
        print("No OpenSky CSV files found.")
        return

    results = []

    for file in files:
        results.append(analyze_file(file))

    summary = pd.DataFrame(results)

    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    print(summary.to_string(index=False))

    print("\nTOTAL:")
    print(f"Rows: {summary['rows'].sum():,}")
    print(f"Usable points: {summary['usable_points'].sum():,}")


if __name__ == "__main__":
    main()