# Profile utilities for multi-account AWS operations with enterprise caching
import os
import time
import boto3
from typing import Optional, List, Dict, Any
from runbooks.common.rich_utils import console
from datetime import datetime
from botocore.config import Config

# Enhanced caching system for enterprise performance
_profile_cache: Dict[str, str] = {}
_validation_cache: Dict[str, bool] = {}  # Cache for profile validation results
_cache_timestamp: Optional[float] = None
_cache_ttl: int = 300  # 5 minutes TTL for enterprise session management
_session_id: Optional[str] = None  # Track session consistency
_session_cache: Dict[str, boto3.Session] = {}  # Cache AWS sessions

# Timeout configuration for AWS API calls (prevents execution flow hangs)
_AWS_CLIENT_CONFIG = Config(
    connect_timeout=30,  # Connection timeout: 30 seconds
    read_timeout=60,  # Read timeout: 60 seconds
    retries={"max_attempts": 3, "mode": "adaptive"},
)


def _get_session_id() -> str:
    """Generate consistent session ID for cache scoping"""
    global _session_id
    if _session_id is None:
        _session_id = f"session_{int(time.time())}"
    return _session_id


def get_profile_for_operation(
    operation_type: str, user_specified_profile: Optional[str] = None, profiles: Optional[List[str]] = None
) -> str:
    """
    Enhanced profile resolution with intelligent caching and enterprise logging optimization.

    Priority Order:
    1. User-specified profile (--profile parameter) - HIGHEST PRIORITY
    2. Environment variable mapping (per operation type)
    3. Default profile fallback

    Args:
        operation_type: Type of operation (billing, management, operational)
        user_specified_profile: User-provided profile via --profile parameter
        profiles: List of profiles for multi-account operations

    Returns:
        Profile name to use for the operation

    Caching Strategy:
    - Cache profile resolution to prevent redundant AWS API calls
    - Session-scoped caching with 5-minute TTL
    - Only log profile selection once per session to reduce noise
    """
    global _cache_timestamp
    current_time = time.time()

    # Create profile-specific cache key (same profile for all operations)
    profile_cache_key = f"{_get_session_id()}:{user_specified_profile or 'default'}"

    # Return cached result if still valid and within TTL
    if profile_cache_key in _profile_cache and _cache_timestamp and current_time - _cache_timestamp < _cache_ttl:
        return _profile_cache[profile_cache_key]

    # Update cache timestamp only when cache is actually refreshed
    if not _cache_timestamp or current_time - _cache_timestamp >= _cache_ttl:
        _profile_cache.clear()
        _validation_cache.clear()
        _cache_timestamp = current_time

    available_profiles = boto3.Session().available_profiles

    # PRIORITY 1: User-specified profile ALWAYS takes precedence
    if user_specified_profile and user_specified_profile != "default":
        if user_specified_profile in available_profiles:
            # SESSION-AWARE LOGGING: Only log when cache miss occurs
            if profile_cache_key not in _profile_cache:
                console.log(f"[green]Using user-specified profile: {user_specified_profile}[/]")
            # Cache the result to prevent duplicate logging
            _profile_cache[profile_cache_key] = user_specified_profile
            return user_specified_profile
        else:
            console.log(f"[red]Error: Profile '{user_specified_profile}' not found in AWS config[/]")
            console.log(f"[yellow]Available profiles: {', '.join(available_profiles)}[/]")
            raise SystemExit(1)

    # PRIORITY 2: AWS_PROFILE environment variable (standard AWS convention)
    aws_profile = os.getenv("AWS_PROFILE")
    if aws_profile and aws_profile in available_profiles:
        _profile_cache[profile_cache_key] = aws_profile
        return aws_profile

    # PRIORITY 3: Operation-specific environment variables
    profile_map = {
        "billing": os.getenv("BILLING_PROFILE"),
        "management": os.getenv("MANAGEMENT_PROFILE"),
        "operational": os.getenv("CENTRALISED_OPS_PROFILE"),
    }

    env_profile = profile_map.get(operation_type)
    if env_profile and env_profile in available_profiles:
        _profile_cache[profile_cache_key] = env_profile
        return env_profile

    # PRIORITY 4: Default profile fallback
    if "default" in available_profiles:
        _profile_cache[profile_cache_key] = "default"
        return "default"
    elif available_profiles:
        # Use first available profile if no default
        first_profile = available_profiles[0]
        console.log(f"[yellow]Warning: No default profile found, using: {first_profile}[/]")
        _profile_cache[profile_cache_key] = first_profile
        return first_profile
    else:
        console.log("[red]Error: No AWS profiles configured[/]")
        console.log("[yellow]Please run: aws configure sso or aws configure[/]")
        raise SystemExit(1)


