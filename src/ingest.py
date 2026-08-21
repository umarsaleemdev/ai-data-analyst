from pathlib import Path
from typing import Any
import pandas as pd


class DataIngestor:
    """Loads, cleans, and extracts summary statistics from tabular datasets."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.df: pd.DataFrame = pd.DataFrame()

    def load_and_clean(self) -> pd.DataFrame:
        """Reads CSV data, handles missing values, and derives essential columns."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found at: {self.file_path}")

        # 1. Load raw data
        self.df = pd.read_csv(self.file_path)

        # 2. Fill missing numerical values with median strategies
        for col in self.df.select_dtypes(include=["number"]).columns:
            if self.df[col].isnull().any():
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)

        # 3. Calculate derived business metrics if applicable
        if "units_sold" in self.df.columns and "unit_price" in self.df.columns:
            self.df["total_revenue"] = self.df["units_sold"] * self.df["unit_price"]

        return self.df

    def detect_outliers(self) -> dict[str, list[dict[str, Any]]]:
        """Uses the Interquartile Range (IQR) method to detect numeric anomalies."""
        if self.df.empty:
            self.load_and_clean()

        outliers: dict[str, list[dict[str, Any]]] = {}
        numeric_cols = self.df.select_dtypes(include=["number"]).columns

        for col in numeric_cols:
            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            # Filter rows outside the bounds
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outlier_rows = self.df[outlier_mask]

            if not outlier_rows.empty:
                id_col = "transaction_id" if "transaction_id" in self.df.columns else self.df.columns[0]
                outliers[col] = [
                    {
                        "id": str(row[id_col]),
                        "value": float(row[col]),
                        "lower_bound": round(float(lower_bound), 2),
                        "upper_bound": round(float(upper_bound), 2),
                    }
                    for _, row in outlier_rows.iterrows()
                ]

        return outliers

    def get_summary_statistics(self) -> dict[str, Any]:
        """Generates a structured dictionary of statistics for LLM consumption."""
        if self.df.empty:
            self.load_and_clean()

        total_rows = len(self.df)
        numeric_cols = self.df.select_dtypes(include=["number"]).columns.tolist()

        stats: dict[str, Any] = {
            "total_records": total_rows,
            "columns": list(self.df.columns),
            "numeric_summaries": {},
            "categorical_breakdowns": {},
            "detected_outliers": self.detect_outliers(),
        }

        for col in numeric_cols:
            stats["numeric_summaries"][col] = {
                "mean": round(float(self.df[col].mean()), 2),
                "std": round(float(self.df[col].std()), 2),
                "min": round(float(self.df[col].min()), 2),
                "max": round(float(self.df[col].max()), 2),
                "sum": round(float(self.df[col].sum()), 2),
            }

        categorical_cols = self.df.select_dtypes(include=["object"]).columns
        for col in categorical_cols:
            if col not in ["transaction_id", "date"]:
                stats["categorical_breakdowns"][col] = (
                    self.df[col].value_counts().to_dict()
                )

        return stats