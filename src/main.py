"""Main entry point for Interview Agent."""

import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.agents.core_processor import CoreProcessorAgent
from src.exporters.exporter import Exporter
from src.handlers.input_handler import InputHandler
from src.models.schema import ProcessingResult
from src.utils.config import Config
from src.utils.llm_client import SiliconFlowClient


console = Console()


class InterviewAgent:
    """Main Interview Agent orchestrator."""

    def __init__(self, config: Config):
        """Initialize the agent.

        Args:
            config: Application configuration
        """
        self.config = config
        self.config.ensure_directories()

        # Initialize components
        self.client = SiliconFlowClient(config)
        self.input_handler = InputHandler(self.client)
        self.core_processor = CoreProcessorAgent(self.client)
        self.exporter = Exporter(config.output_dir)

    def process(
        self,
        input_data: str,
        generate_answers: bool = False,
        export_format: str = "both",
        output_filename: Optional[str] = None,
    ) -> ProcessingResult:
        """Process interview experience input.

        Args:
            input_data: Input string (text or image path)
            generate_answers: Whether to generate missing answers
            export_format: Export format ("json", "markdown", or "both")
            output_filename: Optional custom output filename

        Returns:
            ProcessingResult object
        """
        start_time = time.time()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                # Step 1: Input handling
                task1 = progress.add_task("[cyan]Processing input...", total=None)
                text_content, source_type = self.input_handler.process_input(input_data)
                progress.update(task1, completed=True)

                # Step 2: Core processing
                task2 = progress.add_task("[cyan]Analyzing content...", total=None)
                experience = self.core_processor.process(text_content, source_type)
                progress.update(task2, completed=True)

                # Step 3: Export
                task3 = progress.add_task("[cyan]Exporting results...", total=None)
                exported_files = []

                if export_format in ["json", "both"]:
                    json_path = self.exporter.export_json(experience, output_filename)
                    exported_files.append(str(json_path))

                if export_format in ["markdown", "both"]:
                    md_path = self.exporter.export_markdown(experience, output_filename)
                    exported_files.append(str(md_path))

                progress.update(task3, completed=True)

            processing_time = time.time() - start_time

            # Display success message
            self._display_success(experience, exported_files, processing_time)

            return ProcessingResult(
                success=True,
                experience=experience,
                output_files=exported_files,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return ProcessingResult(
                success=False, error=str(e), processing_time=processing_time
            )

    def _display_success(
        self, experience, exported_files: list, processing_time: float
    ) -> None:
        """Display success message with results summary.

        Args:
            experience: InterviewExperience object
            exported_files: List of exported file paths
            processing_time: Processing time in seconds
        """
        console.print("\n[bold green]Processing completed successfully![/bold green]\n")

        # Summary panel
        summary_lines = []
        if experience.company_name:
            summary_lines.append(f"Company: {experience.company_name}")
        if experience.position:
            summary_lines.append(f"Position: {experience.position}")
        if experience.interview_stage:
            summary_lines.append(f"Stage: {experience.interview_stage}")

        summary_lines.append(f"Questions extracted: {len(experience.questions)}")
        summary_lines.append(f"Tags: {', '.join(experience.tags)}")
        summary_lines.append(f"Processing time: {processing_time:.2f}s")

        console.print(Panel("\n".join(summary_lines), title="Summary", border_style="green"))

        # Exported files
        console.print("\n[bold]Exported files:[/bold]")
        for filepath in exported_files:
            console.print(f"  - {filepath}")


def main() -> None:
    """Main function."""
    console.print(
        Panel.fit(
            "[bold cyan]Interview Agent[/bold cyan]\n"
            "AI-powered interview experience processor",
            border_style="cyan",
        )
    )

    # Load configuration
    try:
        config = Config.from_env()
    except Exception as e:
        console.print(f"[bold red]Configuration error:[/bold red] {str(e)}")
        console.print("\nPlease create a .env file with your configuration.")
        console.print("See .env.example for reference.")
        return

    # Validate API key
    if not config.siliconflow_api_key or config.siliconflow_api_key == "your_api_key_here":
        console.print(
            "[bold red]Error:[/bold red] SILICONFLOW_API_KEY not set in .env file"
        )
        return

    # Initialize agent
    agent = InterviewAgent(config)

    # Interactive mode
    console.print("\n[bold]Input options:[/bold]")
    console.print("1. Paste text content directly")
    console.print("2. Provide path to an image file")
    console.print()

    input_data = console.input("[cyan]Enter your input:[/cyan] ").strip()

    if not input_data:
        console.print("[yellow]No input provided.[/yellow]")
        return

    # Ask if user wants to generate missing answers
    generate_answers_input = (
        console.input("[cyan]Generate missing answers? (y/N):[/cyan] ").strip().lower()
    )
    generate_answers = generate_answers_input == "y"

    # Process
    agent.process(input_data, generate_answers=generate_answers)


if __name__ == "__main__":
    main()
