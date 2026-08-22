"""
src/reporter.py
Renders Rich terminal dashboards and exports Markdown reports matching ExecutiveReport schema.
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.analyzer import ExecutiveReport

console = Console()


class ReportGenerator:
    """Handles terminal visual rendering and file exports for analysis reports."""

    def __init__(self, report: ExecutiveReport):
        self.report = report

    def display_terminal_dashboard(self) -> None:
        """Renders formatted Rich panels and tables to stdout."""
        # 1. Executive Summary Panel
        summary_panel = Panel(
            self.report.summary,
            title="[bold blue]Executive Summary[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(summary_panel)
        console.print()

        # 2. Key Insights Table
        table = Table(
            title="Key Business Insights",
            header_style="bold magenta",
            show_lines=True,
        )
        table.add_column("Title", style="cyan", width=25)
        table.add_column("Observation", width=45)
        table.add_column("Business Impact", width=35)

        for insight in self.report.key_insights:
            table.add_row(
                insight.title,
                insight.observation,
                insight.business_impact,
            )

        console.print(table)
        console.print()

        # 3. Data Anomalies Table (if present)
        if self.report.anomalies:
            anomaly_table = Table(
                title="Detected Data Anomalies",
                header_style="bold yellow",
                show_lines=True,
            )
            anomaly_table.add_column("Metric", style="yellow", width=20)
            anomaly_table.add_column("Finding", width=55)
            anomaly_table.add_column("Risk Level", width=15)

            for anomaly in self.report.anomalies:
                anomaly_table.add_row(
                    anomaly.metric,
                    anomaly.finding,
                    anomaly.risk_level,
                )

            console.print(anomaly_table)
            console.print()

        # 4. Strategic Recommendations Panel
        recs_text = "\n".join(
            [f"➜ {rec}" for rec in self.report.recommended_actions]
        )
        recs_panel = Panel(
            recs_text,
            title="[bold green]Strategic Recommended Actions[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(recs_panel)

    # Alias to keep both method signatures compatible
    display_terminal_report = display_terminal_dashboard

    def to_markdown(self) -> str:
        """Converts ExecutiveReport into a clean Markdown string."""
        lines = [
            "# AI Data Analysis Report\n",
            "## Executive Summary",
            f"{self.report.summary}\n",
            "## Key Business Insights\n",
            "| Title | Observation | Business Impact |",
            "| :--- | :--- | :--- |",
        ]

        for insight in self.report.key_insights:
            lines.append(
                f"| {insight.title} | {insight.observation} | {insight.business_impact} |"
            )

        if self.report.anomalies:
            lines.extend(
                [
                    "\n## Detected Data Anomalies\n",
                    "| Metric | Finding | Risk Level |",
                    "| :--- | :--- | :--- |",
                ]
            )
            for anomaly in self.report.anomalies:
                lines.append(
                    f"| {anomaly.metric} | {anomaly.finding} | {anomaly.risk_level} |"
                )

        lines.extend(
            [
                "\n## Recommended Actions",
                *(f"- {action}" for action in self.report.recommended_actions),
            ]
        )

        return "\n".join(lines)

    def export_markdown(self, output_path: str | Path) -> Path:
        """Saves the Markdown report to disk, creating parent directories if needed."""
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        markdown_content = self.to_markdown()
        target_path.write_text(markdown_content, encoding="utf-8")

        return target_path