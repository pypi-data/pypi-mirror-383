"""
MINIMAL CloudOps Runbooks CLI - Performance Baseline Test

This is a minimal version to test basic CLI performance without
any heavy imports or MCP initialization.

Performance Target: <0.5s for --help, --version
"""

import sys
import click
from datetime import datetime

# Minimal imports - only what's absolutely necessary
from runbooks import __version__


# Simple console fallback
class SimpleConsole:
    def print(self, *args, **kwargs):
        print(*args)


console = SimpleConsole()


@click.group()
@click.version_option(version=__version__, prog_name="runbooks")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--profile", help="AWS profile to use")
@click.pass_context
def cli(ctx: click.Context, debug: bool, profile: str):
    """
    CloudOps Runbooks - Enterprise AWS Automation Platform (Minimal Version)

    Performance optimized for sub-second response times.
    """
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["debug"] = debug


@cli.command()
def version():
    """Show version information."""
    console.print(f"CloudOps Runbooks v{__version__}")
    console.print("Enterprise AWS Automation Platform")


@cli.command()
def status():
    """Show basic status."""
    console.print("🚀 CloudOps Runbooks Status")
    console.print(f"Version: {__version__}")
    console.print("Status: Ready")


@cli.command()
def perf():
    """Test CLI performance baseline."""
    start_time = datetime.now()
    console.print("🚀 Performance Test")
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    console.print(f"Command execution: {duration:.3f}s")


# Only include minimal commands for performance testing
@cli.group()
def finops():
    """Financial Operations (lazy loaded)"""
    pass


@finops.command()
@click.option("--profile", help="AWS profile to use")
def dashboard(profile: str):
    """Run FinOps dashboard (will lazy load when needed)."""
    console.print("Loading FinOps dashboard...")

    # This is where we would lazy load the actual functionality
    start_time = datetime.now()

    # Simulate lazy loading
    try:
        from runbooks.finops.dashboard_runner import run_dashboard

        console.print(f"FinOps module loaded in {(datetime.now() - start_time).total_seconds():.3f}s")
    except ImportError:
        console.print(
            f"FinOps module not available (simulated lazy load: {(datetime.now() - start_time).total_seconds():.3f}s)"
        )


if __name__ == "__main__":
    cli()
