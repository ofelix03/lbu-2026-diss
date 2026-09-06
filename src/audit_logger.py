import pandas as pd


def data_quality_audit(df):
    report = []
    for col in df.columns:
        col_data = df[col]
        n_miss = col_data.isna().sum()
        report.append(
            {
                "column": col,
                "dtype": str(col_data.dtype),
                "total": f"{len(col_data):>8,}",
                "n_missing": f"{n_miss:>8,}",
                "pct_missing": round(100 * n_miss / len(df), 2),
                "n_unique": col_data.nunique(),
                "min": col_data.min() if col_data.dtype != object else None,
                "max": col_data.max() if col_data.dtype != object else None,
                "example": (
                    col_data.dropna().iloc[0] if len(col_data.dropna()) else None
                ),
            }
        )
    report_df = pd.DataFrame(report).sort_values("pct_missing", ascending=False)
    return report_df
