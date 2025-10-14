"""
VPC Networking Operations Module

This module provides comprehensive VPC networking analysis and optimization capabilities
with support for both CLI and Jupyter notebook interfaces using Rich for beautiful outputs.

Key Components:
- VPCNetworkingWrapper: Main interface for all VPC operations
- VPCManagerInterface: Business-friendly interface for non-technical users
- NetworkingCostEngine: Cost analysis and optimization engine
- NetworkingCostHeatMapEngine: Heat map generation for cost visualization
- Rich formatters: Consistent, beautiful output formatting

Usage:
    CLI: runbooks vpc analyze --profile aws-profile
    Jupyter: from runbooks.vpc import VPCNetworkingWrapper
    Manager Dashboard: from runbooks.vpc import VPCManagerInterface
"""

from .cost_engine import NetworkingCostEngine
from .heatmap_engine import NetworkingCostHeatMapEngine
from .manager_interface import BusinessRecommendation, ManagerDashboardConfig, VPCManagerInterface
from .networking_wrapper import VPCNetworkingWrapper
from .rich_formatters import display_cost_table, display_heatmap, display_optimization_recommendations
from .vpc_cleanup_integration import VPCCleanupFramework, VPCCleanupCandidate, VPCCleanupRisk, VPCCleanupPhase
from .cleanup_wrapper import (
    VPCCleanupCLI,
    analyze_cleanup_candidates,
    validate_cleanup_safety,
    generate_business_report,
)
from .runbooks_adapter import RunbooksAdapter
from .nat_gateway_optimizer import NATGatewayOptimizer

__all__ = [
    "VPCNetworkingWrapper",
    "VPCManagerInterface",
    "BusinessRecommendation",
    "ManagerDashboardConfig",
    "NetworkingCostEngine",
    "NetworkingCostHeatMapEngine",
    "display_cost_table",
    "display_heatmap",
    "display_optimization_recommendations",
    "VPCCleanupFramework",
    "VPCCleanupCandidate",
    "VPCCleanupRisk",
    "VPCCleanupPhase",
    "VPCCleanupCLI",
    "analyze_cleanup_candidates",
    "validate_cleanup_safety",
    "generate_business_report",
    "RunbooksAdapter",
    "NATGatewayOptimizer",
]

# Import centralized version from main runbooks package
from runbooks import __version__
