"""
Core types for python-env-resolver.

Defines the core abstractions: Resolver protocol, policy options, and audit events.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Literal, Mapping, Optional, Protocol, Union


class Resolver(Protocol):
    """
    Protocol for environment variable resolvers.

    A resolver loads environment variables from a specific source
    (e.g., os.environ, .env file, secrets managers, APIs, etc.).

    This protocol provides a public typing contract that enables IDE
    completion and type checking for custom resolver implementations.
    """

    name: str
    metadata: Dict[str, Any]

    async def load(self) -> Mapping[str, str]:
        """Load environment variables from this source.

        Returns:
            Mapping of environment variable names to values.
            Keys should be uppercase (e.g., "DATABASE_URL", "PORT").
        """
        ...


@dataclass
class PolicyConfig:
    """
    Security policies to control where environment variables can be loaded from.

    Attributes:
        allow_dotenv_in_production: Control loading from .env files in production.
            - None (default): .env files completely blocked in production
            - True: Allow all vars from .env in production (NOT recommended)
            - List[str]: Allow only specific vars from .env in production

        enforce_allowed_sources: Restrict variables to specific resolvers.
            Example: {"DATABASE_PASSWORD": ["vault-secrets", "process.env"]}
    """

    allow_dotenv_in_production: Optional[Union[bool, List[str]]] = None
    enforce_allowed_sources: Optional[Dict[str, List[str]]] = None


# Keep PolicyOptions as an alias for backwards compatibility
PolicyOptions = PolicyConfig


@dataclass
class Provenance:
    """
    Tracks where an environment variable was loaded from.

    Attributes:
        source: Name of the resolver that provided this variable
        timestamp: When the variable was loaded (seconds since epoch)
        cached: Whether this value came from cache
    """

    source: str
    timestamp: float
    cached: Optional[bool] = None


AuditEventType = Literal[
    "validation_success",
    "validation_failure",
    "policy_violation",
    "env_loaded",
    "resolver_error",
]


@dataclass
class AuditEvent:
    """
    An event in the audit log.

    Attributes:
        type: Type of audit event
        timestamp: When the event occurred (seconds since epoch)
        key: Environment variable key (if applicable)
        source: Resolver name (if applicable)
        error: Error message (if applicable)
        metadata: Additional event metadata
    """

    type: AuditEventType
    timestamp: float
    key: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheOptions:
    """
    Options for caching resolver results.

    Attributes:
        ttl: Time to live (default: 300 seconds = 5 minutes).
             Accepts int/float (seconds) or timedelta for native Python types.
        max_age: Maximum age before forcing refresh (default: 3600 seconds = 1 hour).
                 Accepts int/float (seconds) or timedelta for native Python types.
        stale_while_revalidate: Serve stale data while refreshing in background
        key: Custom cache key for debugging
    """

    ttl: Union[int, float, timedelta] = 300  # 5 minutes
    max_age: Union[int, float, timedelta] = 3600  # 1 hour
    stale_while_revalidate: bool = False
    key: Optional[str] = None

    def get_ttl_seconds(self) -> float:
        """Convert TTL to seconds."""
        if isinstance(self.ttl, timedelta):
            return self.ttl.total_seconds()
        return float(self.ttl)

    def get_max_age_seconds(self) -> float:
        """Convert max_age to seconds."""
        if isinstance(self.max_age, timedelta):
            return self.max_age.total_seconds()
        return float(self.max_age)


@dataclass
class ResolveError:
    """
    Structured error information for resolution failures.

    Provides programmatic access to error details while maintaining
    backward compatibility with string errors via __str__().

    Attributes:
        type: Type of error (validation_error, policy_violation, resolver_error)
        message: Human-readable error message
        key: Environment variable key (if applicable)
        source: Resolver name (if applicable)
        field: Field name for validation errors (if applicable)
        details: Additional error context
    """

    type: Literal["validation_error", "policy_violation", "resolver_error"]
    message: str
    key: Optional[str] = None
    source: Optional[str] = None
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        """Return human-readable error message."""
        return self.message


@dataclass
class ResolveOptions:
    """
    Options for environment resolution.

    Attributes:
        interpolate: Enable variable interpolation using ${VAR_NAME} syntax
        strict: Fail-fast if any resolver fails (vs graceful degradation)
        priority: Merge strategy when multiple resolvers provide same variable.
                 - "last": later resolvers override earlier ones (default)
                 - "first": earlier resolvers take precedence
        policies: Security policies to enforce
        enable_audit: Enable audit logging
        env: Override environment detection ("production" or "development").
             If None, checks PYTHON_ENV > ENV > defaults to "development"
    """

    interpolate: bool = True
    strict: bool = True
    priority: Literal["first", "last"] = "last"
    policies: Optional[PolicyConfig] = None
    enable_audit: Optional[bool] = None  # None = auto (true in production)
    env: Optional[Literal["production", "development"]] = None

