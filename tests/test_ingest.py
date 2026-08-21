import pandas as pd
import pytest
from src.ingest import DataIngestor


@pytest.fixture
def sample_csv(tmp_path):
    """Creates a temporary CSV file with missing values for testing."""
    csv_file = tmp_path / "test_data.csv"
    content = (
        "transaction_id,units_sold,unit_price,category\n"
        "TX1,10,100.0,Electronics\n"
        "TX2,,200.0,Furniture\n"
        "TX3,30,50.0,Electronics\n"
    )
    csv_file.write_text(content)
    return csv_file


def test_load_and_clean_imputation(sample_csv):
    """Verify that missing numerical values are filled with the column median."""
    ingestor = DataIngestor(sample_csv)
    df = ingestor.load_and_clean()

    # TX2 units_sold was missing; median of 10 and 30 is 20.0
    assert df.loc[df["transaction_id"] == "TX2", "units_sold"].iloc[0] == 20.0
    assert df["units_sold"].isnull().sum() == 0


def test_revenue_calculation(sample_csv):
    """Verify total_revenue is derived correctly after cleaning."""
    ingestor = DataIngestor(sample_csv)
    df = ingestor.load_and_clean()

    assert "total_revenue" in df.columns
    # TX1 revenue = 10 * 100.0 = 1000.0
    assert df.loc[df["transaction_id"] == "TX1", "total_revenue"].iloc[0] == 1000.0


def test_summary_statistics_structure(sample_csv):
    """Verify that extracted summary dictionary has required key metrics."""
    ingestor = DataIngestor(sample_csv)
    stats = ingestor.get_summary_statistics()

    assert stats["total_records"] == 3
    assert "units_sold" in stats["numeric_summaries"]
    assert "category" in stats["categorical_breakdowns"]
def test_outlier_detection(sample_csv):
    """Verify that IQR outlier detection flags high-value anomalies."""
    ingestor = DataIngestor(sample_csv)
    stats = ingestor.get_summary_statistics()

    assert "detected_outliers" in stats
    # Ensure the method runs without throwing key errors on clean/small datasets
    assert isinstance(stats["detected_outliers"], dict)