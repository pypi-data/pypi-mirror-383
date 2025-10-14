"""
CloudOps & FinOps Runbooks Module - Enterprise Cost and Resource Monitoring

This module provides terminal-based AWS cost monitoring with features including:
- Multi-account cost summaries
- Service-level cost breakdown
- Budget monitoring
- EC2 resource status
- Cost trend analysis
- Audit reporting for optimization opportunities

Integrated as a submodule of CloudOps Runbooks for enterprise FinOps automation.
"""

# Import centralized version from main runbooks package
from runbooks import __version__

# Core components
# AWS client utilities
from runbooks.finops.aws_client import (
    ec2_summary,
    get_accessible_regions,
    get_account_id,
    get_aws_profiles,
    get_budgets,
    get_stopped_instances,
    get_untagged_resources,
    get_unused_eips,
    get_unused_volumes,
)

# Data processors
from runbooks.finops.cost_processor import export_to_csv, export_to_json, get_cost_data, get_trend

# Enterprise FinOps Dashboard Components - Using consolidated dashboard_runner.py
# Backward compatibility for legacy tests and components
from runbooks.finops.dashboard_runner import (
    FinOpsConfig,
    _run_audit_report,
    _run_cost_trend_analysis,
    _run_executive_dashboard,
    _run_resource_heatmap_analysis,
    run_complete_finops_workflow,
    run_dashboard,
)

# Enhanced helpers with notebook integration functions
from runbooks.finops.helpers import (
    create_business_summary_table,
    create_roi_analysis_table,
    export_audit_report_to_csv,
    export_audit_report_to_json,
    export_audit_report_to_pdf,
    export_cost_dashboard_to_pdf,
    export_scenarios_to_notebook_html,
    export_trend_data_to_json,
    # NOTEBOOK INTEGRATION FUNCTIONS - Added for clean notebook consumption
    format_currency,
    load_config_file,
)
from runbooks.finops.profile_processor import process_combined_profiles, process_single_profile

# Business scenarios with notebook integration
# NEW latest version: Clean API wrapper for notebook consumption
from runbooks.finops.scenarios import (
    UnifiedScenarioManager,  # Replaces FinOpsBusinessScenarios
    create_business_scenarios_validated,
    display_unlimited_scenarios_help,  # CLI help function
    finops_23_rds_snapshots_optimization,
    # Legacy aliases for backward compatibility
    finops_24_workspaces_cleanup,
    finops_25_commvault_investigation,
    finops_commvault,
    finops_snapshots,
    finops_workspaces,
    format_for_audience,  # Consolidated function replaces format_for_business_audience and format_for_technical_audience
    get_business_scenarios_summary,
    validate_finops_mcp_accuracy,
)

# Type definitions
from runbooks.finops.types import BudgetInfo, CostData, EC2Summary, ProfileData, RegionName

# Visualization and export
from runbooks.finops.visualisations import create_trend_bars

__all__ = [
    # Core functionality
    "run_dashboard",
    "run_complete_finops_workflow",
    # Enterprise FinOps Dashboard Functions
    "_run_audit_report",
    "_run_cost_trend_analysis",
    "_run_resource_heatmap_analysis",
    "_run_executive_dashboard",
    # Enterprise Dashboard Classes - backward compatibility
    "FinOpsConfig",
    # Business scenarios with notebook integration (consolidated version)
    "create_business_scenarios_validated",
    "format_for_audience",  # Consolidated function
    "UnifiedScenarioManager",  # Consolidated class
    # NEW latest version: Clean API wrapper functions (cleaned naming)
    "finops_workspaces",
    "finops_snapshots",
    "finops_commvault",
    # Legacy aliases (deprecated)
    "finops_24_workspaces_cleanup",
    "finops_23_rds_snapshots_optimization",
    "finops_25_commvault_investigation",
    "get_business_scenarios_summary",
    "format_for_audience",
    "validate_finops_mcp_accuracy",  # Updated function name in consolidated version
    "display_unlimited_scenarios_help",  # CLI help function
    # Processors
    "get_cost_data",
    "get_trend",
    "process_single_profile",
    "process_combined_profiles",
    # AWS utilities
    "get_aws_profiles",
    "get_account_id",
    "get_accessible_regions",
    "ec2_summary",
    "get_stopped_instances",
    "get_unused_volumes",
    "get_unused_eips",
    "get_untagged_resources",
    "get_budgets",
    # Visualization and export
    "create_trend_bars",
    "export_to_csv",
    "export_to_json",
    "export_audit_report_to_pdf",
    "export_cost_dashboard_to_pdf",
    "export_audit_report_to_csv",
    "export_audit_report_to_json",
    "export_trend_data_to_json",
    "load_config_file",
    # NOTEBOOK INTEGRATION FUNCTIONS (latest version)
    "format_currency",
    "create_business_summary_table",
    "export_scenarios_to_notebook_html",
    "create_roi_analysis_table",
    # Types
    "ProfileData",
    "CostData",
    "BudgetInfo",
    "EC2Summary",
    "RegionName",
    # Metadata
    "__version__",
]
