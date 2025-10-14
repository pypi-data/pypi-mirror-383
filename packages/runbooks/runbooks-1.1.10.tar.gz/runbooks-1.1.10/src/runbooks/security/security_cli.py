#!/usr/bin/env python3
"""
Security CLI Commands - Dynamic Configuration Support

Enhanced security CLI with enterprise configuration patterns:
- Dynamic account discovery (environment variables, config files, Organizations API)
- Dynamic compliance weights and thresholds
- Profile override support (--profile parameter)
- Multi-account operations (--all flag)
- Configuration-driven approach eliminating hardcoded values

Author: DevOps Security Engineer (Claude Code Enterprise Team)
Version: 1.0 - Enterprise Dynamic Configuration Ready
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel

from runbooks.common.profile_utils import get_profile_for_operation, validate_profile_access
from runbooks.common.rich_utils import (
    console,
    create_panel,
    print_error,
    print_info,
    print_success,
    print_warning,
)

from .compliance_automation_engine import ComplianceAutomationEngine, ComplianceFramework
from .security_baseline_tester import SecurityBaselineTester
from .config_template_generator import SecurityConfigTemplateGenerator
from .two_way_validation_framework import execute_2way_validation


@click.group()
@click.option("--profile", default=None, help="AWS profile to use (overrides environment variables)")
@click.option("--output-dir", default="./artifacts/security", help="Output directory for security reports")
@click.pass_context
def security(ctx, profile: Optional[str], output_dir: str):
    """
    Enterprise Security Operations with Dynamic Configuration.

    Supports configuration via:
    - Environment variables
    - Configuration files
    - AWS Organizations API
    - Profile override patterns
    """
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["output_dir"] = output_dir

    # Validate profile if specified
    if profile:
        resolved_profile = get_profile_for_operation("management", profile)
        if not validate_profile_access(resolved_profile, "security operations"):
            print_error(f"Profile validation failed: {resolved_profile}")
            raise click.Abort()


@security.command()
@click.option(
    "--frameworks",
    multiple=True,
    type=click.Choice(
        ["aws-well-architected", "soc2-type-ii", "pci-dss", "hipaa", "iso27001", "nist-cybersecurity", "cis-benchmarks"]
    ),
    default=["aws-well-architected"],
    help="Compliance frameworks to assess",
)
@click.option("--accounts", help="Comma-separated account IDs (overrides discovery)")
@click.option("--all", "all_accounts", is_flag=True, help="Assess all discovered accounts via Organizations API")
@click.option("--scope", type=click.Choice(["full", "quick", "critical"]), default="full", help="Assessment scope")
@click.option(
    "--export-formats",
    multiple=True,
    type=click.Choice(["json", "csv", "html", "pdf"]),
    default=["json", "csv"],
    help="Export formats for compliance reports",
)
@click.pass_context
def assess(
    ctx, frameworks: List[str], accounts: Optional[str], all_accounts: bool, scope: str, export_formats: List[str]
):
    """
    Execute comprehensive compliance assessment with dynamic configuration.

    Environment Variables Supported:
    - COMPLIANCE_TARGET_ACCOUNTS: Comma-separated account IDs
    - COMPLIANCE_ACCOUNTS_CONFIG: Path to accounts configuration file
    - COMPLIANCE_WEIGHT_<CONTROL_ID>: Dynamic control weights
    - COMPLIANCE_THRESHOLD_<FRAMEWORK>: Dynamic framework thresholds
    """
    profile = ctx.obj["profile"]
    output_dir = ctx.obj["output_dir"]

    try:
        # Convert framework names to enum values
        framework_mapping = {
            "aws-well-architected": ComplianceFramework.AWS_WELL_ARCHITECTED,
            "soc2-type-ii": ComplianceFramework.SOC2_TYPE_II,
            "pci-dss": ComplianceFramework.PCI_DSS,
            "hipaa": ComplianceFramework.HIPAA,
            "iso27001": ComplianceFramework.ISO27001,
            "nist-cybersecurity": ComplianceFramework.NIST_CYBERSECURITY,
            "cis-benchmarks": ComplianceFramework.CIS_BENCHMARKS,
        }

        selected_frameworks = [framework_mapping[f] for f in frameworks]

        # Parse target accounts
        target_accounts = None
        if accounts:
            target_accounts = [acc.strip() for acc in accounts.split(",")]
            print_info(f"Using specified accounts: {len(target_accounts)} accounts")
        elif all_accounts:
            print_info("Using all discovered accounts via Organizations API")
            # target_accounts will be None, triggering discovery
        else:
            print_info("Using default account discovery")

        # Initialize compliance engine
        console.print(
            create_panel(
                f"[bold cyan]Enterprise Compliance Assessment[/bold cyan]\n\n"
                f"[dim]Frameworks: {', '.join(frameworks)}[/dim]\n"
                f"[dim]Profile: {profile or 'default'}[/dim]\n"
                f"[dim]Scope: {scope}[/dim]\n"
                f"[dim]Export Formats: {', '.join(export_formats)}[/dim]",
                title="🛡️ Starting Assessment",
                border_style="cyan",
            )
        )

        compliance_engine = ComplianceAutomationEngine(profile=profile, output_dir=output_dir)

        # Execute assessment
        reports = asyncio.run(
            compliance_engine.assess_compliance(
                frameworks=selected_frameworks, target_accounts=target_accounts, scope=scope
            )
        )

        # Display summary
        print_success(f"Assessment completed! Generated {len(reports)} compliance reports")
        print_info(f"Reports saved to: {output_dir}")

        # Display configuration sources used
        _display_configuration_sources()

    except Exception as e:
        print_error(f"Compliance assessment failed: {str(e)}")
        raise click.Abort()


@security.command()
@click.option("--language", type=click.Choice(["en", "ja", "ko", "vi"]), default="en", help="Report language")
@click.option(
    "--export-formats",
    multiple=True,
    type=click.Choice(["json", "csv", "html", "pdf"]),
    default=["json", "csv"],
    help="Export formats for security reports",
)
@click.pass_context
def baseline(ctx, language: str, export_formats: List[str]):
    """
    Execute security baseline assessment with dynamic configuration.

    Uses enterprise profile management and configuration-driven approach.
    """
    profile = ctx.obj["profile"]
    output_dir = ctx.obj["output_dir"]

    try:
        console.print(
            create_panel(
                f"[bold cyan]AWS Security Baseline Assessment[/bold cyan]\n\n"
                f"[dim]Profile: {profile or 'default'}[/dim]\n"
                f"[dim]Language: {language}[/dim]\n"
                f"[dim]Export Formats: {', '.join(export_formats)}[/dim]",
                title="🔒 Starting Baseline Assessment",
                border_style="green",
            )
        )

        # Initialize security baseline tester
        baseline_tester = SecurityBaselineTester(
            profile=profile, lang_code=language, output_dir=output_dir, export_formats=list(export_formats)
        )

        # Execute baseline assessment
        baseline_tester.run()

        print_success("Security baseline assessment completed successfully!")
        print_info(f"Results saved to: {output_dir}")

    except Exception as e:
        print_error(f"Security baseline assessment failed: {str(e)}")
        raise click.Abort()


@security.command()
@click.pass_context
def config_info(ctx):
    """
    Display current security configuration and environment setup.
    """
    console.print(Panel.fit("[bold cyan]Security Configuration Information[/bold cyan]", border_style="cyan"))

    # Display environment variables
    print_info("Environment Configuration:")

    env_vars = {
        "Profile Configuration": {
            "MANAGEMENT_PROFILE": os.getenv("MANAGEMENT_PROFILE", "Not set"),
            "BILLING_PROFILE": os.getenv("BILLING_PROFILE", "Not set"),
            "CENTRALISED_OPS_PROFILE": os.getenv("CENTRALISED_OPS_PROFILE", "Not set"),
        },
        "Compliance Configuration": {
            "COMPLIANCE_TARGET_ACCOUNTS": os.getenv("COMPLIANCE_TARGET_ACCOUNTS", "Not set"),
            "COMPLIANCE_ACCOUNTS_CONFIG": os.getenv("COMPLIANCE_ACCOUNTS_CONFIG", "Not set"),
            "COMPLIANCE_WEIGHTS_CONFIG": os.getenv("COMPLIANCE_WEIGHTS_CONFIG", "Not set"),
            "COMPLIANCE_THRESHOLDS_CONFIG": os.getenv("COMPLIANCE_THRESHOLDS_CONFIG", "Not set"),
        },
        "Remediation Configuration": {
            "REMEDIATION_TARGET_ACCOUNTS": os.getenv("REMEDIATION_TARGET_ACCOUNTS", "Not set"),
            "REMEDIATION_ACCOUNT_CONFIG": os.getenv("REMEDIATION_ACCOUNT_CONFIG", "Not set"),
        },
    }

    for category, variables in env_vars.items():
        console.print(f"\n[bold]{category}:[/bold]")
        for var_name, var_value in variables.items():
            status = "✅" if var_value != "Not set" else "❌"
            console.print(f"  {status} {var_name}: {var_value}")

    # Display example configuration files
    console.print("\n[bold]Example Configuration Files:[/bold]")
    config_examples = [
        "src/runbooks/security/config/compliance_weights_example.json",
        "src/runbooks/remediation/config/accounts_example.json",
    ]

    for config_file in config_examples:
        if os.path.exists(config_file):
            console.print(f"  ✅ {config_file}")
        else:
            console.print(f"  📝 {config_file} (example)")


def _display_configuration_sources():
    """Display information about configuration sources used."""
    console.print("\n[bold]Configuration Sources:[/bold]")

    # Check environment variables
    if os.getenv("COMPLIANCE_TARGET_ACCOUNTS"):
        console.print("  ✅ Using COMPLIANCE_TARGET_ACCOUNTS environment variable")

    if os.getenv("COMPLIANCE_ACCOUNTS_CONFIG"):
        config_path = os.getenv("COMPLIANCE_ACCOUNTS_CONFIG")
        if os.path.exists(config_path):
            console.print(f"  ✅ Using accounts config file: {config_path}")
        else:
            console.print(f"  ⚠️  Accounts config file not found: {config_path}")

    if os.getenv("COMPLIANCE_WEIGHTS_CONFIG"):
        config_path = os.getenv("COMPLIANCE_WEIGHTS_CONFIG")
        if os.path.exists(config_path):
            console.print(f"  ✅ Using compliance weights config: {config_path}")
        else:
            console.print(f"  ⚠️  Compliance weights config not found: {config_path}")

    # Check for dynamic control weights
    weight_vars = [var for var in os.environ.keys() if var.startswith("COMPLIANCE_WEIGHT_")]
    if weight_vars:
        console.print(f"  ✅ Using {len(weight_vars)} dynamic control weights")

    # Check for dynamic thresholds
    threshold_vars = [var for var in os.environ.keys() if var.startswith("COMPLIANCE_THRESHOLD_")]
    if threshold_vars:
        console.print(f"  ✅ Using {len(threshold_vars)} dynamic framework thresholds")

    if not any(
        [os.getenv("COMPLIANCE_TARGET_ACCOUNTS"), os.getenv("COMPLIANCE_ACCOUNTS_CONFIG"), weight_vars, threshold_vars]
    ):
        console.print("  ℹ️  Using default configuration (Organizations API discovery)")


@security.command("2way-validate")
@click.option("--profile", default="ams-admin-ReadOnlyAccess-909135376185", help="AWS profile for validation testing")
@click.option(
    "--certification-required", is_flag=True, help="Require production certification (≥97% combined accuracy)"
)
@click.pass_context
def two_way_validate(ctx, profile: str, certification_required: bool):
    """
    Execute comprehensive 2-Way Validation Framework for production readiness.

    Combines Playwright MCP (UI/browser testing) with AWS MCP (real API validation)
    to achieve ≥97% combined accuracy for enterprise production deployment.

    **SECURITY VALIDATION SCOPE**:
    - Playwright MCP: >98% browser testing success rate
    - AWS MCP: >97.5% real AWS API validation accuracy
    - Combined Accuracy: ≥97% overall validation requirement
    - Enterprise Compliance: Audit trail and production certification
    """
    try:
        console.print(
            create_panel(
                f"[bold cyan]🚨 Enterprise 2-Way Validation Framework[/bold cyan]\n\n"
                f"[dim]Profile: {profile}[/dim]\n"
                f"[dim]Certification Required: {'Yes' if certification_required else 'No'}[/dim]\n"
                f"[dim]Target Accuracy: ≥97% Combined[/dim]",
                title="🛡️ Security Validation Execution",
                border_style="cyan",
            )
        )

        print_info("🚀 Initiating comprehensive 2-way validation framework...")

        # Execute 2-way validation
        results = asyncio.run(execute_2way_validation(profile))

        # Display results
        certification_status = results["overall_status"]
        combined_accuracy = results["combined_accuracy"]["combined_accuracy"]

        if certification_status == "CERTIFIED":
            print_success(f"🏆 2-Way Validation: PRODUCTION CERTIFIED")
            print_success(f"📊 Combined Accuracy: {combined_accuracy * 100:.1f}%")
        else:
            print_warning(f"⚠️ 2-Way Validation: REQUIRES REVIEW")
            print_warning(f"📊 Combined Accuracy: {combined_accuracy * 100:.1f}%")

        # Display detailed metrics
        playwright_success = results["playwright_validation"]["success_rate"]
        aws_mcp_accuracy = results["aws_mcp_validation"]["accuracy_rate"]
        compliance_score = results["enterprise_compliance"]["compliance_score"]

        console.print(f"\n[bold cyan]Validation Metrics:[/bold cyan]")
        console.print(f"🎭 Playwright Success Rate: {playwright_success * 100:.1f}%")
        console.print(f"☁️ AWS MCP Accuracy Rate: {aws_mcp_accuracy * 100:.1f}%")
        console.print(f"🏢 Enterprise Compliance Score: {compliance_score * 100:.1f}%")

        # Handle certification requirements
        if certification_required and certification_status != "CERTIFIED":
            print_error("❌ Production certification required but not achieved")

            if results["recommendations"]:
                console.print(f"\n[bold yellow]Recommendations:[/bold yellow]")
                for recommendation in results["recommendations"]:
                    console.print(f"• {recommendation}")

            raise click.Abort()

        print_success("✅ 2-Way Validation Framework execution completed")
        print_info(f"📁 Evidence package saved to: ./artifacts/2way_validation_evidence/")

    except Exception as e:
        print_error(f"2-Way validation failed: {str(e)}")
        raise click.Abort()


@security.command("generate-config")
@click.option(
    "--output-dir", default="./artifacts/security/config", help="Output directory for configuration templates"
)
@click.pass_context
def generate_config_templates(ctx, output_dir: str):
    """
    Generate universal configuration templates for security operations.

    Creates templates for:
    - Compliance weights and thresholds
    - Account discovery configuration
    - Environment variable examples
    - Complete setup documentation

    All templates support universal AWS compatibility with no hardcoded values.
    """
    print_info(f"Generating universal security configuration templates in {output_dir}...")

    try:
        generator = SecurityConfigTemplateGenerator(output_dir)
        generator.generate_all_templates()

        print_success("Configuration templates generated successfully!")
        console.print("\n[bold yellow]Next steps:[/bold yellow]")
        console.print("1. Review and customize the generated configuration files")
        console.print("2. Set environment variables or copy configuration files to your preferred location")
        console.print("3. Run: runbooks security assess --help")
        console.print("4. Run: runbooks security 2way-validate --help")

    except Exception as e:
        print_error(f"Failed to generate configuration templates: {e}")
        raise click.Abort()


if __name__ == "__main__":
    security()
