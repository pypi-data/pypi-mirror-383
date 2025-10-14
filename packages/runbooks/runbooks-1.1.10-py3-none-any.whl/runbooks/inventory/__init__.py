"""
Enterprise AWS Inventory System.

This module provides comprehensive AWS resource discovery and inventory
capabilities across multiple accounts and regions with enterprise-grade
architecture, validation, and automation.

Architecture:
    - core/: Main business logic and orchestration
    - collectors/: Specialized resource collectors by service category
    - models/: Pydantic data models with validation
    - utils/: Reusable utilities and helpers
    - legacy/: Deprecated scripts for backward compatibility

Components:
    - InventoryCollector: Main orchestration engine
    - InventoryFormatter: Multi-format output handling
    - BaseResourceCollector: Abstract base for all collectors
    - AWSResource/AWSAccount: Core data models
    - Validation utilities and AWS helpers
"""

# Core components
# Base collector for extending
from runbooks.inventory.collectors.base import BaseResourceCollector
from runbooks.inventory.core.collector import InventoryCollector
from runbooks.inventory.core.formatter import InventoryFormatter

# Enhanced collector integrated into core collector module
from runbooks.inventory.core.collector import (
    EnhancedInventoryCollector,
)

# Data models
from runbooks.inventory.models.account import AWSAccount, OrganizationAccount
from runbooks.inventory.models.inventory import InventoryMetadata, InventoryResult
from runbooks.inventory.models.resource import AWSResource, ResourceState, ResourceType
from runbooks.inventory.utils.aws_helpers import get_boto3_session, validate_aws_credentials

# Utilities
from runbooks.inventory.utils.validation import validate_aws_account_id, validate_resource_types

# VPC Module Migration Integration
from runbooks.inventory.vpc_analyzer import VPCAnalyzer, VPCDiscoveryResult, AWSOAnalysis

# Note: EnhancedInventoryCollector now imported above from core.collector

# Import centralized version from main runbooks package
from runbooks import __version__

__all__ = [
    # Core functionality
    "InventoryCollector",
    "InventoryFormatter",
    # Enhanced functionality with proven finops patterns
    "EnhancedInventoryCollector",
    # Base classes for extension
    "BaseResourceCollector",
    # Data models
    "AWSAccount",
    "OrganizationAccount",
    "AWSResource",
    "InventoryResult",
    "InventoryMetadata",
    # Enums
    "ResourceState",
    "ResourceType",
    # Utilities
    "validate_aws_account_id",
    "validate_resource_types",
    "get_boto3_session",
    "validate_aws_credentials",
    # VPC Module Migration Integration
    "VPCAnalyzer",
    "VPCDiscoveryResult",
    "AWSOAnalysis",
    # Version
    "__version__",
]
