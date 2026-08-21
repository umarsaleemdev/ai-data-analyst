from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.analyzer import ExecutiveReport

console = Console()


class ReportGenerator:
    """Handles terminal rendering and Markdown exporting for executive reports."""

    def __init__(self, report: ExecutiveReport, output_dir: str = "reports"):
        self.report = report
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def display_terminal_dashboard(self) -> None:
        """Renders a styled Rich dashboard directly in the terminal."""
        console.print()

        # 1. Executive Summary Panel
        console.print(
            Panel(
                self.report.summary,
                title="[bold green]Executive Summary[/bold green]",
                border_style="green",
                expand=False,
            )
        )

        # 2. Key Insights Table
        insights_table = Table(
            title="[bold cyan]Key Business Insights[/bold cyan]",
            show_header=True,
            header_style="bold cyan",
        )
        insights_table.add_column("Topic", style="bold yellow", width=25)
        insights_table.add_column("Observation", width=45)
        insights_table.add_column("Business Impact", style="dim", width=35)

        for insight in self.report.key_insights:
            insights_table.add_row(
                insight.title, insight.observation, insight.business_impact
            )

        console.print(insights_table)

        # 3. Recommended Actions Panel
        actions_text = "\n".join(
            f"➜ {action}" for action in self.report.recommended_actions
        )
        console.print(
            Panel(
                actions_text,
                title="[bold magenta]Strategic Recommendations[/bold magenta]",
                border_style="magenta",
                expand=False,
            )
        )

    def export_markdown(self, filename: str = "executive_report.md") -> Path:
        """Exports the executive report to a structured Markdown file."""
        filepath = self.output_dir / filename

        md_content = f"# Executive Data Analysis Report\n\n"
        md_content += f"## Summary\n{self.report.summary}\n\n"

        md_content += f"## Key Insights\n"
        for insight in self.report.key_insights:
            md_content += f"### {insight.title}\n"
            md_content += f"- **Observation:** {insight.observation}\n"
            md_content += f"- **Impact:** {insight.business_impact}\n\n"

        md_content += f"## Recommended Actions\n"
        for action in self.report.recommended_actions:
            md_content += f"- {action}\n"

        filepath.write_text(md_content, encoding="utf-8")
        return filepath