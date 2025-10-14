"""
Utilities package for CloudOps Runbooks.

This package provides utility modules including logging, configuration,
and helper functions used throughout the runbooks package.
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from loguru import logger

    _HAS_LOGURU = True
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    _HAS_LOGURU = False

# Legacy utilities
from runbooks.utils.logger import configure_logger

# Version management utilities
from runbooks.utils.version_validator import (
    check_pyproject_version,
    get_all_module_versions,
    print_version_report,
    validate_version_consistency,
    VersionDriftError,
)


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application.

    Args:
        debug: Enable debug logging if True
        log_file: Optional path to log file
    """
    if _HAS_LOGURU:
        from loguru import logger as loguru_logger

        # Remove default handler
        loguru_logger.remove()

        # Console handler with appropriate level
        log_level = "DEBUG" if debug else "INFO"
        loguru_logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            loguru_logger.add(
                log_path,
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="10 MB",
                retention="7 days",
                compression="zip",
            )

        loguru_logger.info(f"Logging initialized with level: {log_level}")
    else:
        # Fallback to standard logging
        import logging

        log_level_value = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level_value,
            format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            handlers=[logging.StreamHandler(sys.stderr)],
        )

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(log_level_value)
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)


def setup_enhanced_logging(log_level: str = "INFO", json_output: bool = False, debug: bool = False) -> None:
    """
    Configure enhanced enterprise logging with Rich CLI integration and user-type specific output.

    This function initializes the global enhanced logger that provides:
    - User-type specific formatting (DEBUG=tech, INFO=standard, WARNING=business, ERROR=all)
    - Rich CLI integration with beautiful formatting
    - Structured JSON output option for programmatic use
    - AWS API tracing for technical users
    - Business recommendations for warning level
    - Clear error solutions for all users

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: Enable structured JSON output for programmatic use
        debug: Legacy debug flag for backward compatibility
    """
    try:
        from runbooks.enterprise.logging import configure_enterprise_logging, get_context_logger
        from runbooks.common.rich_utils import get_context_aware_console

        # Override level if debug flag is set (backward compatibility)
        if debug:
            log_level = "DEBUG"

        # Get context-aware console for Rich CLI integration
        try:
            rich_console = get_context_aware_console()
        except ImportError:
            rich_console = None

        # Configure global enhanced logger
        logger = configure_enterprise_logging(level=log_level, rich_console=rich_console, json_output=json_output)

        # Log initialization success with user-type appropriate message
        if log_level == "DEBUG":
            logger.debug_tech(
                "Enhanced logging initialized with Rich CLI integration",
                aws_api={"service": "logging", "operation": "initialize"},
                duration=0.001,
            )
        elif log_level == "INFO":
            logger.info_standard("CloudOps Runbooks logging initialized")
        elif log_level == "WARNING":
            logger.warning_business(
                "Business-focused logging enabled", recommendation="Use --log-level INFO for standard operations"
            )
        else:
            logger.error_all("Minimal error-only logging enabled")

    except ImportError as e:
        # Fallback to standard logging if enhanced logging not available
        setup_logging(debug=debug)
        print(f"Warning: Enhanced logging not available, falling back to standard logging: {e}")


def validate_aws_profile(profile: str) -> bool:
    """
    Validate that an AWS profile exists in credentials.

    Args:
        profile: AWS profile name to validate

    Returns:
        True if profile exists, False otherwise
    """
    import configparser

    try:
        # Check ~/.aws/credentials
        credentials_path = Path.home() / ".aws" / "credentials"
        if credentials_path.exists():
            config = configparser.ConfigParser()
            config.read(credentials_path)
            if profile in config.sections():
                return True

        # Check ~/.aws/config
        config_path = Path.home() / ".aws" / "config"
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path)
            profile_section = f"profile {profile}" if profile != "default" else "default"
            if profile_section in config.sections():
                return True

        return False
    except Exception as e:
        logger.warning(f"Error validating AWS profile '{profile}': {e}")
        return False


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        The directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_size(size_bytes: int) -> str:
    """
    Format byte size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    size_index = 0
    size = float(size_bytes)

    while size >= 1024 and size_index < len(size_names) - 1:
        size /= 1024
        size_index += 1

    return f"{size:.1f} {size_names[size_index]}"


def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    Decorator for retrying operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor for exponential backoff
    """
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise

                    wait_time = backoff_factor * (2**attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)

            raise last_exception

        return wrapper

    return decorator


__all__ = [
    "setup_logging",
    "setup_enhanced_logging",
    "validate_aws_profile",
    "ensure_directory",
    "format_size",
    "retry_with_backoff",
    "configure_logger",
    # Version management
    "check_pyproject_version",
    "get_all_module_versions",
    "print_version_report",
    "validate_version_consistency",
    "VersionDriftError",
]