def validate_profile_access(profile_name: str, operation_description: str = "") -> bool:
    """
    Validate that the specified profile has proper AWS access with caching.

    Args:
        profile_name: AWS profile name to validate
        operation_description: Optional description of the operation (for logging)

    Returns:
        True if profile has access, False otherwise
    """
    # Check cache first to avoid redundant validations
    global _cache_timestamp
    current_time = time.time()
    cache_key = f"validation:{profile_name}"

    if cache_key in _validation_cache and _cache_timestamp and current_time - _cache_timestamp < _cache_ttl:
        return _validation_cache[cache_key]

    try:
        session = boto3.Session(profile_name=profile_name)
        sts_client = session.client("sts")
        sts_client.get_caller_identity()

        # Cache successful validation
        _validation_cache[cache_key] = True
        return True
    except Exception as e:
        # Cache failed validation for shorter time to allow retry
        _validation_cache[cache_key] = False
        console.log(f"[yellow]Profile {profile_name} validation failed: {e}[/]")
        return False


def get_account_id_from_profile(profile_name: str) -> Optional[str]:
    """
    Extract account ID from AWS profile.

    Args:
        profile_name: AWS profile name

    Returns:
        Account ID if available, None otherwise
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        sts_client = session.client("sts")
        response = sts_client.get_caller_identity()
        return response.get("Account")
    except Exception:
        return None


def auto_discover_enterprise_profiles() -> Dict[str, Optional[str]]:
    """
    Auto-discover enterprise AWS SSO profiles for streamlined initialization.

    Searches for profiles matching common enterprise naming patterns:
    - *Billing* or *billing* for BILLING_PROFILE
    - *Management* or *management* for MANAGEMENT_PROFILE
    - *Ops* or *ops* for CENTRALISED_OPS_PROFILE
    - Single account profiles for SINGLE_AWS_PROFILE

    Returns:
        Dict mapping profile types to discovered profile names
    """
    available_profiles = boto3.Session().available_profiles
    discovered = {"billing": None, "management": None, "centralised_ops": None, "single_aws": None}

    # Search patterns for enterprise profiles
    for profile in available_profiles:
        profile_lower = profile.lower()

        # Billing profile detection
        if ("billing" in profile_lower or "cost" in profile_lower) and not discovered["billing"]:
            discovered["billing"] = profile

        # Management profile detection
        elif ("management" in profile_lower or "admin" in profile_lower) and not discovered["management"]:
            discovered["management"] = profile

        # Operations profile detection
        elif (
            "ops" in profile_lower or "operational" in profile_lower or "centralised" in profile_lower
        ) and not discovered["centralised_ops"]:
            discovered["centralised_ops"] = profile

        # Single account detection (typically shorter names or containing 'single')
        elif ("single" in profile_lower or len(profile) < 20) and not discovered["single_aws"]:
            discovered["single_aws"] = profile

    # Log discovered profiles for transparency
    for profile_type, profile_name in discovered.items():
        if profile_name:
            console.log(f"[green]✅ Auto-discovered {profile_type}: {profile_name}[/green]")
        else:
            console.log(f"[yellow]⚠️ No profile found for {profile_type}[/yellow]")

    return discovered


def setup_enterprise_environment_variables(discovered_profiles: Optional[Dict[str, Optional[str]]] = None) -> None:
    """
    Setup enterprise environment variables from discovered profiles.

    Args:
        discovered_profiles: Optional pre-discovered profiles dict
    """
    if not discovered_profiles:
        discovered_profiles = auto_discover_enterprise_profiles()

    # Set environment variables if not already set
    env_mappings = {
        "BILLING_PROFILE": discovered_profiles.get("billing"),
        "MANAGEMENT_PROFILE": discovered_profiles.get("management"),
        "CENTRALISED_OPS_PROFILE": discovered_profiles.get("centralised_ops"),
        "SINGLE_AWS_PROFILE": discovered_profiles.get("single_aws"),
    }

    for env_var, profile_name in env_mappings.items():
        if profile_name and not os.getenv(env_var):
            os.environ[env_var] = profile_name
            console.log(f"[blue]📋 Set {env_var}={profile_name}[/blue]")
        elif os.getenv(env_var):
            console.log(f"[dim]Using existing {env_var}={os.getenv(env_var)}[/dim]")


def create_cost_session(profile_name: Optional[str] = None) -> boto3.Session:
    """
    Create AWS session optimized for cost operations (Cost Explorer) with token error handling.

    Args:
        profile_name: AWS profile name for cost operations

    Returns:
        Configured boto3 Session for cost operations

    Raises:
        SystemExit: When authentication fails with clear user guidance
    """
    from botocore.exceptions import TokenRetrievalError, NoCredentialsError
    from .rich_utils import console, print_error, print_info

    cost_profile = get_profile_for_operation("billing", profile_name)

    # Use cached session if available and validate it's still working
    session_key = f"cost:{cost_profile}"
    if session_key in _session_cache:
        cached_session = _session_cache[session_key]
        # Quick validation that the cached session still works
        try:
            # Test with a minimal STS call to check if credentials are valid (with timeout)
            sts_client = cached_session.client("sts", config=_AWS_CLIENT_CONFIG)
            sts_client.get_caller_identity()
            return cached_session
        except (TokenRetrievalError, NoCredentialsError):
            # Remove invalid cached session
            del _session_cache[session_key]
            console.log("[yellow]⚠️ Cached session expired, creating new session[/]")

    try:
        session = boto3.Session(profile_name=cost_profile)
        # Test the session to ensure credentials are valid (with timeout)
        sts_client = session.client("sts", config=_AWS_CLIENT_CONFIG)
        sts_client.get_caller_identity()

        # Cache only if session works
        _session_cache[session_key] = session
        return session

    except TokenRetrievalError as e:
        print_error("🔐 AWS SSO token has expired")
        print_info("💡 To fix this issue:")
        print_info(f"   1. Run: [cyan]aws sso login --profile {cost_profile}[/]")
        print_info("   2. Or try: [cyan]aws sso login[/] (if using default profile)")
        print_info("   3. Verify your internet connection")
        print_info("   4. Check if your AWS SSO session has expired")
        console.log(f"[dim]Profile used: {cost_profile}[/]")
        console.log(f"[dim]Error details: {str(e)}[/]")
        raise SystemExit(1)

    except NoCredentialsError as e:
        print_error("🔐 No AWS credentials configured")
        print_info("💡 To fix this issue:")
        print_info("   1. Configure AWS CLI: [cyan]aws configure[/]")
        print_info("   2. Or setup SSO: [cyan]aws configure sso[/]")
        print_info(f"   3. Or set profile: [cyan]export AWS_PROFILE={cost_profile}[/]")
        console.log(f"[dim]Profile attempted: {cost_profile}[/]")
        raise SystemExit(1)

    except Exception as e:
        print_error(f"🔐 Authentication failed for profile: {cost_profile}")
        print_info("💡 To fix this issue:")
        print_info("   1. Verify the profile exists: [cyan]aws configure list-profiles[/]")
        print_info("   2. Check profile permissions for cost analysis")
        print_info("   3. Ensure profile has Cost Explorer access")
        console.log(f"[dim]Error details: {str(e)}[/]")
        raise SystemExit(1)


def create_management_session(profile_name: Optional[str] = None) -> boto3.Session:
    """
    Create AWS session optimized for management operations (Organizations) with token error handling.

    Args:
        profile_name: AWS profile name for management operations

    Returns:
        Configured boto3 Session for management operations

    Raises:
        SystemExit: When authentication fails with clear user guidance
    """
    from botocore.exceptions import TokenRetrievalError, NoCredentialsError
    from .rich_utils import console, print_error, print_info

    mgmt_profile = get_profile_for_operation("management", profile_name)

    # Use cached session if available and validate it's still working
    session_key = f"management:{mgmt_profile}"
    if session_key in _session_cache:
        cached_session = _session_cache[session_key]
        # Quick validation that the cached session still works
        try:
            # Test with a minimal STS call to check if credentials are valid (with timeout)
            sts_client = cached_session.client("sts", config=_AWS_CLIENT_CONFIG)
            sts_client.get_caller_identity()
            return cached_session
        except (TokenRetrievalError, NoCredentialsError):
            # Remove invalid cached session
            del _session_cache[session_key]
            console.log("[yellow]⚠️ Cached session expired, creating new session[/]")

    try:
        session = boto3.Session(profile_name=mgmt_profile)
        # Test the session to ensure credentials are valid (with timeout)
        sts_client = session.client("sts", config=_AWS_CLIENT_CONFIG)
        sts_client.get_caller_identity()

        # Cache only if session works
        _session_cache[session_key] = session
        return session

    except TokenRetrievalError as e:
        print_error("🔐 AWS SSO token has expired")
        print_info("💡 To fix this issue:")
        print_info(f"   1. Run: [cyan]aws sso login --profile {mgmt_profile}[/]")
        print_info("   2. Or try: [cyan]aws sso login[/] (if using default profile)")
        print_info("   3. Verify your internet connection")
        print_info("   4. Check if your AWS SSO session has expired")
        console.log(f"[dim]Profile used: {mgmt_profile}[/]")
        console.log(f"[dim]Error details: {str(e)}[/]")
        raise SystemExit(1)

    except NoCredentialsError as e:
        print_error("🔐 No AWS credentials configured")
        print_info("💡 To fix this issue:")
        print_info("   1. Configure AWS CLI: [cyan]aws configure[/]")
        print_info("   2. Or setup SSO: [cyan]aws configure sso[/]")
        print_info(f"   3. Or set profile: [cyan]export AWS_PROFILE={mgmt_profile}[/]")
        console.log(f"[dim]Profile attempted: {mgmt_profile}[/]")
        raise SystemExit(1)

    except Exception as e:
        print_error(f"🔐 Authentication failed for profile: {mgmt_profile}")
        print_info("💡 To fix this issue:")
        print_info("   1. Verify the profile exists: [cyan]aws configure list-profiles[/]")
        print_info("   2. Check profile permissions for management operations")
        print_info("   3. Ensure profile has Organizations access")
        console.log(f"[dim]Error details: {str(e)}[/]")
        raise SystemExit(1)


def create_operational_session(profile_name: Optional[str] = None) -> boto3.Session:
    """
    Create AWS session optimized for operational tasks (EC2, S3, etc).

    Args:
        profile_name: AWS profile name for operational tasks

    Returns:
        Configured boto3 Session for operational tasks
    """
    ops_profile = get_profile_for_operation("operational", profile_name)

    # Use cached session if available
    session_key = f"operational:{ops_profile}"
    if session_key in _session_cache:
        return _session_cache[session_key]

    session = boto3.Session(profile_name=ops_profile)
    _session_cache[session_key] = session
    return session


def get_current_profile_info(profile_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current profile information including account ID and region.

    Args:
        profile_name: AWS profile name to get info for

    Returns:
        Dictionary containing profile information
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        sts_client = session.client("sts", config=_AWS_CLIENT_CONFIG)
        identity = sts_client.get_caller_identity()

        return {
            "profile_name": profile_name or "default",
            "account_id": identity.get("Account"),
            "user_arn": identity.get("Arn"),
            "region": session.region_name or "us-east-1",
        }
    except Exception as e:
        return {
            "profile_name": profile_name or "default",
            "error": str(e),
            "account_id": None,
            "user_arn": None,
            "region": None,
        }


def resolve_profile_for_operation_silent(operation_type: str, user_specified_profile: Optional[str] = None) -> str:
    """
    Silent version of profile resolution without logging.

    Args:
        operation_type: Type of operation (billing, management, operational)
        user_specified_profile: User-provided profile via --profile parameter

    Returns:
        Profile name to use for the operation
    """
    # Skip all logging and caching, just return the profile
    if user_specified_profile and user_specified_profile != "default":
        return user_specified_profile

    # Check environment variables
    profile_map = {
        "billing": os.getenv("BILLING_PROFILE"),
        "management": os.getenv("MANAGEMENT_PROFILE"),
        "operational": os.getenv("CENTRALISED_OPS_PROFILE"),
    }

    env_profile = profile_map.get(operation_type)
    if env_profile:
        return env_profile

    return user_specified_profile or "default"


def list_available_profiles() -> List[str]:
    """
    Get list of all available AWS profiles.

    Returns:
        List of available profile names
    """
    return boto3.Session().available_profiles


def clear_profile_cache() -> None:
    """Clear the profile cache for testing or troubleshooting."""
    global _profile_cache, _validation_cache, _session_cache, _cache_timestamp, _session_id
    _profile_cache.clear()
    _validation_cache.clear()
    _session_cache.clear()
    _cache_timestamp = None
    _session_id = None


def create_timeout_protected_client(session: boto3.Session, service_name: str, region_name: Optional[str] = None):
    """
    Create AWS service client with timeout protection to prevent execution flow hangs.

    This function should be used by all FinOps modules to create AWS clients with
    enterprise-grade timeout protection and retry configuration.

    Args:
        session: boto3 Session to use for client creation
        service_name: AWS service name (e.g., 'ec2', 'ce', 'workspaces', 'rds')
        region_name: AWS region name (optional)

    Returns:
        AWS service client with timeout protection

    Example:
        session = create_cost_session()
        ce_client = create_timeout_protected_client(session, 'ce', 'us-east-1')
        ec2_client = create_timeout_protected_client(session, 'ec2', region_name)
    """
    return session.client(service_name, region_name=region_name, config=_AWS_CLIENT_CONFIG)
