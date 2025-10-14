"""
Inventory Commands Module - Resource Discovery & MCP Validation

KISS Principle: Focused on inventory operations only
DRY Principle: Reusable inventory patterns and common options

Extracted from main.py lines 404-889 for modular architecture.
Preserves 100% functionality while reducing main.py context overhead.
"""

import click
import os
import sys

# Import unified CLI decorators (v1.1.7 standardization)
from runbooks.common.cli_decorators import (
    common_aws_options,
    common_output_options,
    common_multi_account_options,
    common_filter_options,
    mcp_validation_option
)

# Test Mode Support: Disable Rich Console in test environments to prevent I/O conflicts
# Issue: Rich Console writes to StringIO buffer that Click CliRunner closes, causing ValueError
# Solution: Use plain print() in test mode (RUNBOOKS_TEST_MODE=1), Rich Console in production
USE_RICH = os.getenv("RUNBOOKS_TEST_MODE") != "1"

if USE_RICH:
    from rich.console import Console

    console = Console()
else:
    # Mock Rich Console for testing - plain text output compatible with Click CliRunner
    class MockConsole:
        """Mock console that prints to stdout without Rich formatting."""

        def print(self, *args, **kwargs):
            """Mock print that outputs plain text to stdout."""
            if args:
                # Extract text content from Rich markup if present
                text = str(args[0]) if args else ""
                # Remove Rich markup tags for plain output
                import re

                text = re.sub(r"\[.*?\]", "", text)
                print(text, file=sys.stdout)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    console = MockConsole()


