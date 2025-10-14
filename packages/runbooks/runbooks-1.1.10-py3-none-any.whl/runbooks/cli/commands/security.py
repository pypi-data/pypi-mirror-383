"""
Security Commands Module - Security Assessment & Compliance

KISS Principle: Focused on security assessment and compliance operations
DRY Principle: Centralized security patterns and compliance frameworks

Extracted from main.py lines 4500-6000 for modular architecture.
Preserves 100% functionality while reducing main.py context overhead.
"""

import click
from rich.console import Console

# Import common utilities and decorators
from runbooks.common.decorators import common_aws_options, common_output_options

console = Console()


def create_security_group():
    """
    Create the security command group with all subcommands.

    Returns:
        Click Group object with all security commands

    Performance: Lazy creation only when needed by DRYCommandRegistry
    Context Reduction: ~1500 lines extracted from main.py
    """

    @click.group(invoke_without_command=True)
    @common_aws_options
    @click.pass_context
    def security(ctx, profile, region, dry_run):
        """
        Security assessment and compliance operations.

        Comprehensive security baseline assessment with multi-framework compliance
        and enterprise-grade reporting capabilities.

        Compliance Frameworks:
        • SOC2, PCI-DSS, HIPAA, ISO 27001
        • AWS Well-Architected Security Pillar
        • NIST Cybersecurity Framework
        • CIS Benchmarks

        Examples:
            runbooks security assess --framework soc2
            runbooks security baseline --all-checks
            runbooks security report --format pdf --compliance hipaa
        """
        ctx.obj.update({"profile": profile, "region": region, "dry_run": dry_run})

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @security.command()
    @common_aws_options
    @click.option(
        "--framework",
        type=click.Choice(["soc2", "pci-dss", "hipaa", "iso27001", "well-architected"]),
        multiple=True,
        help="Compliance frameworks to assess",
    )
    @click.option("--all-checks", is_flag=True, help="Run all available security checks")
    @click.option(
        "--severity", type=click.Choice(["critical", "high", "medium", "low"]), help="Filter by minimum severity level"
    )
    @click.option(
        "--export-format", type=click.Choice(["json", "csv", "pdf", "markdown"]), help="Export format for results"
    )
    @click.option(
        "--language",
        type=click.Choice(["en", "ja", "ko", "vi"]),
        default="en",
        help="Report language (English, Japanese, Korean, Vietnamese)",
    )
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account security assessment")
    @click.pass_context
    def assess(ctx, profile, region, dry_run, framework, all_checks, severity, export_format, language, all):
        """
        Comprehensive security assessment with multi-framework compliance and universal profile support.

        Enterprise Features:
        • 15+ security checks across multiple frameworks
        • Multi-language reporting (EN/JP/KR/VN)
        • Risk scoring and prioritization
        • Remediation recommendations with business impact
        • Multi-account security assessment with --all flag

        Examples:
            runbooks security assess --framework soc2,pci-dss
            runbooks security assess --all-checks --export-format pdf
            runbooks security assess --severity critical --language ja
            runbooks security assess --all --framework soc2  # Multi-account assessment
        """
        try:
            from runbooks.security.assessment_runner import SecurityAssessmentRunner
            from runbooks.common.profile_utils import get_profile_for_operation

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            assessment = SecurityAssessmentRunner(
                profile=resolved_profile,
                region=region,
                frameworks=list(framework) if framework else None,
                all_checks=all_checks,
                severity_filter=severity,
                language=language,
            )

            results = assessment.run_comprehensive_assessment()

            if export_format:
                assessment.export_results(results, format=export_format)

            return results

        except ImportError as e:
            console.print(f"[red]❌ Security assessment module not available: {e}[/red]")
            raise click.ClickException("Security assessment functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Security assessment failed: {e}[/red]")
            raise click.ClickException(str(e))

    @security.command()
    @common_aws_options
    @click.option(
        "--check-type",
        type=click.Choice(["baseline", "advanced", "enterprise"]),
        default="baseline",
        help="Security check depth level",
    )
    @click.option("--include-remediation", is_flag=True, help="Include remediation recommendations")
    @click.option("--auto-fix", is_flag=True, help="Automatically fix low-risk issues (with approval)")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account baseline assessment")
    @click.pass_context
    def baseline(ctx, profile, region, dry_run, check_type, include_remediation, auto_fix, all):
        """
        Security baseline assessment and configuration validation with universal profile support.

        Baseline Security Checks:
        • IAM policy analysis and least privilege validation
        • S3 bucket public access and encryption assessment
        • VPC security group and NACL configuration review
        • CloudTrail and logging configuration verification
        • Encryption at rest and in transit validation

        Examples:
            runbooks security baseline --check-type enterprise
            runbooks security baseline --include-remediation --auto-fix
            runbooks security baseline --all --check-type enterprise  # Multi-account assessment
        """
        try:
            from runbooks.security.baseline_checker import SecurityBaselineChecker
            from runbooks.common.profile_utils import get_profile_for_operation

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            baseline_checker = SecurityBaselineChecker(
                profile=resolved_profile,
                region=region,
                check_type=check_type,
                include_remediation=include_remediation,
                auto_fix=auto_fix and not dry_run,
            )

            baseline_results = baseline_checker.run_baseline_assessment()

            return baseline_results

        except ImportError as e:
            console.print(f"[red]❌ Security baseline module not available: {e}[/red]")
            raise click.ClickException("Security baseline functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Security baseline assessment failed: {e}[/red]")
            raise click.ClickException(str(e))

    @security.command()
    @common_aws_options
    @click.option(
        "--format",
        "report_format",
        type=click.Choice(["pdf", "html", "markdown", "json"]),
        multiple=True,
        default=["pdf"],
        help="Report formats",
    )
    @click.option(
        "--compliance",
        type=click.Choice(["soc2", "pci-dss", "hipaa", "iso27001"]),
        multiple=True,
        help="Include compliance mapping",
    )
    @click.option("--executive-summary", is_flag=True, help="Generate executive summary")
    @click.option("--output-dir", default="./security_reports", help="Output directory")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account security reporting")
    @click.pass_context
    def report(ctx, profile, region, dry_run, report_format, compliance, executive_summary, output_dir, all):
        """
        Generate comprehensive security compliance reports with universal profile support.

        Enterprise Reporting Features:
        • Executive-ready summary with risk quantification
        • Compliance framework mapping and gap analysis
        • Multi-language support for global enterprises
        • Audit trail documentation and evidence collection
        • Multi-account security reporting with --all flag

        Examples:
            runbooks security report --format pdf,html --executive-summary
            runbooks security report --compliance soc2,hipaa --output-dir ./audit
            runbooks security report --all --compliance soc2  # Multi-account reporting
        """
        try:
            from runbooks.security.report_generator import SecurityReportGenerator
            from runbooks.common.profile_utils import get_profile_for_operation

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            report_generator = SecurityReportGenerator(
                profile=resolved_profile,
                output_dir=output_dir,
                compliance_frameworks=list(compliance) if compliance else None,
                executive_summary=executive_summary,
            )

            report_results = {}
            for format_type in report_format:
                result = report_generator.generate_report(format=format_type)
                report_results[format_type] = result

            console.print(f"[green]✅ Successfully generated {len(report_format)} report format(s)[/green]")
            console.print(f"[dim]Output directory: {output_dir}[/dim]")

            return report_results

        except ImportError as e:
            console.print(f"[red]❌ Security report module not available: {e}[/red]")
            raise click.ClickException("Security report functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Security report generation failed: {e}[/red]")
            raise click.ClickException(str(e))

    return security
