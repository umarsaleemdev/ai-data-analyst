from pathlib import Path
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.analyzer import DataAnalyzer
from src.ingest import DataIngestor
from src.reporter import ReportGenerator

# no_args_is_help=True shows help automatically if user runs `python main.py` without args
app = typer.Typer(
    help="AI-Powered CLI Data Analyst - Ingest, inspect, and analyze tabular data.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def analyze(
    file_path: Path = typer.Argument(
        ..., help="Path to the tabular dataset (CSV) to analyze."
    ),
    output: str = typer.Option(
        "sales_analysis.md",
        "--output",
        "-o",
        help="Filename for the exported Markdown report.",
    ),
) -> None:
    """Runs full ingestion, Gemini AI statistical analysis, and renders/exports report."""
    load_dotenv()

    if not file_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Target dataset '{file_path}' does not exist."
        )
        raise typer.Exit(code=1)

    try:
        with console.status(
            "[bold yellow]Processing dataset & querying AI...[/bold yellow]"
        ):
            ingestor = DataIngestor(file_path)
            stats = ingestor.get_summary_statistics()

            analyzer = DataAnalyzer()
            report = analyzer.analyze(stats)

        reporter = ReportGenerator(report)
        reporter.display_terminal_dashboard()

        saved_path = reporter.export_markdown(output)
        console.print(
            f"\n[bold green]✓ Report saved to:[/bold green] {saved_path}"
        )

    except Exception as e:
        console.print(f"[bold red]Pipeline Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def inspect(
    file_path: Path = typer.Argument(
        ..., help="Path to the tabular dataset (CSV) to inspect."
    )
) -> None:
    """Quick dry-run: Displays clean summary statistics & detected outliers without making API calls."""
    if not file_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Target dataset '{file_path}' does not exist."
        )
        raise typer.Exit(code=1)

    ingestor = DataIngestor(file_path)
    stats = ingestor.get_summary_statistics()

    console.print(
        Panel(
            f"Records: [bold cyan]{stats['total_records']}[/bold cyan] | Columns: [bold cyan]{len(stats['columns'])}[/bold cyan]",
            title="[bold green]Dataset Quick Inspection[/bold green]",
            expand=False,
        )
    )

    # Print numeric metrics table
    table = Table(title="Numeric Columns Overview", header_style="bold yellow")
    table.add_column("Column")
    table.add_column("Mean")
    table.add_column("Min")
    table.add_column("Max")
    table.add_column("Total Sum")

    for col, metrics in stats["numeric_summaries"].items():
        table.add_row(
            col,
            str(metrics["mean"]),
            str(metrics["min"]),
            str(metrics["max"]),
            str(metrics["sum"]),
        )

    console.print(table)

    # Print flagged IQR outliers if any
    if stats["detected_outliers"]:
        console.print("\n[bold red]Detected IQR Outliers:[/bold red]")
        for col, items in stats["detected_outliers"].items():
            for item in items:
                console.print(
                    f"  • [yellow]{col}[/yellow] (ID: {item['id']}): Value [bold red]{item['value']}[/bold red] "
                    f"exceeds upper bound ({item['upper_bound']})"
                )
    else:
        console.print("\n[bold green]✓ No severe statistical outliers detected.[/bold green]")


@app.command()
def version() -> None:
    """Displays the CLI version."""
    console.print("[bold cyan]AI Data Analyst CLI v1.0.0[/bold cyan]")