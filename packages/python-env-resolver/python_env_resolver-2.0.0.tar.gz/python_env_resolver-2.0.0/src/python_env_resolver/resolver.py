"""
Core resolution logic with Pydantic integration.

Implements the resolve() function that loads, merges, validates, and enforces
policies on environment variables using Pydantic BaseModel.
"""

import asyncio
import os
import re
import threading
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, TypeVar, cast

from pydantic import BaseModel, ValidationError

from .audit import log_audit_event
from .resolvers import process_env
from .types import (
    AuditEvent,
    PolicyConfig,
    Provenance,
    ResolveError,
    ResolveOptions,
    Resolver,
)

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')


class ResolveResult:
    """
    Result of safe_resolve() - similar to TypeScript SafeResolveResult.

    Provides a non-raising API for error handling.

    Attributes:
        success: True if resolution succeeded, False if failed
        data: The resolved model instance (if success=True)
        error: Structured error information (if success=False)

    Example:
        >>> result = await safe_resolve(AppConfig)
        >>> if result.success:
        ...     config = result.data
        ...     print(config.port)
        ... else:
        ...     # Structured error access
        ...     if result.error.type == "policy_violation":
        ...         log.error(f"Policy error: {result.error.key} from {result.error.source}")
        ...     # Or as string
        ...     log.error(f"Configuration failed: {result.error}")
    """

    def __init__(
        self,
        success: bool,
        data: Optional[BaseModel] = None,
        error: Optional[ResolveError] = None
    ):
        self.success = success
        self.data = data
        self.error = error


def _is_production(options: Optional[ResolveOptions] = None) -> bool:
    """
    Check if running in production environment.

    Detection order: ResolveOptions(env=...) > PYTHON_ENV > ENV > "development"
    """
    # 1. Check explicit override from ResolveOptions
    if options and options.env:
        return options.env == "production"

    # 2. Check PYTHON_ENV
    python_env = os.environ.get("PYTHON_ENV", "").lower()
    if python_env:
        return python_env == "production"

    # 3. Check ENV
    env = os.environ.get("ENV", "").lower()
    if env:
        return env == "production"

    # 4. Default to development
    return False


def _interpolate_value(value: str, env: Dict[str, str]) -> str:
    """
    Interpolate ${VAR_NAME} references in value.

    Args:
        value: String that may contain ${VAR_NAME} references
        env: Environment dict to resolve from

    Returns:
        Interpolated string
    """
    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        return env.get(var_name, match.group(0))

    return re.sub(r'\$\{([^}]+)\}', replacer, value)


async def _resolve_from_resolvers(
    resolvers: List[Resolver],
    interpolate: bool,
    strict: bool,
    priority: str,
) -> tuple[Dict[str, str], Dict[str, Provenance]]:
    """
    Load and merge environment variables from multiple resolvers.

    Args:
        resolvers: List of resolvers to load from
        interpolate: Whether to interpolate ${VAR} references
        strict: Whether to fail on resolver errors
        priority: 'first' or 'last' - merge strategy

    Returns:
        Tuple of (merged_env, provenance)
    """
    merged_env: Dict[str, str] = {}
    provenance: Dict[str, Provenance] = {}

    for resolver in resolvers:
        try:
            env = await resolver.load()
            for key, value in env.items():
                if value is not None:
                    # priority: 'first' - only set if not already defined
                    # priority: 'last' - always overwrite (default behavior)
                    if priority == 'first' and key in merged_env:
                        continue

                    merged_env[key] = value
                    provenance[key] = Provenance(
                        source=resolver.name,
                        timestamp=time.time(),
                        cached=resolver.metadata.get("cached") if resolver.metadata else None
                    )
        except Exception as error:
            log_audit_event(AuditEvent(
                type="resolver_error",
                timestamp=time.time(),
                source=resolver.name,
                error=str(error)
            ))

            if strict:
                raise RuntimeError(f"Resolver {resolver.name} failed: {error}")

    # Interpolation
    if interpolate:
        for key in merged_env:
            merged_env[key] = _interpolate_value(merged_env[key], merged_env)

    return merged_env, provenance


def _apply_policies(
    key: str,
    source: str,
    policies: Optional[PolicyConfig],
    options: Optional[ResolveOptions] = None,
) -> Optional[str]:
    """
    Apply security policies to check if variable is allowed from this source.

    Args:
        key: Environment variable name
        source: Resolver name that provided this variable
        policies: Security policies to enforce
        options: Resolve options (for environment detection override)

    Returns:
        Error message if policy violated, None if OK
    """
    if policies is None:
        return None

    is_production = _is_production(options)

    # In production, .env files are forbidden by default (secure by default)
    if is_production and source.startswith("dotenv("):
        policy = policies.allow_dotenv_in_production

        # If True, allow all vars from .env
        if policy is True:
            return None

        # If list, only allow specific vars
        if isinstance(policy, list):
            if key not in policy:
                return f"{key} cannot be sourced from .env files in production. Use os.environ or cloud resolvers. To allow: policies.allow_dotenv_in_production: [{key!r}] or set to True for all."
            return None

        # Default: forbid all .env in production
        return f"{key} cannot be sourced from .env files in production (secure default). Production platforms use os.environ. To allow .env in production: policies.allow_dotenv_in_production: True"

    # Enforce allowed sources
    if policies.enforce_allowed_sources and key in policies.enforce_allowed_sources:
        allowed = policies.enforce_allowed_sources[key]
        if source not in allowed:
            return f"{key} must be sourced from one of: {', '.join(allowed)} (actual: {source})"

    return None


