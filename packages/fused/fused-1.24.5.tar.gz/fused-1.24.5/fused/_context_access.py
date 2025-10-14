"""
Access to request headers and context properties for UDFs.
"""

from typing import Dict, Optional

from fused._udf.context import get_global_context


def get_headers() -> Dict[str, str]:
    """Get the request headers that were passed to the UDF."""
    context = get_global_context()
    if context and hasattr(context, "headers"):
        return context.headers
    return {}


def get_header(name: str) -> Optional[str]:
    """Get a specific request header by name (case-insensitive)."""
    headers = get_headers()
    # Case-insensitive lookup
    for header_name, value in headers.items():
        if header_name.lower() == name.lower():
            return value
    return None


def get_user_email() -> Optional[str]:
    """Get the user email from the current context."""
    context = get_global_context()
    if context and hasattr(context, "user_email"):
        return context.user_email
    return None


def get_realtime_client_id() -> Optional[str]:
    """Get the realtime client ID from the current context."""
    context = get_global_context()
    if context and hasattr(context, "realtime_client_id"):
        return context.realtime_client_id
    return None


def get_recursion_factor() -> Optional[int]:
    """Get the recursion factor from the current context."""
    context = get_global_context()
    if context and hasattr(context, "recursion_factor"):
        return context.recursion_factor
    return None
