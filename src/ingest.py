"""
src/ingest.py
Handles data loading (CSV & Excel), statistical aggregation, and IQR outlier detection.
"""

from pathlib import Path
from typing import Any, cast
import pandas as pd


class DataIngestor:
    """Handles multi-format data ingestion and statistical summarization."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def load_data(self) -> pd.DataFrame:
        """Loads CSV or Excel datasets cleanly into a Pandas DataFrame."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found at: {self.file_path}")

        extension = self.file_path.suffix.lower()

        if extension == ".csv":
            return pd.read_csv(self.file_path)
        elif extension in [".xlsx", ".xls"]:
            return pd.read_excel(self.file_path, engine="openpyxl")
        else:
            raise ValueError(
                f"Unsupported file format '{extension}'. Only .csv and .xlsx files are supported."
            )

    def calculate_iqr_outliers(
        self, df: pd.DataFrame, numeric_cols: list[str]
    ) -> dict[str, Any]:
        """Identifies numerical outliers using the 1.5 * IQR rule."""
        outlier_summary: dict[str, Any] = {}

        for col in numeric_cols:
            clean_col = df[col].dropna()
            if clean_col.empty:
                continue

            q1 = float(cast(float, clean_col.quantile(0.25)))
            q3 = float(cast(float, clean_col.quantile(0.75)))
            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            if not outliers.empty:
                sample_values = [
                    round(float(v), 2) for v in outliers[col].head(5).tolist()
                ]
                outlier_summary[col] = {
                    "count": len(outliers),
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                    "sample_outlier_values": sample_values,
                }

        return outlier_summary

    # RENAMED to match what cli.py is calling
    def get_summary_statistics(self) -> dict[str, Any]:
        """
        Ingests dataset, cleans nulls, computes distributions, and generates
        a statistical summary payload for the LLM.
        """
        df = self.load_data()

        total_rows, total_cols = df.shape

        numeric_cols = [str(c) for c in df.select_dtypes(include=["number"]).columns]
        categorical_cols = [
            str(c) for c in df.select_dtypes(include=["object", "category"]).columns
        ]

        numeric_stats: dict[str, Any] = {}
        for col in numeric_cols:
            s = df[col].dropna()
            if s.empty:
                continue

            mean_val = float(cast(float, s.mean()))
            std_val = float(cast(float, s.std())) if len(s) > 1 else 0.0
            min_val = float(cast(float, s.min()))
            median_val = float(cast(float, s.median()))
            max_val = float(cast(float, s.max()))

            numeric_stats[col] = {
                "mean": round(mean_val, 2),
                "std": round(std_val, 2),
                "min": round(min_val, 2),
                "median": round(median_val, 2),
                "max": round(max_val, 2),
                "null_count": int(df[col].isnull().sum()),
            }

        categorical_stats: dict[str, Any] = {}
        for col in categorical_cols:
            top_counts = df[col].value_counts().head(3).to_dict()
            categorical_stats[col] = {
                "unique_values": int(df[col].nunique()),
                "top_frequencies": {str(k): int(v) for k, v in top_counts.items()},
                "null_count": int(df[col].isnull().sum()),
            }

        outliers = self.calculate_iqr_outliers(df, numeric_cols)

        return {
            "dataset_metadata": {
                "file_name": self.file_path.name,
                "total_rows": total_rows,
                "total_columns": total_cols,
            },
            "numeric_statistics": numeric_stats,
            "categorical_statistics": categorical_stats,
            "detected_outliers": outliers,
        }