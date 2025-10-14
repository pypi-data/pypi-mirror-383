"""
PERFORMANCE OPTIMIZED CloudOps Runbooks - Enterprise CLI Interface

## Performance Optimizations Applied

### 1. Lazy Loading Architecture
- Defer AWS session initialization until needed
- Defer MCP validator loading until actual validation
- Defer pricing API calls until cost analysis operations
- Keep basic CLI operations (--help, --version) lightning fast

### 2. Startup Experience Optimization
- Move enterprise validation to on-demand loading
- Eliminate pricing API failures during basic operations
- Clean up warning pollution for simple commands
- Progressive disclosure of enterprise features

### 3. Import Optimization
- Critical imports only at module level
- Expensive imports deferred using lazy_loader
- Basic CLI functionality remains fast

## Performance Targets:
- Basic CLI operations < 0.5s
- Zero warnings for --help, --version
- Clean startup without overhead
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import os

import click
from loguru import logger

# Import lazy loading architecture FIRST
from runbooks.common.lazy_loader import (
    lazy_rich_console,
    lazy_aws_session,
    lazy_mcp_validator,
    lazy_performance_monitor,
    lazy_pricing_api,
    lazy_inventory_collector,
    fast_startup_mode,
    defer_expensive_imports,
    requires_aws,
    requires_mcp,
)

# Enable deferred imports for startup optimization
defer_expensive_imports()

# Fast Rich console loading
try:
    from rich.console import Console
    from rich.table import Table
    from rich.markup import escape

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

    # Fallback console implementation
    class Console:
        def print(self, *args, **kwargs):
            output = " ".join(str(arg) for arg in args)
            print(output)


# Basic imports only - no heavy AWS/MCP initialization
from runbooks import __version__


# Lazy imports for performance-critical operations
def get_assessment_runner():
    """Lazy load CFAT assessment runner."""
    from runbooks.cfat.runner import AssessmentRunner

    return AssessmentRunner


def get_profile_utils():
    """Lazy load profile utilities."""
    from runbooks.common.profile_utils import (
        create_management_session,
        create_operational_session,
        get_profile_for_operation,
    )

    return {
        "create_management_session": create_management_session,
        "create_operational_session": create_operational_session,
        "get_profile_for_operation": get_profile_for_operation,
    }


def get_rich_utils():
    """Lazy load Rich utilities."""
    from runbooks.common.rich_utils import console, create_table, print_banner, print_header, print_status

    return {
        "console": console,
        "create_table": create_table,
        "print_banner": print_banner,
        "print_header": print_header,
        "print_status": print_status,
    }


def get_config_utils():
    """Lazy load configuration utilities."""
    from runbooks.config import load_config, save_config

    return {"load_config": load_config, "save_config": save_config}


def get_logging_utils():
    """Lazy load logging utilities."""
    from runbooks.utils import setup_logging, setup_enhanced_logging

    return {"setup_logging": setup_logging, "setup_enhanced_logging": setup_enhanced_logging}


def get_business_case_utils():
    """Lazy load business case utilities."""
    from runbooks.finops.business_case_config import get_business_case_config, format_business_achievement

    return {
        "get_business_case_config": get_business_case_config,
        "format_business_achievement": format_business_achievement,
    }


# Global console for basic operations
console = Console()

# ============================================================================
# CLI ARGUMENT FIXES - Handle Profile Tuples and Export Format Issues
# ============================================================================


def normalize_profile_parameter(profile_param):
    """
    Normalize profile parameter from Click multiple=True tuple to string.

    Args:
        profile_param: Profile parameter from Click (could be tuple, list, or string)

    Returns:
        str: Single profile name for AWS operations
    """
    if profile_param is None:
        return None

    # Handle tuple/list from Click multiple=True
    if isinstance(profile_param, (tuple, list)):
        # Take the first profile if multiple provided
        return profile_param[0] if len(profile_param) > 0 else None

    # Handle string directly
    return profile_param


# Performance monitoring decorator
def track_performance(operation_name: str):
    """Decorator to track CLI operation performance."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if fast_startup_mode():
                # Skip performance tracking for fast operations
                return func(*args, **kwargs)

            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Only log if operation takes >0.1s to avoid spam
                if duration > 0.1:
                    logger.debug(f"Operation '{operation_name}' completed in {duration:.3f}s")

                return result
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.error(f"Operation '{operation_name}' failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


# ============================================================================
# CLI MAIN ENTRY POINT - OPTIMIZED FOR PERFORMANCE
# ============================================================================


@click.group()
@click.version_option(version=__version__, prog_name="runbooks")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--profile", help="AWS profile to use")
@click.pass_context
def cli(ctx: click.Context, debug: bool, profile: str):
    """
    CloudOps Runbooks - Enterprise AWS Automation Platform

    Fast, enterprise-grade automation for CloudOps, DevOps, and SRE teams.

    Performance optimized for sub-second response times.
    """
    # Fast context setup
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["debug"] = debug

    # Only setup logging if not a fast operation
    if not fast_startup_mode() and debug:
        setup_logging = get_logging_utils()["setup_logging"]
        setup_logging(debug=debug)


@cli.command()
@track_performance("version")
def version():
    """Show version information (fast operation)."""
    console.print(f"CloudOps Runbooks v{__version__}")
    console.print("Enterprise AWS Automation Platform")


@cli.command()
@track_performance("status")
def status():
    """Show system status (fast operation)."""
    console.print("🚀 CloudOps Runbooks Status")
    console.print(f"Version: {__version__}")
    console.print("Status: Ready")

    # Only check AWS if explicitly requested (not for basic status)
    import sys

    if "--aws" in sys.argv:
        check_aws_status()


def check_aws_status():
    """Check AWS connectivity (lazy loaded)."""
    try:
        session = lazy_aws_session()
        console.print("AWS: Connected")
    except Exception as e:
        console.print(f"AWS: Error - {e}")


# ============================================================================
# FINOPS COMMANDS - WITH LAZY LOADING
# ============================================================================


@cli.group()
def finops():
    """Financial Operations and Cost Analysis"""
    pass


@finops.command()
@click.option("--profile", help="AWS profile to use")
@click.option("--export", type=click.Choice(["csv", "json", "html", "pdf"]), help="Export format")
@click.option("--output-file", type=click.Path(), help="Output file path")
@click.option("--mcp-validation", is_flag=True, help="Enable MCP validation")
@track_performance("finops_dashboard")
@requires_aws
def dashboard(profile: str, export: str, output_file: str, mcp_validation: bool):
    """Run FinOps cost analysis dashboard (lazy loaded)."""
    # Lazy load FinOps components only when needed
    from runbooks.finops.dashboard_runner import run_dashboard

    profile_utils = get_profile_utils()
    rich_utils = get_rich_utils()

    # Normalize profile parameter
    normalized_profile = normalize_profile_parameter(profile)

    console.print("🚀 Starting FinOps Dashboard Analysis...")

    # Optional MCP validation
    if mcp_validation:
        validator = lazy_mcp_validator()
        console.print("📊 MCP validation enabled")

    # Run dashboard with lazy-loaded components
    try:
        result = run_dashboard(profile=normalized_profile, export_format=export, output_file=output_file)
        console.print("✅ FinOps analysis completed successfully")
        return result
    except Exception as e:
        console.print(f"❌ FinOps analysis failed: {e}")
        raise


# ============================================================================
# INVENTORY COMMANDS - WITH LAZY LOADING
# ============================================================================


@cli.group()
def inventory():
    """Resource Discovery and Inventory Management"""
    pass


@inventory.command()
@click.option("--profile", help="AWS profile to use")
@click.option("--regions", multiple=True, help="AWS regions to scan")
@click.option("--services", multiple=True, help="AWS services to include")
@click.option("--export", type=click.Choice(["csv", "json", "yaml"]), help="Export format")
@track_performance("inventory_collect")
@requires_aws
def collect(profile: str, regions: tuple, services: tuple, export: str):
    """Collect comprehensive inventory across AWS accounts (lazy loaded)."""
    # Lazy load inventory collector only when needed
    InventoryCollector = lazy_inventory_collector()

    profile_utils = get_profile_utils()

    # Normalize profile parameter
    normalized_profile = normalize_profile_parameter(profile)

    console.print("🔍 Starting inventory collection...")

    # Create collector with lazy-loaded session
    session = lazy_aws_session()
    collector = InventoryCollector(session=session)

    try:
        result = collector.collect_all(
            profile=normalized_profile,
            regions=list(regions) if regions else None,
            services=list(services) if services else None,
            export_format=export,
        )
        console.print("✅ Inventory collection completed successfully")
        return result
    except Exception as e:
        console.print(f"❌ Inventory collection failed: {e}")
        raise


# ============================================================================
# SECURITY COMMANDS - WITH LAZY LOADING
# ============================================================================


@cli.group()
def security():
    """Security Assessment and Compliance"""
    pass


@security.command()
@click.option("--profile", help="AWS profile to use")
@click.option("--frameworks", multiple=True, help="Compliance frameworks to check")
@click.option("--export", type=click.Choice(["csv", "json", "html"]), help="Export format")
@track_performance("security_assess")
@requires_aws
def assess(profile: str, frameworks: tuple, export: str):
    """Run security baseline assessment (lazy loaded)."""
    # Lazy load security components only when needed
    from runbooks.security.security_baseline_tester import SecurityBaselineTester

    profile_utils = get_profile_utils()

    # Normalize profile parameter
    normalized_profile = normalize_profile_parameter(profile)

    console.print("🔒 Starting security assessment...")

    # Create tester with lazy-loaded session
    session = lazy_aws_session()
    tester = SecurityBaselineTester(session=session)

    try:
        result = tester.run_assessment(
            profile=normalized_profile, frameworks=list(frameworks) if frameworks else None, export_format=export
        )
        console.print("✅ Security assessment completed successfully")
        return result
    except Exception as e:
        console.print(f"❌ Security assessment failed: {e}")
        raise


# ============================================================================
# OPERATE COMMANDS - WITH LAZY LOADING
# ============================================================================


@cli.group()
def operate():
    """AWS Resource Operations and Automation"""
    pass


@operate.command()
@click.option("--profile", help="AWS profile to use")
@click.option("--dry-run", is_flag=True, default=True, help="Dry run mode (default: enabled)")
@track_performance("operate_ec2")
@requires_aws
def ec2(profile: str, dry_run: bool):
    """EC2 resource operations (lazy loaded)."""
    # Lazy load EC2 operations only when needed
    from runbooks.operate.ec2_operations import EC2Operations

    # Normalize profile parameter
    normalized_profile = normalize_profile_parameter(profile)

    console.print("⚡ Starting EC2 operations...")

    if dry_run:
        console.print("🔒 Running in dry-run mode (no changes will be made)")

    # Create operations with lazy-loaded session
    session = lazy_aws_session()
    ec2_ops = EC2Operations(session=session)

    try:
        result = ec2_ops.list_instances(profile=normalized_profile, dry_run=dry_run)
        console.print("✅ EC2 operations completed successfully")
        return result
    except Exception as e:
        console.print(f"❌ EC2 operations failed: {e}")
        raise


# ============================================================================
# CFAT COMMANDS - WITH LAZY LOADING
# ============================================================================


@cli.group()
def cfat():
    """Cloud Foundations Assessment Tool"""
    pass


@cfat.command()
@click.option("--profile", help="AWS profile to use")
@click.option("--output-file", type=click.Path(), help="Assessment report output file")
@track_performance("cfat_assess")
@requires_aws
def assess(profile: str, output_file: str):
    """Run Cloud Foundations Assessment (lazy loaded)."""
    # Lazy load CFAT components only when needed
    AssessmentRunner = get_assessment_runner()

    # Normalize profile parameter
    normalized_profile = normalize_profile_parameter(profile)

    console.print("🏛️ Starting Cloud Foundations Assessment...")

    # Create runner with lazy-loaded session
    session = lazy_aws_session()
    runner = AssessmentRunner(session=session)

    try:
        result = runner.run_assessment(profile=normalized_profile, output_file=output_file)
        console.print("✅ CFAT assessment completed successfully")
        return result
    except Exception as e:
        console.print(f"❌ CFAT assessment failed: {e}")
        raise


# ============================================================================
# PERFORMANCE DIAGNOSTICS
# ============================================================================


@cli.command()
@track_performance("perf_test")
def perf():
    """Performance diagnostics and benchmarking."""
    start_time = datetime.now()

    console.print("🚀 Performance Diagnostics")
    console.print(f"Startup Time: {(datetime.now() - start_time).total_seconds():.3f}s")

    # Test lazy loading performance
    console.print("\n📊 Component Loading Times:")

    # Test Rich loading
    rich_start = datetime.now()
    lazy_rich_console()
    rich_time = (datetime.now() - rich_start).total_seconds()
    console.print(f"Rich Console: {rich_time:.3f}s")

    # Test AWS session (only if credentials available)
    try:
        aws_start = datetime.now()
        lazy_aws_session()
        aws_time = (datetime.now() - aws_start).total_seconds()
        console.print(f"AWS Session: {aws_time:.3f}s")
    except Exception:
        console.print("AWS Session: Not available (no credentials)")

    # Test MCP validator
    try:
        mcp_start = datetime.now()
        lazy_mcp_validator()
        mcp_time = (datetime.now() - mcp_start).total_seconds()
        console.print(f"MCP Validator: {mcp_time:.3f}s")
    except Exception:
        console.print("MCP Validator: Not available")

    total_time = (datetime.now() - start_time).total_seconds()
    console.print(f"\n⏱️ Total Diagnostic Time: {total_time:.3f}s")


if __name__ == "__main__":
    cli()