async def resolve_async(
    model: Type[T],
    resolvers: Optional[List[Resolver]] = None,
    options: Optional[ResolveOptions] = None,
) -> T:
    """
    Async version of resolve() - use only when you have async resolvers or are already in async context.

    For most use cases, use resolve() (sync) instead.

    Args:
        model: Pydantic BaseModel class defining the schema
        resolvers: List of resolvers to load from (default: [process_env()])
        options: Resolution options (policies, audit, etc.)

    Returns:
        Instance of model with validated environment variables

    Raises:
        ValueError: If validation fails or policies are violated

    Example:
        >>> from pydantic import BaseModel, HttpUrl
        >>> from python_env_resolver import resolve_async, process_env
        >>>
        >>> class Config(BaseModel):
        ...     port: int = 3000
        ...     database_url: HttpUrl
        ...
        >>> config = await resolve_async(Config)
        >>> print(config.port)  # Type-safe!
    """
    if resolvers is None:
        resolvers = [process_env()]

    if options is None:
        options = ResolveOptions()

    # Determine if audit should be enabled
    enable_audit = options.enable_audit
    if enable_audit is None:
        enable_audit = _is_production(options)

    # Load from all resolvers
    merged_env, provenance = await _resolve_from_resolvers(
        resolvers,
        options.interpolate,
        options.strict,
        options.priority,
    )

    # Apply policies and collect errors
    policy_errors: List[str] = []

    for key in model.model_fields.keys():
        key_upper = key.upper()
        if key_upper in provenance:
            policy_error = _apply_policies(
                key_upper,
                provenance[key_upper].source,
                options.policies,
                options,
            )
            if policy_error:
                policy_errors.append(policy_error)

                if enable_audit:
                    log_audit_event(AuditEvent(
                        type="policy_violation",
                        timestamp=time.time(),
                        key=key_upper,
                        source=provenance[key_upper].source,
                        error=policy_error
                    ))

    if policy_errors:
        raise ValueError("Policy violations:\n" + "\n".join(f"  - {e}" for e in policy_errors))

    # Build a dict for Pydantic validation
    # For fields with validation_alias, keep the alias key
    # For fields without, map UPPERCASE env key -> lowercase field
    data_for_pydantic = {}

    # First, add all uppercase env vars AS-IS (for validation_alias to work)
    data_for_pydantic.update(merged_env)

    # Then, for fields without validation_alias, add lowercase mapping
    for field_name, field_info in model.model_fields.items():
        if not field_info.validation_alias:
            # No alias - use UPPERCASE convention
            env_key = field_name.upper()
            if env_key in merged_env:
                # Add lowercase key for Pydantic
                data_for_pydantic[field_name] = merged_env[env_key]

    # Validate with Pydantic
    try:
        instance = model.model_validate(data_for_pydantic)

        # Audit successful loads
        if enable_audit:
            for field_name in model.model_fields.keys():
                env_key = field_name.upper()
                if env_key in provenance:
                    log_audit_event(AuditEvent(
                        type="env_loaded",
                        timestamp=time.time(),
                        key=env_key,
                        source=provenance[env_key].source,
                        metadata={"cached": provenance[env_key].cached}
                    ))

            log_audit_event(AuditEvent(
                type="validation_success",
                timestamp=time.time(),
                metadata={"variable_count": len(model.model_fields)}
            ))

        return instance

    except ValidationError as e:
        if enable_audit:
            log_audit_event(AuditEvent(
                type="validation_failure",
                timestamp=time.time(),
                error=str(e)
            ))
        raise ValueError(f"Environment validation failed:\n{e}")


async def safe_resolve_async(
    model: Type[T],
    resolvers: Optional[List[Resolver]] = None,
    options: Optional[ResolveOptions] = None,
) -> ResolveResult:
    """
    Async safe version that doesn't raise exceptions.

    Similar to Zod's safeParse() - returns a result object.

    Args:
        model: Pydantic BaseModel class defining the schema
        resolvers: List of resolvers to load from (default: [process_env()])
        options: Resolution options (policies, audit, etc.)

    Returns:
        ResolveResult with success flag, data, or structured error

    Example:
        >>> result = await safe_resolve_async(Config)
        >>> if result.success:
        ...     print(result.data.port)
        ... else:
        ...     # Access structured error
        ...     if result.error.type == "validation_error":
        ...         print(f"Field {result.error.field}: {result.error.message}")
        ...     # Or as string
        ...     print(f"Error: {result.error}")
    """
    try:
        data = await resolve_async(model, resolvers, options)
        return ResolveResult(success=True, data=data)
    except ValueError as e:
        # Policy violation or validation error
        error_msg = str(e)
        if "Policy violations:" in error_msg:
            error = ResolveError(
                type="policy_violation",
                message=error_msg
            )
        else:
            error = ResolveError(
                type="validation_error",
                message=error_msg
            )
        return ResolveResult(success=False, error=error)
    except RuntimeError as e:
        # Resolver error
        error_msg = str(e)
        error = ResolveError(
            type="resolver_error",
            message=error_msg
        )
        return ResolveResult(success=False, error=error)
    except Exception as e:
        # Generic error
        error = ResolveError(
            type="validation_error",
            message=str(e)
        )
        return ResolveResult(success=False, error=error)


