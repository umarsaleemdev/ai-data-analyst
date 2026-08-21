# AI-Powered CLI Data Analyst

A production-grade Python CLI application that ingests tabular datasets (CSVs), performs deterministic data cleaning and statistical extraction with Pandas, enforces structured analytical output via Gemini API & Pydantic, and renders rich terminal dashboards and Markdown reports.

---

## Key Features

- **Deterministic Data Engine**: Reads raw CSVs, handles missing value imputation, derives custom metrics, and calculates statistical summaries using Pandas.
- **IQR Outlier Detection**: Automatically flags numeric anomalies using the Interquartile Range method before LLM processing.
- **Structured AI Insights**: Enforces strict JSON schemas using Pydantic and `gemini-3.6-flash` for deterministic, schema-validated report generation.
- **Rich Terminal UI**: Renders styled tables, colored callout panels, and spinners directly in your terminal with `rich`.
- **Markdown Exporter**: Generates structured, executive-ready `.md` files for stakeholder distribution.
- **Tested & Robust**: Includes `pytest` test suites verifying data cleaning, statistics, and outlier detection logic.

---

## Tech Stack

- **CLI Framework**: `typer`
- **Data Engine**: `pandas`
- **AI Orchestration**: `google-genai` (`gemini-3.6-flash`)
- **Schema Validation**: `pydantic`
- **Terminal UI**: `rich`
- **Testing**: `pytest`

---

## Project Architecture

```
ai-data-analyst/
├── data/
│   └── sales_data.csv       # Sample dataset
├── reports/                 # Generated Markdown outputs
├── src/
│   ├── analyzer.py          # Gemini API orchestration & Pydantic schemas
│   ├── cli.py               # Typer CLI subcommand handlers
│   ├── ingest.py            # Pandas data cleaning, statistics & IQR outliers
│   └── reporter.py          # Rich terminal dashboard & Markdown exporter
├── tests/
│   └── test_ingest.py       # Pytest suite for data ingestion
├── .env                     # API key configuration
├── main.py                  # CLI entry point
├── README.md
└── requirements.txt
```

---

## Usage

### 1. Inspect Dataset (Dry-Run / Free)
Preview summary statistics and detected IQR outliers instantly without making LLM API calls:

```powershell
python main.py inspect data/sales_data.csv
```

### 2. Run Full AI Analysis
Execute data ingestion, statistical extraction, Gemini analysis, and report generation:

```powershell
python main.py analyze data/sales_data.csv --output executive_report.md
```

### 3. Check CLI Version

```powershell
python main.py version
```

---

## Running Unit Tests

Execute the `pytest` suite to verify data cleaning and statistical logic:

```powershell
pytest
```