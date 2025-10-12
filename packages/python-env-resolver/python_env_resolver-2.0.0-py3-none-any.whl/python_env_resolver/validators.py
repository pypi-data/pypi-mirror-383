"""
Built-in validators for common environment variable types.

Provides validators for URLs, emails, database connection strings, etc.
"""

import json
import re
from typing import Any
from urllib.parse import urlparse

from pydantic import EmailStr, ValidationError


def validate_url(value: str, require_https: bool = False) -> str:
    """
    Validate generic URL with protocol whitelist.

    Args:
        value: URL string to validate
        require_https: If True, only allow HTTPS URLs (default: False)

    Allowed protocols: http, https, ws, wss, ftp, ftps, file,
                       postgres, postgresql, mysql, mongodb, redis, rediss
    """
    try:
        parsed = urlparse(value)

        if require_https:
            if parsed.scheme != 'https':
                raise ValueError("URL must use HTTPS protocol")
        else:
            allowed_protocols = [
                'http', 'https', 'ws', 'wss', 'ftp', 'ftps', 'file',
                'postgres', 'postgresql', 'mysql', 'mongodb', 'redis', 'rediss'
            ]
            if parsed.scheme not in allowed_protocols:
                raise ValueError(f"URL protocol '{parsed.scheme}:' is not allowed")
        return value
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")


def validate_http(value: str) -> str:
    """Validate HTTP or HTTPS URL."""
    if not re.match(r'^https?://.+', value):
        raise ValueError("Invalid HTTP URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid HTTP URL")


def validate_https(value: str) -> str:
    """Validate HTTPS URL only (strict)."""
    if not re.match(r'^https://.+', value):
        raise ValueError("Invalid HTTPS URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid HTTPS URL")


def validate_email(value: str) -> str:
    """Validate email address using Pydantic's EmailStr."""
    try:
        # Use Pydantic's email validator
        from pydantic import TypeAdapter
        adapter = TypeAdapter(EmailStr)
        adapter.validate_python(value)
        return value
    except ValidationError:
        raise ValueError("Invalid email address")


def validate_port(value: int | str, min_port: int = 1, max_port: int = 65535) -> int:
    """
    Validate port number.

    Args:
        value: Port number (int or string)
        min_port: Minimum allowed port (default: 1)
        max_port: Maximum allowed port (default: 65535)

    Returns:
        Validated port number as int
    """
    try:
        port = int(value)
        if port < min_port or port > max_port:
            raise ValueError(f"Port must be between {min_port} and {max_port}")
        return port
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Invalid port number")
        raise


def validate_postgres(value: str) -> str:
    """Validate PostgreSQL connection string."""
    if not re.match(r'^postgres(ql)?://.+', value):
        raise ValueError("Invalid PostgreSQL URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid PostgreSQL URL")


def validate_mysql(value: str) -> str:
    """Validate MySQL connection string."""
    if not re.match(r'^mysql://.+', value):
        raise ValueError("Invalid MySQL URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid MySQL URL")


def validate_mongodb(value: str) -> str:
    """
    Validate MongoDB connection string.

    Supports mongodb:// and mongodb+srv:// with replica sets.
    """
    if not re.match(r'^mongodb(\+srv)?://.+', value):
        raise ValueError("Invalid MongoDB URL")

    # MongoDB supports multiple hosts (replica sets), so basic pattern match
    mongo_pattern = r'^mongodb(\+srv)?://([^@]+@)?[^/]+(/[^?]*)?(\\?.*)?$'
    if not re.match(mongo_pattern, value):
        raise ValueError("Invalid MongoDB URL")

    return value


def validate_redis(value: str) -> str:
    """
    Validate Redis connection string.

    Supports redis:// and rediss:// (TLS).
    """
    if not re.match(r'^rediss?://.+', value):
        raise ValueError("Invalid Redis URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid Redis URL")


def validate_json(value: str) -> Any:
    """
    Validate and parse JSON string.

    Returns:
        Parsed JSON value
    """
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")


def validate_boolean(value: str) -> bool:
    """
    Validate and coerce boolean from string.

    Accepts: true/false, 1/0, yes/no, on/off (case-insensitive)
    Empty string is treated as False.
    """
    lower = value.lower().strip()
    if lower in ['true', '1', 'yes', 'on']:
        return True
    elif lower in ['false', '0', 'no', 'off', '']:
        return False
    else:
        raise ValueError("Invalid boolean value")


def validate_number(value: str) -> float:
    """Validate and coerce number from string."""
    try:
        return float(value)
    except ValueError:
        raise ValueError("Invalid number")


def validate_integer(value: str) -> int:
    """Validate and coerce integer from string."""
    try:
        return int(value)
    except ValueError:
        raise ValueError("Invalid integer")


def validate_number_range(
    value: int | float | str,
    min_val: int | float | None = None,
    max_val: int | float | None = None
) -> int | float:
    """
    Validate that a number is within a specified range.

    Args:
        value: Number to validate (int, float, or string)
        min_val: Minimum allowed value (inclusive, optional)
        max_val: Maximum allowed value (inclusive, optional)

    Returns:
        Validated number (preserves type as int or float)
    """
    # Convert to number if string
    if isinstance(value, str):
        try:
            # Try int first, then float
            if '.' in value:
                num = float(value)
            else:
                num = int(value)
        except ValueError:
            raise ValueError("Invalid number")
    else:
        num = value

    # Range validation
    if min_val is not None and num < min_val:
        raise ValueError(f"Value must be at least {min_val}")
    if max_val is not None and num > max_val:
        raise ValueError(f"Value must be at most {max_val}")

    return num

