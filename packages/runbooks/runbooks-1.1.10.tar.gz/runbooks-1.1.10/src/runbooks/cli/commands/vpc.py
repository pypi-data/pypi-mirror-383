"""
VPC Commands Module - Network Operations & Cost Optimization

KISS Principle: Focused on VPC networking operations and cost optimization
DRY Principle: Centralized networking patterns and cost analysis

Extracted from main.py lines 7500-9000 for modular architecture.
Preserves 100% functionality while reducing main.py context overhead.
"""

import click

# Import common utilities and decorators
from runbooks.common.decorators import common_aws_options, common_output_options
from runbooks.common.rich_utils import Console

console = Console()


def create_vpc_group():
    """
    Create the vpc command group with all subcommands.

    Returns:
        Click Group object with all vpc commands

    Performance: Lazy creation only when needed by DRYCommandRegistry
    Context Reduction: ~1500 lines extracted from main.py
    """

    @click.group(invoke_without_command=True)
    @common_aws_options
    @click.pass_context
    def vpc(ctx, profile, region, dry_run):
        """
        VPC networking operations and cost optimization.

        Comprehensive VPC analysis, network cost optimization, and topology
        management with enterprise-grade safety and reporting capabilities.

        Network Operations:
        • VPC cost analysis and optimization recommendations
        • NAT Gateway rightsizing and cost reduction
        • Network topology analysis and security assessment
        • Multi-account network discovery and management

        Examples:
            runbooks vpc analyze --cost-optimization
            runbooks vpc nat-gateway --analyze --savings-target 0.3
            runbooks vpc topology --export-format pdf
        """
        ctx.obj.update({"profile": profile, "region": region, "dry_run": dry_run})

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @vpc.command()
    @common_aws_options
    @common_output_options
    @click.option("--cost-optimization", is_flag=True, help="Include cost optimization analysis")
    @click.option("--topology-analysis", is_flag=True, help="Include network topology analysis")
    @click.option("--security-assessment", is_flag=True, help="Include security configuration review")
    @click.option(
        "--savings-target",
        type=click.FloatRange(0.1, 0.8),
        default=0.3,
        help="Target savings percentage for optimization",
    )
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account VPC analysis")
    @click.option(
        "--config",
        type=click.Path(exists=True),
        help="Path to YAML campaign configuration file (config-driven analysis)",
    )
    @click.pass_context
    def analyze(
        ctx,
        profile,
        region,
        dry_run,
        output_format,
        output_file,
        cost_optimization,
        topology_analysis,
        security_assessment,
        savings_target,
        all,
        config,
    ):
        """
        Comprehensive VPC analysis with cost optimization and security assessment with universal profile support.

        Enterprise Analysis Features:
        • Network cost analysis with optimization recommendations
        • Security group and NACL configuration review
        • NAT Gateway and VPC endpoint optimization
        • Multi-account network topology mapping
        • Cross-account VPC analysis with --all flag
        • Config-driven campaign analysis with --config (NEW)

        Examples:
            runbooks vpc analyze --cost-optimization --savings-target 0.25
            runbooks vpc analyze --topology-analysis --security-assessment
            runbooks vpc analyze --export-format pdf --cost-optimization
            runbooks vpc analyze --all --cost-optimization  # Multi-account analysis
            runbooks vpc analyze --config campaign.yaml --profile billing-profile  # Config-driven campaign
        """
        try:
            from runbooks.common.profile_utils import get_profile_for_operation
            from runbooks.common.rich_utils import handle_output_format

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            # NEW: Config-driven campaign analysis
            if config:
                from runbooks.vpc import VPCCleanupFramework
                from runbooks.vpc.cleanup_wrapper import display_config_campaign_results

                cleanup_framework = VPCCleanupFramework(profile=resolved_profile, region=region, safety_mode=True)

                results = cleanup_framework.analyze_from_config(config)
                display_config_campaign_results(results)

                # Export if requested
                if output_file:
                    handle_output_format(
                        data=results,
                        output_format=output_format,
                        output_file=output_file,
                        title=f"Campaign {results.get('campaign_metadata', {}).get('campaign_id', 'Unknown')} Results",
                    )

                return results

            # EXISTING: Standard VPC analysis (unchanged)
            from runbooks.vpc.analyzer import VPCAnalyzer

            analyzer = VPCAnalyzer(
                profile=resolved_profile,
                region=region,
                cost_optimization=cost_optimization,
                topology_analysis=topology_analysis,
                security_assessment=security_assessment,
                savings_target=savings_target,
            )

            analysis_results = analyzer.run_comprehensive_analysis()

            # Use unified format handling
            handle_output_format(
                data=analysis_results,
                output_format=output_format,
                output_file=output_file,
                title="VPC Analysis Results",
            )

            return analysis_results

        except ImportError as e:
            console.print(f"[red]❌ VPC analyzer module not available: {e}[/red]")
            raise click.ClickException("VPC analysis functionality not available")
        except Exception as e:
            console.print(f"[red]❌ VPC analysis failed: {e}[/red]")
            raise click.ClickException(str(e))

    @vpc.command("nat-gateway")
    @common_aws_options
    @common_output_options
    @click.option("--analyze", is_flag=True, help="Analyze NAT Gateway usage and costs")
    @click.option("--optimize", is_flag=True, help="Generate optimization recommendations")
    @click.option("--savings-target", type=click.FloatRange(0.1, 0.8), default=0.3, help="Target savings percentage")
    @click.option("--include-alternatives", is_flag=True, help="Include NAT instance alternatives")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account NAT Gateway analysis")
    @click.pass_context
    def nat_gateway_operations(
        ctx,
        profile,
        region,
        dry_run,
        output_format,
        output_file,
        analyze,
        optimize,
        savings_target,
        include_alternatives,
        all,
    ):
        """
        NAT Gateway cost analysis and optimization recommendations with universal profile support.

        NAT Gateway Optimization Features:
        • Usage pattern analysis and rightsizing recommendations
        • Cost comparison with NAT instances and VPC endpoints
        • Multi-AZ deployment optimization
        • Business impact assessment and implementation timeline
        • Multi-account NAT Gateway optimization with --all flag

        Examples:
            runbooks vpc nat-gateway --analyze --savings-target 0.4
            runbooks vpc nat-gateway --optimize --include-alternatives
            runbooks vpc nat-gateway --analyze --export-format pdf
            runbooks vpc nat-gateway --all --analyze  # Multi-account analysis
        """
        try:
            from runbooks.vpc.nat_gateway_optimizer import NATGatewayOptimizer
            from runbooks.common.profile_utils import get_profile_for_operation
            from runbooks.common.rich_utils import handle_output_format

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            optimizer = NATGatewayOptimizer(
                profile=resolved_profile,
                region=region,
                analyze=analyze,
                optimize=optimize,
                savings_target=savings_target,
                include_alternatives=include_alternatives,
            )

            optimization_results = optimizer.run_nat_gateway_optimization()

            # Use unified format handling
            handle_output_format(
                data=optimization_results,
                output_format=output_format,
                output_file=output_file,
                title="NAT Gateway Optimization Results",
            )

            return optimization_results

        except ImportError as e:
            console.print(f"[red]❌ NAT Gateway optimizer module not available: {e}[/red]")
            raise click.ClickException("NAT Gateway optimization functionality not available")
        except Exception as e:
            console.print(f"[red]❌ NAT Gateway optimization failed: {e}[/red]")
            raise click.ClickException(str(e))

    @vpc.command()
    @common_aws_options
    @common_output_options
    @click.option("--include-costs", is_flag=True, help="Include cost analysis in topology")
    @click.option(
        "--detail-level",
        type=click.Choice(["basic", "detailed", "comprehensive"]),
        default="detailed",
        help="Topology detail level",
    )
    @click.option("--output-dir", default="./vpc_topology", help="Output directory")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account topology generation")
    @click.pass_context
    def topology(
        ctx, profile, region, dry_run, output_format, output_file, include_costs, detail_level, output_dir, all
    ):
        """
        Generate network topology diagrams with cost correlation and universal profile support.

        Topology Analysis Features:
        • Visual network topology with cost overlay
        • Security group and routing visualization
        • Multi-account network relationships
        • Cost flow analysis and optimization opportunities
        • Cross-account topology generation with --all flag

        Examples:
            runbooks vpc topology --include-costs --export-format pdf
            runbooks vpc topology --detail-level comprehensive
            runbooks vpc topology --all --include-costs  # Multi-account topology
        """
        try:
            from runbooks.vpc.topology_generator import NetworkTopologyGenerator
            from runbooks.common.profile_utils import get_profile_for_operation
            from runbooks.common.rich_utils import handle_output_format

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            topology_generator = NetworkTopologyGenerator(
                profile=resolved_profile,
                region=region,
                include_costs=include_costs,
                detail_level=detail_level,
                output_dir=output_dir,
            )

            topology_results = topology_generator.generate_network_topology()

            # Use unified format handling
            handle_output_format(
                data=topology_results,
                output_format=output_format,
                output_file=output_file,
                title="Network Topology Analysis",
            )

            console.print(f"[green]✅ Network topology generated successfully[/green]")
            console.print(f"[dim]Output directory: {output_dir}[/dim]")

            return topology_results

        except ImportError as e:
            console.print(f"[red]❌ VPC topology module not available: {e}[/red]")
            raise click.ClickException("VPC topology functionality not available")
        except Exception as e:
            console.print(f"[red]❌ VPC topology generation failed: {e}[/red]")
            raise click.ClickException(str(e))

    return vpc
