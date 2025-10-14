#!/usr/bin/env python3
"""
Output formatting utilities for Organizations module.

This module provides consistent multi-format export capabilities for
Organizations inventory scripts supporting JSON, CSV, Markdown, and
Rich table formats.

Features:
    - Rich table formatting with CloudOps theme
    - Multi-format export (JSON, CSV, Markdown, Table)
    - Account metadata formatting utilities
    - Organizations hierarchy visualization helpers

Author: CloudOps Runbooks Team
Version: 1.1.10
"""

import csv
import json
import logging
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.table import Table

from runbooks.common.rich_utils import console, create_table, print_error, print_success
from runbooks.common.config_loader import get_config_loader

logger = logging.getLogger(__name__)


class OrganizationsFormatter:
    """Format Organizations data for various output types."""

    @staticmethod
    def format_accounts_table(accounts: List[Dict], title: str = "AWS Organization Accounts") -> Table:
        """
        Create Rich table for accounts listing.

        Args:
            accounts: List of account dictionaries with keys:
                - id: Account ID
                - name: Account name
                - email: Email address
                - status: Account status
                - profile: Mapped profile name
            title: Table title

        Returns:
            Rich Table object with CloudOps theme
        """
        table = create_table(
            title=title,
            columns=[
                {"name": "Account ID", "style": "cyan", "justify": "left"},
                {"name": "Account Name", "style": "white", "justify": "left"},
                {"name": "Email", "style": "dim", "justify": "left"},
                {"name": "Status", "style": "green", "justify": "center"},
                {"name": "Profile", "style": "yellow", "justify": "left"},
            ],
        )

        for account in accounts:
            # Color status based on value
            status = account.get("status", "UNKNOWN")
            status_style = "green" if status == "ACTIVE" else "red"
            status_display = f"[{status_style}]{status}[/{status_style}]"

            table.add_row(
                account.get("id", ""),
                account.get("name", ""),
                account.get("email", ""),
                status_display,
                account.get("profile", ""),
            )

        return table

    @staticmethod
    def export_json(accounts: List[Dict], output_file: str, metadata: Optional[Dict] = None) -> None:
        """
        Export accounts to JSON format with config-aware 14+ columns.

        Args:
            accounts: List of account dictionaries
            output_file: Output file path
            metadata: Optional metadata to include in export

        Raises:
            IOError: If file write fails
        """
        try:
            # Load tag mappings for field names (optional metadata)
            config_loader = get_config_loader()
            tag_mappings = config_loader.load_tag_mappings()

            # Enhanced accounts with all tiers
            enhanced_accounts = []
            for account in accounts:
                enhanced_account = {
                    # Baseline fields (9 columns - unchanged for backward compatibility)
                    'id': account.get('id'),
                    'name': account.get('name'),
                    'email': account.get('email'),
                    'status': account.get('status'),
                    'joined_method': account.get('joined_method'),
                    'joined_timestamp': account.get('joined_timestamp'),
                    'organizational_unit': account.get('organizational_unit'),
                    'organizational_unit_id': account.get('organizational_unit_id'),
                    'parent_id': account.get('parent_id'),

                    # TIER 1: Business Metadata (config-aware)
                    'wbs_code': account.get('wbs_code', 'N/A'),
                    'cost_group': account.get('cost_group', 'N/A'),
                    'technical_lead': account.get('technical_lead', 'N/A'),
                    'account_owner': account.get('account_owner', 'N/A'),

                    # TIER 2: Governance Metadata (config-aware)
                    'business_unit': account.get('business_unit', 'N/A'),
                    'functional_area': account.get('functional_area', 'N/A'),
                    'managed_by': account.get('managed_by', 'N/A'),
                    'product_owner': account.get('product_owner', 'N/A'),

                    # TIER 3: Operational Metadata (config-aware)
                    'purpose': account.get('purpose', 'N/A'),
                    'environment': account.get('environment', 'N/A'),
                    'compliance_scope': account.get('compliance_scope', 'N/A'),
                    'data_classification': account.get('data_classification', 'N/A'),

                    # TIER 4: Extended Metadata (optional, config-aware)
                    'project_name': account.get('project_name', 'N/A'),
                    'budget_code': account.get('budget_code', 'N/A'),
                    'support_tier': account.get('support_tier', 'N/A'),
                    'created_date': account.get('created_date', 'N/A'),
                    'expiry_date': account.get('expiry_date', 'N/A'),

                    # Computed fields (if present)
                    'all_tags': account.get('all_tags', {}),
                    'wbs_comparison': account.get('wbs_comparison', {}),
                }

                # Preserve any additional fields from source (forward compatibility)
                for key in account:
                    if key not in enhanced_account:
                        enhanced_account[key] = account[key]

                enhanced_accounts.append(enhanced_account)

            output_data = {"accounts": enhanced_accounts}

            if metadata:
                output_data["metadata"] = metadata

            # Add tag mapping metadata for reference
            output_data["tag_mappings_used"] = tag_mappings
            output_data["config_sources"] = config_loader.get_config_sources()

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print_success(f"Exported {len(accounts)} accounts to {output_file} (JSON, {len(enhanced_accounts[0])} fields)")

        except Exception as e:
            error_msg = f"Failed to export JSON: {str(e)}"
            logger.error(error_msg)
            print_error(error_msg)
            raise IOError(error_msg) from e

    @staticmethod
    def export_csv(accounts: List[Dict], output_file: str, include_header: bool = True) -> None:
        """
        Export accounts to CSV format with config-aware 14+ columns.

        Args:
            accounts: List of account dictionaries
            output_file: Output file path
            include_header: Include CSV header row

        Raises:
            IOError: If file write fails
        """
        if not accounts:
            logger.warning("No accounts to export to CSV")
            return

        try:
            # Define CSV headers (all tiers in priority order)
            headers = [
                # Baseline fields (9 columns)
                'id', 'name', 'email', 'status', 'joined_method', 'joined_timestamp',
                'organizational_unit', 'organizational_unit_id', 'parent_id',
                # TIER 1: Business Metadata
                'wbs_code', 'cost_group', 'technical_lead', 'account_owner',
                # TIER 2: Governance Metadata
                'business_unit', 'functional_area', 'managed_by', 'product_owner',
                # TIER 3: Operational Metadata
                'purpose', 'environment', 'compliance_scope', 'data_classification',
                # TIER 4: Extended Metadata (optional)
                'project_name', 'budget_code', 'support_tier', 'created_date', 'expiry_date'
            ]

            with open(output_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')

                if include_header:
                    writer.writeheader()

                # Write rows with N/A for missing fields
                for account in accounts:
                    row_data = {header: account.get(header, 'N/A') for header in headers}
                    writer.writerow(row_data)

            print_success(f"Exported {len(accounts)} accounts to {output_file} (CSV, {len(headers)} columns)")

        except Exception as e:
            error_msg = f"Failed to export CSV: {str(e)}"
            logger.error(error_msg)
            print_error(error_msg)
            raise IOError(error_msg) from e

    @staticmethod
    def export_markdown(accounts: List[Dict], output_file: str, title: str = "AWS Organization Accounts") -> None:
        """
        Export accounts to Markdown table format with config-aware 14+ columns.

        Args:
            accounts: List of account dictionaries
            output_file: Output file path
            title: Markdown document title

        Raises:
            IOError: If file write fails
        """
        if not accounts:
            logger.warning("No accounts to export to Markdown")
            return

        try:
            # Load config for metadata
            config_loader = get_config_loader()
            tag_mappings = config_loader.load_tag_mappings()

            # Priority columns for markdown display (top 12 most important)
            display_columns = [
                'id', 'name', 'status', 'email',
                'wbs_code', 'cost_group', 'technical_lead',
                'business_unit', 'environment',
                'organizational_unit', 'managed_by', 'purpose'
            ]

            with open(output_file, "w", encoding="utf-8") as f:
                # Write title
                f.write(f"# {title}\n\n")

                # Write metadata
                f.write("## Configuration Details\n\n")
                f.write(f"**Config Sources**: {' → '.join(config_loader.get_config_sources())}\n\n")
                f.write(f"**Tag Mappings**: {len(tag_mappings)} fields configured\n\n")

                # Write table header (display columns only)
                header_names = [col.replace('_', ' ').title() for col in display_columns]
                f.write("| " + " | ".join(header_names) + " |\n")
                f.write("| " + " | ".join(["---"] * len(display_columns)) + " |\n")

                # Write table rows
                for account in accounts:
                    values = [str(account.get(col, 'N/A')) for col in display_columns]
                    # Truncate long values for readability
                    values = [v[:50] + '...' if len(v) > 50 else v for v in values]
                    f.write("| " + " | ".join(values) + " |\n")

                # Write summary
                f.write(f"\n**Total Accounts:** {len(accounts)}\n")
                f.write(f"\n**Display Columns:** {len(display_columns)} (showing most important fields)\n")
                f.write(f"\n**Full Export:** Use JSON/CSV format for complete {len(accounts[0])} field export\n")

            print_success(f"Exported {len(accounts)} accounts to {output_file} (Markdown, {len(display_columns)} display columns)")

        except Exception as e:
            error_msg = f"Failed to export Markdown: {str(e)}"
            logger.error(error_msg)
            print_error(error_msg)
            raise IOError(error_msg) from e

    @staticmethod
    def to_csv_string(accounts: List[Dict]) -> str:
        """
        Convert accounts to CSV string format (in-memory).

        Args:
            accounts: List of account dictionaries

        Returns:
            CSV formatted string
        """
        if not accounts:
            return ""

        output = StringIO()
        fieldnames = list(accounts[0].keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(accounts)

        return output.getvalue()

    @staticmethod
    def to_json_string(accounts: List[Dict], indent: int = 2) -> str:
        """
        Convert accounts to JSON string format (in-memory).

        Args:
            accounts: List of account dictionaries
            indent: JSON indentation level

        Returns:
            JSON formatted string
        """
        return json.dumps({"accounts": accounts}, indent=indent, ensure_ascii=False)


class HierarchyFormatter:
    """Format Organizations hierarchy visualization data."""

    @staticmethod
    def format_hierarchy_tree(accounts: List[Dict], show_profiles: bool = True) -> str:
        """
        Format accounts as hierarchical tree structure.

        Args:
            accounts: List of account dictionaries
            show_profiles: Include profile mappings in output

        Returns:
            Formatted tree string
        """
        tree_lines = []
        tree_lines.append("AWS Organization Hierarchy")
        tree_lines.append("=" * 50)
        tree_lines.append("")

        for idx, account in enumerate(accounts):
            is_last = idx == len(accounts) - 1
            prefix = "└── " if is_last else "├── "

            account_line = f"{prefix}{account.get('name', 'N/A')} ({account.get('id', 'N/A')})"

            if show_profiles:
                account_line += f" → {account.get('profile', 'N/A')}"

            tree_lines.append(account_line)

            # Add status as sub-item
            status_prefix = "    " if is_last else "│   "
            tree_lines.append(f"{status_prefix}Status: {account.get('status', 'UNKNOWN')}")

            if not is_last:
                tree_lines.append("│")

        return "\n".join(tree_lines)

    @staticmethod
    def format_summary(accounts: List[Dict]) -> str:
        """
        Format summary statistics for accounts.

        Args:
            accounts: List of account dictionaries

        Returns:
            Formatted summary string
        """
        total = len(accounts)
        active = sum(1 for a in accounts if a.get("status") == "ACTIVE")
        suspended = sum(1 for a in accounts if a.get("status") == "SUSPENDED")
        closed = sum(1 for a in accounts if a.get("status") == "CLOSED")

        summary_lines = []
        summary_lines.append("Account Summary")
        summary_lines.append("=" * 40)
        summary_lines.append(f"Total Accounts:     {total}")
        summary_lines.append(f"Active Accounts:    {active}")
        summary_lines.append(f"Suspended Accounts: {suspended}")
        summary_lines.append(f"Closed Accounts:    {closed}")

        return "\n".join(summary_lines)


def export_to_file(accounts: List[Dict], output_path: str, format_type: str = "json", **kwargs) -> None:
    """
    Universal export function supporting multiple formats.

    Args:
        accounts: List of account dictionaries
        output_path: Output file path
        format_type: Export format ('json', 'csv', 'markdown')
        **kwargs: Additional format-specific arguments

    Raises:
        ValueError: If format_type is unsupported
        IOError: If file write fails
    """
    format_type = format_type.lower()

    if format_type == "json":
        metadata = kwargs.get("metadata")
        OrganizationsFormatter.export_json(accounts, output_path, metadata=metadata)

    elif format_type == "csv":
        include_header = kwargs.get("include_header", True)
        OrganizationsFormatter.export_csv(accounts, output_path, include_header=include_header)

    elif format_type == "markdown":
        title = kwargs.get("title", "AWS Organization Accounts")
        OrganizationsFormatter.export_markdown(accounts, output_path, title=title)

    else:
        supported_formats = ["json", "csv", "markdown"]
        raise ValueError(f"Unsupported format: {format_type}. Supported formats: {supported_formats}")
