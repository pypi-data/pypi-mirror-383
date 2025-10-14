"""LakePipe CLI - Main entry point."""

from pathlib import Path
from typing import Optional, Dict, Any
import typer
from rich.console import Console
from rich.table import Table
import json

from ..core.config import PipelineConfig
from ..core.pipeline import Pipeline
from ..utils.logger import setup_logging, console as rich_console

app = typer.Typer(
    name="lakepipe",
    help="🌊 LakePipe - Modern data transfer for cloud data lakes",
    add_completion=False
)
console = Console()


@app.command()
def run(
    config_file: Path = typer.Argument(..., help="Path to pipeline configuration file"),
    params: Optional[list[str]] = typer.Option(None, "--params", "-p", help="Runtime parameters (key=value)"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
    work_dir: Optional[Path] = typer.Option(None, "--work-dir", "-w", help="Working directory for intermediate files"),
):
    """Run a LakePipe pipeline."""
    setup_logging(level=log_level, rich_output=True)

    try:
        # Load configuration
        config = PipelineConfig.from_yaml(config_file)

        # Parse runtime parameters
        runtime_params: Dict[str, Any] = {}
        if params:
            for param in params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    runtime_params[key] = value

        # Create and run pipeline
        pipeline = Pipeline(config=config, work_dir=work_dir)
        result = pipeline.run(runtime_params=runtime_params)

        # Display result
        if result.success:
            console.print(f"\n✅ [green]Pipeline completed successfully![/green]")
            console.print(f"Duration: {result.duration:.1f}s")
            console.print(f"Rows loaded: {result.metrics.rows_loaded:,}")
            typer.Exit(0)
        else:
            console.print(f"\n❌ [red]Pipeline failed![/red]")
            for error in result.errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def plan(
    config_file: Path = typer.Argument(..., help="Path to pipeline configuration file"),
    params: Optional[list[str]] = typer.Option(None, "--params", "-p", help="Runtime parameters (key=value)"),
):
    """Show pipeline execution plan without running."""
    setup_logging(level="INFO", rich_output=True)

    try:
        # Load configuration
        config = PipelineConfig.from_yaml(config_file)

        # Parse runtime parameters
        runtime_params: Dict[str, Any] = {}
        if params:
            for param in params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    runtime_params[key] = value

        config.merge_params(runtime_params)

        # Display plan
        console.print("\n📋 [bold]Pipeline Plan[/bold]")
        console.print("=" * 60)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Stage")
        table.add_column("Details")

        table.add_row(
            "1. Source",
            f"{config.source.type}://{config.source.database}.{config.source.table}"
        )
        table.add_row(
            "2. Storage",
            f"{config.storage.type}://{config.storage.bucket}{config.storage.path}"
        )
        table.add_row(
            "3. Target",
            f"{config.target.type}://{config.target.database}.{config.target.table} (loader={config.target.loader})"
        )

        if config.validation:
            validation_str = []
            if config.validation.row_count:
                validation_str.append(f"row_count (variance={config.validation.row_count.max_variance})")
            table.add_row("4. Validation", ", ".join(validation_str) if validation_str else "None")

        console.print(table)
        console.print("\n✓ Plan generation complete")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    config_file: Path = typer.Argument(..., help="Path to pipeline configuration file"),
):
    """Validate pipeline configuration."""
    try:
        config = PipelineConfig.from_yaml(config_file)
        console.print("✓ [green]Configuration is valid[/green]")
        console.print(f"\nPipeline: {config.name}")
        console.print(f"Source: {config.source.type}")
        console.print(f"Storage: {config.storage.type}")
        console.print(f"Target: {config.target.type}")

    except Exception as e:
        console.print(f"[red]Invalid configuration:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def init(
    output: Path = typer.Option("lakepipe.yml", "--output", "-o", help="Output configuration file"),
    source_type: str = typer.Option("hive", "--source", help="Source type"),
    target_type: str = typer.Option("teradata", "--target", help="Target type"),
):
    """Generate a sample pipeline configuration."""

    # Create sample config
    sample_config = {
        "version": "1.0",
        "name": "my_pipeline",
        "description": "Sample LakePipe pipeline",
        "source": {
            "type": source_type,
            "database": "source_db",
            "table": "source_table",
            "partition_by": "date",
        },
        "storage": {
            "type": "s3",
            "bucket": "my-bucket",
            "path": "/staging",
            "cleanup": True,
        },
        "target": {
            "type": target_type,
            "host": "target-host",
            "database": "target_db",
            "table": "target_table",
            "loader": "tpt" if target_type == "teradata" else "default",
        },
        "validation": {
            "row_count": {
                "enabled": True,
                "max_variance": 0.01,
            }
        }
    }

    # Save to file
    config = PipelineConfig.from_dict(sample_config)
    config.to_yaml(output)

    console.print(f"✓ [green]Created sample configuration:[/green] {output}")
    console.print(f"\nEdit the file and run: [bold]lakepipe run {output}[/bold]")


@app.command()
def version():
    """Show LakePipe version."""
    console.print("🌊 LakePipe v0.1.0")
    console.print("Modern data transfer for cloud data lakes")


if __name__ == "__main__":
    app()
