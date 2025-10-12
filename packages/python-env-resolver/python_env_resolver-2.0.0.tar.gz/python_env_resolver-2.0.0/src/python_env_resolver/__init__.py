"""
python-env-resolver: Type-safe environment variable handling for Python

Pythonic configuration management with Pydantic validation.
"""

from .audit import (
    clear_audit_log,
    get_audit_log,
    log_audit_event,
)
from .constants import ResolverNames
from .resolver import (
    ResolveResult,
    from_env,
    from_env_async,
    resolve,
    resolve_async,
    safe_resolve,
    safe_resolve_async,
)
from .resolvers import (
    DotenvResolver,
    FileEnvResolver,
    ProcessEnvResolver,
    dotenv,
    file_env,
    process_env,
)
from .types import (
    AuditEvent,
    CacheOptions,
    PolicyConfig,
    PolicyOptions,
    Provenance,
    ResolveError,
    ResolveOptions,
    Resolver,
)
from .utils import (
    TTL,
    CachedResolver,
    cached,
)
from .validators import (
    validate_boolean,
    validate_email,
    validate_http,
    validate_https,
    validate_integer,
    validate_json,
    validate_mongodb,
    validate_mysql,
    validate_number,
    validate_number_range,
    validate_port,
    validate_postgres,
    validate_redis,
    validate_url,
)

__all__ = [
    # Main API (Pythonic: sync is default, _async suffix for async)
    "resolve",           # sync (default)
    "resolve_async",     # async
    "safe_resolve",      # sync (default)
    "safe_resolve_async",  # async
    "from_env",          # sync (default)
    "from_env_async",    # async
    # Types
    "Resolver",
    "ResolveResult",
    "ResolveError",
    "PolicyConfig",
    "PolicyOptions",  # backwards compatibility
    "Provenance",
    "AuditEvent",
    "ResolveOptions",
    "CacheOptions",
    # Constants
    "ResolverNames",
    # Resolvers
    "ProcessEnvResolver",
    "DotenvResolver",
    "FileEnvResolver",
    "process_env",
    "dotenv",
    "file_env",
    # Caching
    "CachedResolver",
    "cached",
    "TTL",
    # Validators
    "validate_url",
    "validate_http",
    "validate_https",
    "validate_email",
    "validate_port",
    "validate_number_range",
    "validate_postgres",
    "validate_mysql",
    "validate_mongodb",
    "validate_redis",
    "validate_json",
    "validate_boolean",
    "validate_number",
    "validate_integer",
    # Audit
    "get_audit_log",
    "clear_audit_log",
    "log_audit_event",
]

__version__ = "0.1.0"
