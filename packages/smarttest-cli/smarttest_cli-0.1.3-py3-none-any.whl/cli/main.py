#!/usr/bin/env python3
"""
SmartTest CLI - Main entry point
Execute test scenarios inside customer networks with secure, enterprise-ready architecture.
"""

import sys
import asyncio
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .api_client import ApiClient
from .scenario_executor import ScenarioExecutor
from .reporters import TerminalReporter, JunitReporter

app = typer.Typer(
    name="smarttest",
    help="SmartTest CLI - Execute test scenarios with secure credential handling",
    add_completion=False
)
console = Console()

@app.command()
def run(
    scenario_id: Optional[int] = typer.Option(None, "--scenario-id", help="Run specific scenario by ID"),
    endpoint_id: Optional[int] = typer.Option(None, "--endpoint-id", help="Run all scenarios for an endpoint"),
    system_id: Optional[int] = typer.Option(None, "--system-id", help="Run all scenarios for a system"),
    config_file: Optional[str] = typer.Option(".smarttest.yml", "--config", help="Configuration file path"),
    report_file: Optional[str] = typer.Option(None, "--report", help="Generate JUnit XML report"),
):
    """Execute test scenarios with zero-credential exposure security model."""

    # Validate arguments
    selection_count = sum(bool(x) for x in [scenario_id, endpoint_id, system_id])
    if selection_count != 1:
        console.print("❌ [red]Error: Must specify exactly one of --scenario-id, --endpoint-id, or --system-id[/red]")
        raise typer.Exit(1)

    # Load configuration
    try:
        config = Config.load(config_file)
    except Exception as e:
        console.print(f"❌ [red]Configuration error: {e}[/red]")
        raise typer.Exit(1)

    # Run the scenarios
    exit_code = asyncio.run(execute_scenarios(
        config=config,
        scenario_id=scenario_id,
        endpoint_id=endpoint_id,
        system_id=system_id,
        report_file=report_file
    ))

    raise typer.Exit(exit_code)

async def execute_scenarios(
    config: Config,
    scenario_id: Optional[int] = None,
    endpoint_id: Optional[int] = None,
    system_id: Optional[int] = None,
    report_file: Optional[str] = None
) -> int:
    """Main execution logic with error handling and reporting."""

    try:
        # Initialize components
        api_client = ApiClient(config)
        executor = ScenarioExecutor(config, api_client)
        reporter = TerminalReporter(console)

        # Discover scenarios
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            discovery_task = progress.add_task("🔍 Discovering scenarios...", total=None)

            if scenario_id:
                scenarios = await api_client.get_scenario_definition(scenario_id)
                scenarios = [scenarios] if scenarios else []
            elif endpoint_id:
                scenarios = await api_client.get_endpoint_scenarios(endpoint_id, only_with_validations=True)
            elif system_id:
                scenarios = await api_client.get_system_scenarios(system_id, only_with_validations=True)
            else:
                scenarios = []

            progress.update(discovery_task, completed=True)

        if not scenarios:
            console.print("❌ [yellow]No scenarios found with validations[/yellow]")
            return 1

        console.print(f"🔍 Found {len(scenarios)} scenarios")

        # Execute scenarios
        results = await executor.execute_scenarios(scenarios, reporter)

        # Generate reports
        if report_file:
            junit_reporter = JunitReporter()
            junit_reporter.generate_report(results, report_file)
            console.print(f"📄 JUnit report generated: {report_file}")

        # Final summary and exit code
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        if failed > 0:
            console.print(f"\n❌ [red]{failed} scenarios failed, {passed} passed[/red]")
            return 1
        else:
            console.print(f"\n✅ [green]All {passed} scenarios passed[/green]")
            return 0

    except KeyboardInterrupt:
        console.print("\n⚠️  [yellow]Execution interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n💥 [red]Fatal error: {e}[/red]")
        return 1

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()