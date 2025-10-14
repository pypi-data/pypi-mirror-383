"""
ULTRA MINIMAL CloudOps Runbooks CLI - Performance Baseline Test

This version avoids ALL runbooks imports to isolate the performance issue.
"""

import sys
import click
from datetime import datetime

# Import version from single source of truth
from runbooks import __version__


@click.group()
@click.version_option(version=__version__, prog_name="runbooks")
@click.pass_context
def cli(ctx: click.Context):
    """
    CloudOps Runbooks - Ultra Minimal Test Version

    Testing CLI performance without any runbooks imports.
    """
    ctx.ensure_object(dict)


@cli.command()
def version():
    """Show version information."""
    print(f"CloudOps Runbooks v{__version__}")


@cli.command()
def status():
    """Show basic status."""
    print("🚀 CloudOps Runbooks Status")
    print(f"Version: {__version__}")
    print("Status: Ready")


@cli.command()
def perf():
    """Test CLI performance baseline."""
    start_time = datetime.now()
    print("🚀 Performance Test")
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"Command execution: {duration:.3f}s")


if __name__ == "__main__":
    cli()