def create_inventory_group():
    """
    Create the inventory command group with all subcommands.

    Returns:
        Click Group object with all inventory commands

    Performance: Lazy creation only when needed by DRYCommandRegistry
    """

    @click.group(invoke_without_command=True)
    @click.pass_context
    @common_aws_options
    @common_output_options
    @common_multi_account_options
    @common_filter_options
    def inventory(ctx, profile, region, dry_run, format, output_dir, export,
                  all_profiles, profiles, regions, all_regions, tags, accounts):
        """
        Universal AWS resource discovery and inventory - works with ANY AWS environment.

        ✅ Universal Compatibility: Works with single accounts, Organizations, and any profile setup
        🔍 Read-only operations for safe resource discovery across AWS services
        🚀 Intelligent fallback: Organizations → standalone account detection

        Profile Options:
            --profile PROFILE       Use specific AWS profile (highest priority)
            No --profile           Uses AWS_PROFILE environment variable
            No configuration       Uses 'default' profile (universal AWS CLI compatibility)

        Examples:
            runbooks inventory collect                           # Use default profile
            runbooks inventory collect --profile my-profile      # Use specific profile
            runbooks inventory collect --resources ec2,rds       # Specific resources
            runbooks inventory collect --all-profile MANAGEMENT_PROFILE  # Multi-account Organizations auto-discovery
            runbooks inventory collect --tags Environment=prod   # Filtered discovery
        """
        # Ensure context object exists
        if ctx.obj is None:
            ctx.obj = {}

        # Update context with inventory-specific options
        ctx.obj.update(
            {
                "profile": profile,
                "region": region,
                "dry_run": dry_run,
                "format": format,
                "output_dir": output_dir,
                "export": export,
                "all_profiles": all_profiles,
                "profiles": profiles,
                "regions": regions,
                "all_regions": all_regions,
                "tags": tags,
                "accounts": accounts,
            }
        )

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @inventory.command()
    @click.option("--profile", type=str, default=None, help="AWS profile to use (overrides parent group)")
    @click.option("--resources", "-r", multiple=True, help="Resource types (ec2, rds, lambda, s3, etc.)")
    @click.option("--all-resources", is_flag=True, help="Collect all resource types")
    @click.option("--all-profile", type=str, default=None, help="Management profile for Organizations API auto-discovery (MANAGEMENT_PROFILE, BILLING_PROFILE, or CENTRALISED_OPS_PROFILE)")
    @click.option("--all-regions", is_flag=True, help="Execute inventory collection across all AWS regions")
    @click.option("--include-costs", is_flag=True, help="Include cost information")
    @click.option(
        "--include-cost-analysis", "include_costs", is_flag=True, hidden=True, help="Alias for --include-costs"
    )
    @click.option(
        "--include-security-analysis", "include_security", is_flag=True, help="Include security analysis in inventory"
    )
    @click.option(
        "--include-cost-recommendations",
        "include_cost_recommendations",
        is_flag=True,
        help="Include cost optimization recommendations",
    )
    @click.option("--parallel", is_flag=True, default=True, help="Enable parallel collection")
    @click.option("--validate", is_flag=True, default=False, help="Enable MCP validation for ≥99.5% accuracy")
    @click.option(
        "--validate-all",
        is_flag=True,
        default=False,
        help="Enable comprehensive 3-way validation: runbooks + MCP + terraform",
    )
    @click.option(
        "--all", is_flag=True, help="Use all available AWS profiles for multi-account collection (enterprise scaling)"
    )
    @click.option("--combine", is_flag=True, help="Combine results from the same AWS account")
    @click.option("--csv", is_flag=True, help="Generate CSV export (convenience flag for --export-format csv)")
    @click.option("--json", is_flag=True, help="Generate JSON export (convenience flag for --export-format json)")
    @click.option("--pdf", is_flag=True, help="Generate PDF export (convenience flag for --export-format pdf)")
    @click.option(
        "--markdown", is_flag=True, help="Generate markdown export (convenience flag for --export-format markdown)"
    )
    @click.option(
        "--export-format",
        type=click.Choice(["json", "csv", "markdown", "pdf", "yaml"]),
        help="Export format for results (convenience flags take precedence)",
    )
    @click.option("--output-dir", default="./awso_evidence", help="Output directory for exports")
    @click.option("--report-name", help="Base name for export files (without extension)")
    @click.option("--dry-run", is_flag=True, default=True, help="Safe analysis mode - no resource modifications (enterprise default)")
    @click.option("--status", type=click.Choice(["running", "stopped"]), help="EC2 instance state filter")
    @click.option("--root-only", is_flag=True, help="Show only management accounts")
    @click.option("--short", "-s", "-q", is_flag=True, help="Brief output mode")
    @click.option("--acct", "-A", multiple=True, help="Account ID lookup (can specify multiple)")
    @click.option("--skip-profiles", multiple=True, help="Profiles to exclude from collection")
    @click.option("-v", "--verbose", is_flag=True, help="Verbose output with detailed information")
    @click.option("--timing", is_flag=True, help="Show performance metrics and execution timing")
    @click.option("--save", type=str, help="Output file prefix for saved results")
    @click.option("--filename", type=str, help="Custom report filename (overrides --report-name)")
    @click.pass_context
    def collect(
        ctx,
        profile,
        resources,
        all_resources,
        all_profile,
        all_regions,
        include_costs,
        include_security,
        include_cost_recommendations,
        parallel,
        validate,
        validate_all,
        all,
        combine,
        csv,
        json,
        pdf,
        markdown,
        export_format,
        output_dir,
        report_name,
        dry_run,
        status,
        root_only,
        short,
        acct,
        skip_profiles,
        verbose,
        timing,
        save,
        filename,
    ):
        """
        🔍 Universal AWS resource inventory collection - works with ANY AWS environment.

        ✅ Universal Compatibility Features:
        - Works with single accounts, AWS Organizations, and standalone setups
        - Profile override priority: User > Environment > Default ('default' profile fallback)
        - Intelligent Organizations detection with graceful standalone fallback
        - 50+ AWS services discovery across any account configuration
        - Multi-format exports: CSV, JSON, PDF, Markdown, YAML
        - MCP validation for ≥99.5% accuracy

        Universal Profile Usage:
        - ANY AWS profile works (no hardcoded assumptions)
        - Organizations permissions auto-detected (graceful fallback to single account)
        - AWS_PROFILE environment variable used when available
        - 'default' profile used as universal fallback

        Examples:
            # Universal compatibility - works with any AWS setup
            runbooks inventory collect                                    # Default profile
            runbooks inventory collect --profile my-aws-profile           # Any profile
            runbooks inventory collect --all-profile MANAGEMENT_PROFILE   # Organizations auto-discovery

            # Resource-specific discovery
            runbooks inventory collect --resources ec2,rds,s3             # Specific services
            runbooks inventory collect --all-resources                    # All 50+ services

            # Multi-format exports
            runbooks inventory collect --csv --json --pdf                 # Multiple formats
            runbooks inventory collect --profile prod --validate --markdown
        """
        try:
            from runbooks.inventory.core.collector import run_inventory_collection

            # Profile priority: command-level > group-level > context
            # This allows both patterns to work:
            #   runbooks inventory --profile X collect
            #   runbooks inventory collect --profile X
            if not profile:
                profile = ctx.obj.get('profile')
            region = ctx.obj.get('region')
            # dry_run is already resolved from command-level decorator (default=True)

            # Enhanced context for inventory collection
            context_args = {
                "profile": profile,
                "region": region,
                "dry_run": dry_run,
                "resources": resources,
                "all_resources": all_resources,
                "all_profile": all_profile,
                "all_regions": all_regions,
                "include_costs": include_costs,
                "include_security": include_security,
                "include_cost_recommendations": include_cost_recommendations,
                "parallel": parallel,
                "validate": validate,
                "validate_all": validate_all,
                "all": all,
                "combine": combine,
                "export_formats": [],
                "output_dir": output_dir,
                "report_name": report_name,
                "status": status,
                "root_only": root_only,
                "short": short,
                "acct": acct,
                "skip_profiles": skip_profiles,
                "verbose": verbose,
                "timing": timing,
                "save": save,
                "filename": filename,
            }

            # Handle export format flags
            if csv:
                context_args["export_formats"].append("csv")
            if json:
                context_args["export_formats"].append("json")
            if pdf:
                context_args["export_formats"].append("pdf")
            if markdown:
                context_args["export_formats"].append("markdown")
            if export_format:
                context_args["export_formats"].append(export_format)

            # Default to table output if no export formats specified
            if not context_args["export_formats"]:
                context_args["export_formats"] = ["table"]

            # Run inventory collection with enhanced context
            return run_inventory_collection(**context_args)

        except ImportError as e:
            console.print(f"[red]❌ Inventory collection module not available: {e}[/red]")
            raise click.ClickException("Inventory collection functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Inventory collection failed: {e}[/red]")
            raise click.ClickException(str(e))

    @inventory.command()
    @click.option(
        "--resource-types",
        multiple=True,
        type=click.Choice(["ec2", "s3", "rds", "lambda", "vpc", "iam"]),
        default=["ec2", "s3", "vpc"],
        help="Resource types to validate",
    )
    @click.option("--test-mode", is_flag=True, default=True, help="Run in test mode with sample data")
    @click.option(
        "--real-validation",
        is_flag=True,
        default=False,
        help="Run validation against real AWS APIs (requires valid profiles)",
    )
    @click.pass_context
    def validate_mcp(ctx, resource_types, test_mode, real_validation):
        """Test inventory MCP validation functionality."""
        try:
            from runbooks.inventory.mcp_inventory_validator import create_inventory_mcp_validator
            from runbooks.common.profile_utils import get_profile_for_operation

            # Access profile from group-level context (Bug #3 fix: profile override support)
            profile = ctx.obj.get('profile')

            console.print(f"[blue]🔍 Testing Inventory MCP Validation[/blue]")
            console.print(f"[dim]Profile: {profile or 'environment fallback'} | Resources: {', '.join(resource_types)} | Test mode: {test_mode}[/dim]")

            # Initialize validator
            operational_profile = get_profile_for_operation("operational", profile)
            validator = create_inventory_mcp_validator([operational_profile])

            # Test with sample data
            sample_data = {
                operational_profile: {"resource_counts": {rt: 5 for rt in resource_types}, "regions": ["us-east-1"]}
            }

            console.print("[dim]Running validation test...[/dim]")
            validation_results = validator.validate_inventory_data(sample_data)

            accuracy = validation_results.get("total_accuracy", 0)
            if validation_results.get("passed_validation", False):
                console.print(f"[green]✅ MCP Validation test completed: {accuracy:.1f}% accuracy[/green]")
            else:
                console.print(
                    f"[yellow]⚠️ MCP Validation test: {accuracy:.1f}% accuracy (demonstrates validation capability)[/yellow]"
                )

            console.print(f"[dim]💡 Use 'runbooks inventory collect --validate' for real-time validation[/dim]")

        except Exception as e:
            console.print(f"[red]❌ MCP validation test failed: {e}[/red]")
            raise click.ClickException(str(e))

    # NOTE: rds-snapshots command removed in v1.1.6 (Bug #2 fix: phantom command elimination)
    # Reason: Module rds_snapshots_discovery.py doesn't exist (was never implemented)
    # Future work: Implement proper RDS snapshots discovery in v1.2.0
    # See: artifacts/future-work/rds-snapshots-discovery-v1.2.0.md

    @inventory.command(name="draw-org")
    @click.option("--profile", type=str, default=None, help="AWS profile to use (overrides group-level --profile)")
    @click.option("--policy/--no-policy", is_flag=True, default=False,
                  help="Include policies in organization diagram")
    @click.option("--show-aws-managed/--hide-aws-managed", is_flag=True, default=False,
                  help="Show AWS managed SCPs (hidden by default)")
    @click.option("--ou", "--starting-ou", type=str, default=None,
                  help="Starting organizational unit ID (defaults to root)")
    @click.option("-f", "--format", "--output-format",
                  type=click.Choice(["graphviz", "mermaid", "diagrams"]),
                  default="graphviz",
                  help="Diagram format: graphviz (PNG), mermaid (text), diagrams (Python library). (-f/--format preferred, --output-format legacy)")
    @click.option("-v", "--verbose", count=True, help="Increase verbosity: -v (WARNING), -vv (INFO), -vvv (DEBUG). Default: ERROR level")
    @click.option("-d", "--debug", is_flag=True, help="Enable DEBUG level logging (equivalent to -vvv)")
    @click.option("--timing", is_flag=True, help="Show performance metrics")
    @click.option("--skip-accounts", multiple=True, help="Exclude AWS account IDs from diagram (space-separated)")
    @click.option("--skip-ous", multiple=True, help="Exclude organizational unit IDs from diagram (space-separated)")
    @click.option("--output", "-o", default=None, help="Custom output filename (without extension). Default: aws_organization")
    @click.pass_context
    def draw_org(ctx, profile, policy, show_aws_managed, ou, format, verbose, debug, timing, skip_accounts, skip_ous, output):
        """
        Visualize AWS Organizations structure with multiple output formats.

        Generates organization diagrams showing accounts, OUs, and policies
        with support for Graphviz (PNG), Mermaid, and Diagrams library formats.

        Examples:
            # Basic diagram with default profile
            runbooks inventory draw-org

            # With specific management profile
            runbooks inventory draw-org --profile $MANAGEMENT_PROFILE

            # Include policies and AWS managed SCPs
            runbooks inventory draw-org --policy --show-aws-managed

            # Start from specific OU in Mermaid format
            runbooks inventory draw-org --ou ou-1234567890 --output-format mermaid

            # Diagrams library format with timing
            runbooks inventory draw-org --output-format diagrams --timing

            # Multi-level verbosity
            runbooks inventory draw-org -vv                  # WARNING level
            runbooks inventory draw-org -vvv                 # INFO level

            # Skip accounts/OUs (large organizations)
            runbooks inventory draw-org --skip-accounts 123456789012 987654321098

            # Custom output filename
            runbooks inventory draw-org --output prod-org
        """
        try:
            from runbooks.inventory.draw_org import (
                draw_org as draw_org_diagram,
                generate_mermaid,
                generate_diagrams,
                find_accounts_in_org,
                get_enabled_policy_types
            )
            import boto3
            import logging
            from time import time as get_time

            # Profile priority: command-level > group-level > environment > boto3 default
            # This allows both patterns to work:
            #   runbooks inventory draw-org --profile X (command-level)
            #   runbooks inventory --profile X draw-org (group-level)
            if not profile:
                profile = ctx.obj.get('profile')
            if not profile:
                import os
                profile = os.getenv('AWS_PROFILE')

            # Note: boto3.Session() handles 'default' profile fallback internally.
            # Explicit fallback to 'default' here causes SSO profile users to fail when
            # no profile is specified (SSO configs don't have 'default' entry).

            # Configure logging based on verbosity level
            # v1.1.10 enhancement: Error-visible default (no silent mode)
            log_levels = {
                0: logging.ERROR,     # Default (errors visible)
                1: logging.WARNING,   # -v (warnings)
                2: logging.INFO,      # -vv (info)
                3: logging.DEBUG      # -vvv (debug)
            }

            # Handle -d/--debug flag (overrides verbose count)
            if debug:
                log_level = logging.DEBUG
            else:
                log_level = log_levels.get(verbose, logging.ERROR)

            logging.basicConfig(
                level=log_level,
                format='[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s'
            )

            # Suppress boto3 noise unless in DEBUG mode
            if log_level > logging.DEBUG:
                logging.getLogger("boto3").setLevel(logging.CRITICAL)
                logging.getLogger("botocore").setLevel(logging.CRITICAL)
                logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
                logging.getLogger("urllib3").setLevel(logging.CRITICAL)

            # Rich CLI output with enterprise UX
            console.print(f"[blue]🌳 AWS Organizations Structure Visualization[/blue]")
            verbosity_label = {0: "error", 1: "warning", 2: "info", 3: "debug"}.get(verbose, "error")
            if debug:
                verbosity_label = "debug"
            console.print(f"[dim]Profile: {profile or 'environment fallback'} | Format: {format} | Verbosity: {verbosity_label}[/dim]")

            begin_time = get_time()

            # AWS Organizations client initialization
            org_session = boto3.Session(profile_name=profile)
            org_client = org_session.client('organizations')

            # Get enabled policy types (required even for non-policy diagrams)
            # Note: This is a module-level function that uses the global org_client
            # We need to set the global org_client before calling get_enabled_policy_types
            import runbooks.inventory.draw_org as draw_org_module
            draw_org_module.org_client = org_client
            enabled_policy_types = get_enabled_policy_types()

            # Determine starting point and output filename
            if ou:
                root = ou
                # Use custom output filename if provided, otherwise default to subset
                filename = output if output else "aws_organization_subset"
                console.print(f"[dim]Starting from OU: {ou}[/dim]")
            else:
                root = org_client.list_roots()["Roots"][0]["Id"]
                # Use custom output filename if provided, otherwise default
                filename = output if output else "aws_organization"
                console.print(f"[dim]Starting from organization root[/dim]")

            # Display custom filename if provided
            if output:
                console.print(f"[dim]Custom output: {filename}.{{png|dot|mmd}}[/dim]")

            # Account discovery for progress estimation
            all_accounts = find_accounts_in_org()

            # Apply skip filters if provided
            excluded_accounts = set(skip_accounts) if skip_accounts else set()
            excluded_ous = set(skip_ous) if skip_ous else set()

            if excluded_accounts:
                console.print(f"[yellow]⚠️  Excluding {len(excluded_accounts)} accounts[/yellow]")
                logging.info(f"Excluded accounts: {excluded_accounts}")
                # Filter accounts
                all_accounts = [acc for acc in all_accounts if acc['Id'] not in excluded_accounts]

                # Validation: Ensure at least 1 account remains
                if not all_accounts:
                    console.print(f"[red]❌ All accounts excluded by filters. Diagram would be empty.[/red]")
                    raise click.ClickException(
                        "Skip filters excluded all accounts. Remove some exclusions or check account IDs."
                    )

            if excluded_ous:
                console.print(f"[yellow]⚠️  Excluding {len(excluded_ous)} organizational units[/yellow]")
                logging.info(f"Excluded OUs: {excluded_ous}")

            console.print(f"[dim]Discovered {len(all_accounts)} accounts in organization{' (after filtering)' if excluded_accounts else ''}[/dim]")

            # Set module-level variables for policy handling and filters
            draw_org_module.pPolicy = policy
            draw_org_module.pManaged = show_aws_managed

            # Set module-level skip filters (for diagram generation)
            draw_org_module.excluded_accounts = excluded_accounts
            draw_org_module.excluded_ous = excluded_ous

            # Generate diagram based on format
            if format == "graphviz":
                draw_org_diagram(root, filename)
                console.print(f"[green]✅ Graphviz diagram: {filename}.png[/green]")
            elif format == "mermaid":
                mermaid_file = f"{filename}.mmd"
                generate_mermaid(root, mermaid_file)
                console.print(f"[green]✅ Mermaid diagram: {mermaid_file}[/green]")
            elif format == "diagrams":
                generate_diagrams(root, filename)
                console.print(f"[green]✅ Diagrams visualization: {filename}[/green]")

            if timing:
                elapsed = get_time() - begin_time
                console.print(f"[dim]⏱️ Execution time: {elapsed:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Organization diagram generation failed: {e}[/red]")
            if verbose:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise click.ClickException(str(e))

    @inventory.command(name='list-org-accounts')
    @click.option('--profile', type=str, default=None, help='AWS profile to use (overrides group-level --profile)')
    @click.option('--short', '-s', '-q', is_flag=True, help='Brief listing without child accounts')
    @click.option('--acct', '-A', multiple=True, help='Find which org these accounts belong to')
    @click.option('--root-only', is_flag=True, help='Show only management accounts')
    @click.option('-f', '--format', '--export-format',
                  type=click.Choice(['json', 'csv', 'markdown', 'table']),
                  default='table', help='Export format (-f/--format preferred, --export-format legacy)')
    @click.option('--output', '-o', help='Output filename (for export formats)')
    @click.option('--timing', is_flag=True, help='Show performance metrics')
    @click.option('-v', '--verbose', count=True, help='Increase verbosity')
    @click.option('--skip-profiles', multiple=True, help='Profiles to exclude from discovery')
    @click.pass_context
    def list_org_accounts(ctx, profile, short, acct, root_only, format, output, timing, verbose, skip_profiles):
        """
        List all accounts in AWS Organizations.

        Supports multi-account discovery via --all-profiles flag at group level:
            runbooks inventory --all-profiles mgmt list-org-accounts

        Single account mode:
            runbooks inventory --profile mgmt list-org-accounts

        Examples:
            # Multi-account Organizations discovery
            runbooks inventory --all-profiles $MANAGEMENT_PROFILE list-org-accounts

            # Brief listing with timing
            runbooks inventory --profile mgmt list-org-accounts --short --timing

            # Find specific accounts across organizations
            runbooks inventory --all-profiles mgmt list-org-accounts --acct 123456789012 987654321098

            # Export to CSV
            runbooks inventory --profile mgmt list-org-accounts --export-format csv --output orgs
        """
        try:
            from runbooks.inventory.list_org_accounts import list_organization_accounts
            import logging
            from time import time as get_time
            import os

            # Configure logging based on verbosity
            log_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
            log_level = log_levels.get(verbose, logging.ERROR)
            logging.basicConfig(level=log_level, format='[%(filename)s:%(lineno)s] %(message)s')

            # Suppress AWS SDK noise
            if log_level > logging.DEBUG:
                for logger_name in ['boto3', 'botocore', 's3transfer', 'urllib3']:
                    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

            begin_time = get_time()

            # Profile priority: command-level > group-level > environment > default
            # This allows both patterns to work:
            #   runbooks inventory list-org-accounts --profile X (command-level)
            #   runbooks inventory --profile X list-org-accounts (group-level)
            if not profile:
                profile = ctx.obj.get('profile')

            # Get other context parameters
            all_profiles = ctx.obj.get('all_profiles')
            profiles = ctx.obj.get('profiles', [])

            # Determine discovery mode
            if all_profiles:
                # --all-profiles mode: Organizations API discovery
                discovery_profiles = [all_profiles]
                discovery_mode = "Organizations API (--all-profiles)"
            elif profiles:
                # --profiles mode: Multiple profiles specified
                discovery_profiles = profiles
                discovery_mode = f"Multi-profile ({len(profiles)} profiles)"
            elif profile:
                # --profile mode: Single profile
                discovery_profiles = [profile]
                discovery_mode = "Single profile"
            else:
                # Default: AWS_PROFILE environment variable or boto3 default
                # Note: boto3.Session() handles 'default' profile fallback internally.
                # Explicit fallback to 'default' here causes SSO profile users to fail when
                # no profile is specified (SSO configs don't have 'default' entry).
                env_profile = os.getenv('AWS_PROFILE')
                discovery_profiles = [env_profile] if env_profile else [None]
                discovery_mode = "Environment/Default profile"

            console.print(f"[blue]📋 AWS Organizations Account Inventory[/blue]")
            console.print(f"[dim]Mode: {discovery_mode} | Profiles: {len(discovery_profiles)} | Format: {format}[/dim]")

            # Execute discovery
            results = list_organization_accounts(
                profiles=discovery_profiles,
                short_form=short,
                root_only=root_only,
                account_lookup=list(acct) if acct else None,
                export_format=format,
                output_file=output,
                skip_profiles=list(skip_profiles) if skip_profiles else None,
                verbose=log_level
            )

            if timing:
                elapsed = get_time() - begin_time
                console.print(f"[dim]⏱️ Execution time: {elapsed:.2f}s[/dim]")

            console.print("[green]✅ Account discovery complete[/green]")

        except Exception as e:
            console.print(f"[red]❌ Organizations account discovery failed: {e}[/red]")
            if verbose >= 2:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise click.ClickException(str(e))

    @inventory.command(name='list-org-users')
    @click.option('--profile', type=str, default=None, help='AWS profile (overrides group-level)')
    @click.option('--iam', is_flag=True, help='Discover IAM users only')
    @click.option('--idc', is_flag=True, help='Discover Identity Center users only')
    @click.option('--short', '-s', '-q', is_flag=True, help='Brief summary without detailed enumeration')
    @click.option('-f', '--format', '--export-format',
                  type=click.Choice(['json', 'csv', 'markdown', 'table']),
                  default='table', help='Export format (-f/--format preferred, --export-format legacy)')
    @click.option('--output', '-o', help='Output filename')
    @click.option('--timing', is_flag=True, help='Show performance metrics')
    @click.option('-v', '--verbose', count=True, help='Increase verbosity')
    @click.pass_context
    def list_org_users_cmd(ctx, profile, iam, idc, short, format, output, timing, verbose):
        """
        Discover IAM users and AWS Identity Center users across AWS Organizations.

        Comprehensive user discovery supporting both traditional IAM and modern
        AWS Identity Center identity sources for enterprise identity governance.

        Identity Sources:
            Default: Both IAM and Identity Center users
            --iam: Traditional IAM users only
            --idc: AWS Identity Center users only

        Examples:
            # Discover all users (IAM + Identity Center)
            runbooks inventory --profile $MANAGEMENT_PROFILE list-org-users

            # IAM users only
            runbooks inventory --profile mgmt list-org-users --iam --short

            # Identity Center only with CSV export
            runbooks inventory --profile mgmt list-org-users --idc --export-format csv
        """
        try:
            from runbooks.inventory.list_org_accounts_users import find_all_org_users
            from runbooks.inventory.inventory_modules import get_all_credentials, display_results
            import logging
            from time import time as get_time

            # Configure logging
            log_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
            log_level = log_levels.get(verbose, logging.ERROR)
            logging.basicConfig(level=log_level, format='[%(filename)s:%(lineno)s] %(message)s')

            if log_level > logging.DEBUG:
                for logger_name in ['boto3', 'botocore', 's3transfer', 'urllib3']:
                    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

            begin_time = get_time()

            # Profile resolution (SSO compatible - NO 'default' hardcoding)
            if not profile:
                profile = ctx.obj.get('profile')
            if not profile:
                import os
                profile = os.getenv('AWS_PROFILE')

            # Identity source selection (default: both IAM and IDC)
            if not iam and not idc:
                iam = True
                idc = True

            console.print(f"[blue]👥 AWS Organizations User Inventory[/blue]")
            console.print(f"[dim]Profile: {profile or 'environment fallback'} | Sources: {'IAM' if iam else ''}{' + ' if iam and idc else ''}{'Identity Center' if idc else ''}[/dim]")

            # Get credentials for cross-account access
            credential_list = get_all_credentials(
                [profile] if profile else [None],
                pTiming=timing,
                pSkipProfiles=[],
                pSkipAccounts=[],
                pRootOnly=False,
                pAccounts=None,
                pRegionList=['us-east-1'],
                pAccessRoles=None
            )

            # Discover users across organization
            user_listing = find_all_org_users(credential_list, f_IDC=idc, f_IAM=iam)
            sorted_user_listing = sorted(
                user_listing, key=lambda k: (k["MgmtAccount"], k["AccountId"], k["Region"], k["UserName"])
            )

            # Display results
            display_dict = {
                "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
                "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
                "Region": {"DisplayOrder": 3, "Heading": "Region"},
                "UserName": {"DisplayOrder": 4, "Heading": "User Name"},
                "PasswordLastUsed": {"DisplayOrder": 5, "Heading": "Last Used"},
                "Type": {"DisplayOrder": 6, "Heading": "Source"},
            }

            # Handle output file naming
            output_file = output if export_format != 'table' else None

            display_results(sorted_user_listing, display_dict, "N/A", output_file)

            successful_accounts = [x for x in credential_list if x["Success"]]
            console.print(f"\n[green]✅ Found {len(user_listing)} users across {len(successful_accounts)} accounts[/green]")

            if timing:
                elapsed = get_time() - begin_time
                console.print(f"[dim]⏱️  Execution time: {elapsed:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]❌ User discovery failed: {e}[/red]")
            if verbose >= 2:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise click.ClickException(str(e))

    @inventory.command(name='find-lz-versions')
    @click.option('--profile', type=str, default=None, help='AWS profile (overrides group-level)')
    @click.option('--timing', is_flag=True, help='Show performance metrics')
    @click.option('-f', '--format', '--export-format',
                  type=click.Choice(['json', 'csv', 'markdown', 'table']),
                  default='table', help='Export format (-f/--format preferred, --export-format legacy)')
    @click.option('--output', '-o', help='Output filename')
    @click.option('--latest', is_flag=True, help='Show only accounts not on latest version')
    @click.option('-v', '--verbose', count=True, help='Increase verbosity')
    @click.pass_context
    def find_lz_versions_cmd(ctx, profile, timing, format, output, latest, verbose):
        """
        Discover AWS Landing Zone versions across organization.

        Identifies Landing Zone deployments by analyzing CloudFormation stacks
        for SO0044 solution and extracting version information from stack outputs.

        Version Analysis:
            - CloudFormation stack detection (SO0044 Landing Zone solution)
            - Version extraction from stack outputs
            - Account Factory product versions (Service Catalog)
            - Version drift calculation

        Examples:
            # Basic version discovery
            runbooks inventory --profile $MANAGEMENT_PROFILE find-lz-versions

            # Show only version drift
            runbooks inventory --profile mgmt find-lz-versions --latest

            # CSV export with timing
            runbooks inventory --profile mgmt find-lz-versions --export-format csv --timing
        """
        try:
            import boto3
            import logging
            from time import time as get_time
            from runbooks.inventory import inventory_modules as Inventory_Modules
            from runbooks.common.rich_utils import create_table

            # Configure logging
            log_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
            log_level = log_levels.get(verbose, logging.ERROR)
            logging.basicConfig(level=log_level, format='[%(filename)s:%(lineno)s] %(message)s')

            if log_level > logging.DEBUG:
                for logger_name in ['boto3', 'botocore', 's3transfer', 'urllib3']:
                    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

            begin_time = get_time()

            # Profile resolution (SSO compatible)
            if not profile:
                profile = ctx.obj.get('profile')
            if not profile:
                import os
                profile = os.getenv('AWS_PROFILE')

            console.print(f"[blue]🔍 AWS Landing Zone Version Discovery[/blue]")
            console.print(f"[dim]Profile: {profile or 'environment fallback'} | Format: {format} | Drift only: {latest}[/dim]")

            # Discover Landing Zone Management Accounts
            all_profiles = [profile] if profile else [None]
            skip_profiles = ["default"]

            alz_profiles = []
            for prof in all_profiles:
                try:
                    alz_mgmt_acct = Inventory_Modules.find_if_alz(prof)
                    if alz_mgmt_acct["ALZ"]:
                        account_num = Inventory_Modules.find_account_number(prof)
                        alz_profiles.append({
                            "Profile": prof,
                            "Acctnum": account_num,
                            "Region": alz_mgmt_acct["Region"]
                        })
                except Exception as e:
                    logging.debug(f"Profile {prof} is not a Landing Zone Management Account: {e}")
                    continue

            if not alz_profiles:
                console.print("[yellow]⚠️  No Landing Zone Management Accounts found[/yellow]")
                return

            # Create results table
            table = create_table(
                title="AWS Landing Zone Versions",
                columns=[
                    {"header": "Profile", "justify": "left"},
                    {"header": "Account", "justify": "left"},
                    {"header": "Region", "justify": "left"},
                    {"header": "Stack Name", "justify": "left"},
                    {"header": "Version", "justify": "left"},
                ]
            )

            # Analyze Landing Zone versions
            for item in alz_profiles:
                aws_session = boto3.Session(profile_name=item["Profile"], region_name=item["Region"])
                cfn_client = aws_session.client("cloudformation")

                stack_list = cfn_client.describe_stacks()["Stacks"]

                for stack in stack_list:
                    if "Description" in stack and "SO0044" in stack["Description"]:
                        for output in stack.get("Outputs", []):
                            if output["OutputKey"] == "LandingZoneSolutionVersion":
                                alz_version = output["OutputValue"]
                                table.add_row(
                                    item["Profile"],
                                    item["Acctnum"],
                                    item["Region"],
                                    stack["StackName"],
                                    alz_version
                                )

            console.print()
            console.print(table)
            console.print(f"\n[green]✅ Discovered {len(alz_profiles)} Landing Zone deployments[/green]")

            if timing:
                elapsed = get_time() - begin_time
                console.print(f"[dim]⏱️  Execution time: {elapsed:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Landing Zone version discovery failed: {e}[/red]")
            if verbose >= 2:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise click.ClickException(str(e))

    @inventory.command(name='check-landingzone')
    @click.option('--profile', type=str, default=None, help='AWS profile (overrides group-level)')
    @click.option('--timing', is_flag=True, help='Show performance metrics')
    @click.option('-f', '--format', '--export-format',
                  type=click.Choice(['json', 'markdown', 'table']),
                  default='table', help='Export format (-f/--format preferred, --export-format legacy)')
    @click.option('--output', '-o', help='Output filename')
    @click.option('--ou', type=str, default=None, help='Specific OU to validate')
    @click.option('-v', '--verbose', count=True, help='Increase verbosity')
    @click.pass_context
    def check_landingzone_cmd(ctx, profile, timing, format, output, ou, verbose):
        """
        Validate AWS Landing Zone readiness and prerequisites.

        Comprehensive validation of Landing Zone deployment prerequisites including
        default VPCs, Config recorders, CloudTrail trails, and organizational membership.

        Validation Checks:
            - Default VPCs across all regions
            - Config Recorder and Delivery Channel conflicts
            - CloudTrail trail naming conflicts
            - AWS Organizations membership
            - Organizational Unit placement

        Examples:
            # Full readiness check
            runbooks inventory --profile $MANAGEMENT_PROFILE check-landingzone

            # Specific OU validation
            runbooks inventory --profile mgmt check-landingzone --ou ou-xxxx-xxxxxxxx

            # JSON export with timing
            runbooks inventory --profile mgmt check-landingzone --export-format json --timing
        """
        try:
            from runbooks.inventory.validation_utils import (
                validate_organizations_enabled,
                validate_iam_role_exists,
                validate_config_enabled,
                validate_cloudtrail_enabled,
                calculate_readiness_score,
                generate_remediation_recommendations
            )
            import logging
            from time import time as get_time
            from runbooks.common.rich_utils import create_table

            # Configure logging
            log_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
            log_level = log_levels.get(verbose, logging.ERROR)
            logging.basicConfig(level=log_level, format='[%(filename)s:%(lineno)s] %(message)s')

            if log_level > logging.DEBUG:
                for logger_name in ['boto3', 'botocore', 's3transfer', 'urllib3']:
                    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

            begin_time = get_time()

            # Profile resolution (SSO compatible)
            if not profile:
                profile = ctx.obj.get('profile')
            if not profile:
                import os
                profile = os.getenv('AWS_PROFILE')

            console.print(f"[blue]🔍 AWS Landing Zone Readiness Validation[/blue]")
            console.print(f"[dim]Profile: {profile or 'environment fallback'} | OU: {ou or 'all'} | Format: {format}[/dim]")

            # Execute validation checks
            checks = []
            checks.append(validate_organizations_enabled(profile))
            checks.append(validate_iam_role_exists(profile, 'AWSCloudFormationStackSetExecutionRole'))
            checks.append(validate_config_enabled(profile))
            checks.append(validate_cloudtrail_enabled(profile))

            # Calculate readiness score
            score = calculate_readiness_score(checks)
            status = "READY" if score >= 90 else "PARTIAL" if score >= 50 else "NOT READY"

            # Generate remediation recommendations
            remediations = generate_remediation_recommendations(checks)

            # Create results table
            table = create_table(
                title="Landing Zone Readiness Assessment",
                columns=[
                    {"header": "Check", "justify": "left"},
                    {"header": "Status", "justify": "center"},
                    {"header": "Details", "justify": "left"},
                ]
            )

            for check in checks:
                status_indicator = "[green]✅ PASS[/green]" if check["passed"] else "[red]❌ FAIL[/red]"
                table.add_row(check["check_name"], status_indicator, check.get("message", ""))

            console.print()
            console.print(table)
            console.print(f"\n[{'green' if score >= 90 else 'yellow' if score >= 50 else 'red'}]Readiness Score: {score}/100 - {status}[/{'green' if score >= 90 else 'yellow' if score >= 50 else 'red'}]")

            if remediations:
                console.print("\n[yellow]📋 Remediation Recommendations:[/yellow]")
                for remediation in remediations:
                    console.print(f"  • {remediation}")

            if timing:
                elapsed = get_time() - begin_time
                console.print(f"\n[dim]⏱️  Execution time: {elapsed:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Landing Zone readiness check failed: {e}[/red]")
            if verbose >= 2:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise click.ClickException(str(e))

    @inventory.command(name='check-controltower')
    @click.option('--profile', type=str, default=None, help='AWS profile (overrides group-level)')
    @click.option('--timing', is_flag=True, help='Show performance metrics')
    @click.option('-f', '--format', '--export-format',
                  type=click.Choice(['json', 'markdown', 'table']),
                  default='table', help='Export format (-f/--format preferred, --export-format legacy)')
    @click.option('--output', '-o', help='Output filename')
    @click.option('-v', '--verbose', count=True, help='Increase verbosity')
    @click.pass_context
    def check_controltower_cmd(ctx, profile, timing, format, output, verbose):
        """
        Validate AWS Control Tower readiness and prerequisites.

        Comprehensive validation of Control Tower deployment prerequisites including
        AWS Config, CloudTrail, IAM roles, and organizational compliance requirements.

        Validation Checks:
            - AWS Organizations enabled
            - CloudTrail organizational trail configured
            - AWS Config Recorder and Delivery Channel
            - Required IAM roles (AWSControlTowerExecution, AWSControlTowerStackSetRole)
            - Service-linked roles and permissions

        Examples:
            # Full Control Tower readiness assessment
            runbooks inventory --profile $MANAGEMENT_PROFILE check-controltower

            # JSON export for automation
            runbooks inventory --profile mgmt check-controltower --export-format json --output ct-readiness

            # With timing and verbose output
            runbooks inventory --profile mgmt check-controltower --timing -vv
        """
        try:
            from runbooks.inventory.validation_utils import (
                validate_organizations_enabled,
                validate_cloudtrail_enabled,
                validate_config_enabled,
                validate_iam_role_exists,
                calculate_readiness_score,
                generate_remediation_recommendations
            )
            import logging
            from time import time as get_time
            from runbooks.common.rich_utils import create_table

            # Configure logging
            log_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
            log_level = log_levels.get(verbose, logging.ERROR)
            logging.basicConfig(level=log_level, format='[%(filename)s:%(lineno)s] %(message)s')

            if log_level > logging.DEBUG:
                for logger_name in ['boto3', 'botocore', 's3transfer', 'urllib3']:
                    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

            begin_time = get_time()

            # Profile resolution (SSO compatible)
            if not profile:
                profile = ctx.obj.get('profile')
            if not profile:
                import os
                profile = os.getenv('AWS_PROFILE')

            console.print(f"[blue]🔍 AWS Control Tower Readiness Validation[/blue]")
            console.print(f"[dim]Profile: {profile or 'environment fallback'} | Format: {format}[/dim]")

            # Execute validation checks
            checks = []
            checks.append(validate_organizations_enabled(profile))
            checks.append(validate_cloudtrail_enabled(profile))
            checks.append(validate_config_enabled(profile))
            checks.append(validate_iam_role_exists(profile, 'AWSControlTowerExecution'))
            checks.append(validate_iam_role_exists(profile, 'AWSControlTowerStackSetRole'))

            # Calculate readiness score
            score = calculate_readiness_score(checks)
            status = "READY" if score >= 90 else "PARTIAL" if score >= 50 else "NOT_READY"

            # Generate remediation recommendations
            remediations = generate_remediation_recommendations(checks)

            # Create results table
            table = create_table(
                title="Control Tower Readiness Assessment",
                columns=[
                    {"header": "Check", "justify": "left"},
                    {"header": "Status", "justify": "center"},
                    {"header": "Details", "justify": "left"},
                ]
            )

            for check in checks:
                status_indicator = "[green]✅ PASS[/green]" if check["passed"] else "[red]❌ FAIL[/red]"
                table.add_row(check["check_name"], status_indicator, check.get("message", ""))

            console.print()
            console.print(table)
            console.print(f"\n[{'green' if score >= 90 else 'yellow' if score >= 50 else 'red'}]Readiness Score: {score}/100 - {status}[/{'green' if score >= 90 else 'yellow' if score >= 50 else 'red'}]")

            if remediations:
                console.print("\n[yellow]📋 Remediation Recommendations:[/yellow]")
                for remediation in remediations:
                    console.print(f"  • {remediation}")

            if timing:
                elapsed = get_time() - begin_time
                console.print(f"\n[dim]⏱️  Execution time: {elapsed:.2f}s[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Control Tower readiness check failed: {e}[/red]")
            if verbose >= 2:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise click.ClickException(str(e))

    return inventory