def _run_sync(coro_factory: Callable[[], Awaitable[R]]) -> R:
    """
    Execute an async resolver path from synchronous code.

    If an event loop is already running (e.g. Jupyter), the coroutine runs on a
    dedicated thread to avoid RuntimeError from asyncio.run().
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())  # type: ignore[arg-type]

    result: Dict[str, Any] = {}

    def runner() -> None:
        try:
            result["value"] = asyncio.run(coro_factory())  # type: ignore[arg-type]
        except BaseException as exc:  # pragma: no cover - re-raised below
            result["error"] = exc

    thread = threading.Thread(
        target=runner,
        name="python-env-resolver-sync",
        daemon=True,
    )
    thread.start()
    thread.join()

    if "error" in result:
        raise result["error"]  # type: ignore[misc]

    if "value" not in result:
        raise RuntimeError("resolve_sync failed to produce a value")

    return cast(R, result["value"])


def resolve(
    model: Type[T],
    resolvers: Optional[List[Resolver]] = None,
    options: Optional[ResolveOptions] = None,
) -> T:
    """
    Resolve environment variables using a Pydantic BaseModel (sync).

    This is the main API for most users. It automatically detects if running
    in an async context and handles it safely.

    Args:
        model: Pydantic BaseModel class defining the schema
        resolvers: List of resolvers to load from (default: [process_env()])
        options: Resolution options (policies, audit, etc.)

    Returns:
        Instance of model with validated environment variables

    Raises:
        ValueError: If validation fails or policies are violated

    Example:
        >>> from pydantic import BaseModel
        >>> from python_env_resolver import resolve
        >>>
        >>> class Config(BaseModel):
        ...     port: int = 3000
        ...     database_url: str
        ...
        >>> config = resolve(Config)  # Sync - works anywhere!
    """
    return _run_sync(lambda: resolve_async(model, resolvers=resolvers, options=options))


def safe_resolve(
    model: Type[T],
    resolvers: Optional[List[Resolver]] = None,
    options: Optional[ResolveOptions] = None,
) -> ResolveResult:
    """
    Safe version of resolve() that doesn't raise exceptions (sync).

    Similar to Zod's safeParse() - returns a result object.

    Args:
        model: Pydantic BaseModel class defining the schema
        resolvers: List of resolvers to load from (default: [process_env()])
        options: Resolution options (policies, audit, etc.)

    Returns:
        ResolveResult with success flag, data, or structured error

    Example:
        >>> result = safe_resolve(Config)
        >>> if result.success:
        ...     print(result.data.port)
        ... else:
        ...     print(f"Error: {result.error}")
    """
    return _run_sync(lambda: safe_resolve_async(model, resolvers=resolvers, options=options))


def from_env(
    model: Type[T],
    options: Optional[ResolveOptions] = None,
) -> T:
    """
    Load configuration from os.environ (sync).

    This is the most common use case - loading configuration from environment
    variables set by your deployment platform (Docker, Kubernetes, cloud providers, etc.).

    Automatically detects async contexts (FastAPI/uvicorn imports) and handles safely.

    Args:
        model: Pydantic BaseModel class defining the schema
        options: Resolution options (policies, audit, etc.)

    Returns:
        Instance of model with validated environment variables

    Example:
        >>> from pydantic import BaseModel
        >>> from python_env_resolver import from_env
        >>>
        >>> class Config(BaseModel):
        ...     port: int = 3000
        ...     database_url: str
        ...
        >>> config = from_env(Config)  # Sync - works in FastAPI!
    """
    return resolve(model, resolvers=[process_env()], options=options)


async def from_env_async(
    model: Type[T],
    options: Optional[ResolveOptions] = None,
) -> T:
    """
    Async version of from_env() - use only when already in async context.

    For most use cases, use from_env() (sync) instead.

    Args:
        model: Pydantic BaseModel class defining the schema
        options: Resolution options (policies, audit, etc.)

    Returns:
        Instance of model with validated environment variables

    Example:
        >>> from pydantic import BaseModel
        >>> from python_env_resolver import from_env_async
        >>>
        >>> class Config(BaseModel):
        ...     port: int = 3000
        ...     database_url: str
        ...
        >>> config = await from_env_async(Config)
    """
    return await resolve_async(model, resolvers=[process_env()], options=options)
