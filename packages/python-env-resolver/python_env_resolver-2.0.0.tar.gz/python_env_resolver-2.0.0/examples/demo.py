"""
Demo of python-env-resolver features.

Run with: uv run python examples/demo.py
"""

import asyncio
import os
from datetime import timedelta
from typing import Literal

from pydantic import BaseModel, HttpUrl, field_validator

from python_env_resolver import (
    TTL,
    CacheOptions,
    PolicyConfig,
    ResolveOptions,
    cached,
    from_env,
    from_env_async,
    get_audit_log,
    resolve_async,
    safe_resolve_async,
    validate_port,
    validate_url,
)


class Config(BaseModel):
    """Application configuration schema."""

    port: int = 3000
    database_url: HttpUrl
    node_env: Literal["development", "production", "test"] = "development"
    debug: bool = False
    api_key: str | None = None


class ProductionConfig(BaseModel):
    """Production config with enhanced validators."""

    api_url: str
    port: int

    @field_validator("api_url")
    @classmethod
    def check_api_url(cls, v: str) -> str:
        return validate_url(v, require_https=True)

    @field_validator("port")
    @classmethod
    def check_port(cls, v: int) -> int:
        return validate_port(v, min_port=1024, max_port=65535)


async def demo_basic():
    """Demo: Basic usage."""
    print("\n=== Demo 1: Basic Usage ===")

    # Set some environment variables
    os.environ["PORT"] = "8080"
    os.environ["DATABASE_URL"] = "https://db.example.com"
    os.environ["NODE_ENV"] = "production"

    config = await resolve_async(Config)

    print(f"Port: {config.port} (type: {type(config.port).__name__})")
    print(f"Database URL: {config.database_url}")
    print(f"Environment: {config.node_env}")
    print(f"Debug: {config.debug}")


async def demo_safe_resolve():
    """Demo: Safe error handling."""
    print("\n=== Demo 2: Safe Resolve ===")

    # Missing required field
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]

    result = await safe_resolve_async(Config)

    if result.success:
        print(f"Success! Port: {result.data.port}")
    else:
        print(f"Validation failed: {str(result.error)[:100]}...")


async def demo_caching():
    """Demo: TTL caching."""
    print("\n=== Demo 3: TTL Caching ===")

    call_count = 0

    class MockSecretsResolver:
        name = "secrets-manager"
        metadata = {}

        async def load(self):
            nonlocal call_count
            call_count += 1
            print(f"  → Loading from secrets manager (call #{call_count})")
            await asyncio.sleep(0.1)  # Simulate network delay
            return {
                "PORT": "3000",
                "DATABASE_URL": "https://db.example.com",
            }

    # Wrap with caching
    cached_resolver = cached(
        MockSecretsResolver(),
        CacheOptions(ttl=2, stale_while_revalidate=True)
    )

    print("Call 1 (cache miss):")
    data1 = await cached_resolver.load()
    print(f"  ← Got data: {data1['PORT']}")

    print("\nCall 2 (cached, instant):")
    data2 = await cached_resolver.load()
    print(f"  ← Got data: {data2['PORT']} [CACHED]")

    print("\nWaiting 2.5s for TTL to expire...")
    await asyncio.sleep(2.5)

    print("\nCall 3 (stale-while-revalidate):")
    data3 = await cached_resolver.load()
    print(f"  ← Got data instantly: {data3['PORT']} [STALE]")
    print("  → Background refresh triggered")

    await asyncio.sleep(0.2)
    print(f"\nTotal secrets manager calls: {call_count}")


async def demo_audit():
    """Demo: Audit logging."""
    print("\n=== Demo 4: Audit Logging ===")

    os.environ["PORT"] = "8080"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    _config = await resolve_async(
        Config,
        options=ResolveOptions(enable_audit=True)
    )

    logs = get_audit_log()
    print(f"\nAudit log ({len(logs)} events):")
    for log in logs:
        if log.key:
            print(f"  - {log.type}: {log.key} from {log.source}")
        else:
            print(f"  - {log.type}")


async def demo_api_shortcuts():
    """Demo: API shortcuts and enhanced validators."""
    print("\n=== Demo 5: API Shortcuts (from_env) ===")

    os.environ["API_URL"] = "https://api.example.com"
    os.environ["PORT"] = "8080"

    # Async shortcut
    config = await from_env_async(ProductionConfig)
    print(f"API URL: {config.api_url} (HTTPS validated)")
    print(f"Port: {config.port} (in range 1024-65535)")

    # Sync shortcut
    config_sync = from_env(ProductionConfig)
    print(f"Sync API also works: {config_sync.port}")


async def demo_timedelta_ttl():
    """Demo: Timedelta support for TTL."""
    print("\n=== Demo 6: Timedelta TTL Support ===")

    # Both constants and timedelta work
    opts1 = CacheOptions(ttl=TTL.minutes5, max_age=TTL.hour)
    opts2 = CacheOptions(ttl=timedelta(minutes=5), max_age=timedelta(hours=1))

    print(f"TTL constants: {opts1.get_ttl_seconds()}s, {opts1.get_max_age_seconds()}s")
    print(f"Timedelta: {opts2.get_ttl_seconds()}s, {opts2.get_max_age_seconds()}s")
    print("Both approaches are equivalent")


async def demo_policies():
    """Demo: Security policies with PolicyConfig."""
    print("\n=== Demo 7: Security Policies (PolicyConfig) ===")

    _policy = PolicyConfig(
        allow_dotenv_in_production=None,  # Block .env in production (default)
        enforce_allowed_sources={"DATABASE_URL": ["process.env", "vault-secrets"]},
    )

    print("Policy configured:")
    print("  - .env blocked in production (default)")
    print("  - DATABASE_URL must come from: process.env or vault-secrets")
    print("Policy enforcement happens at resolve time")


async def main():
    """Run all demos."""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       python-env-resolver Demo                        ║")
    print("║  Type-safe environment configuration for Python      ║")
    print("╚═══════════════════════════════════════════════════════╝")

    await demo_basic()
    await demo_safe_resolve()
    await demo_caching()
    await demo_audit()
    await demo_api_shortcuts()
    await demo_timedelta_ttl()
    await demo_policies()

    print("\nAll demos complete.")
    print("\nKey features demonstrated:")
    print("  - API shortcuts: from_env() (sync) / from_env_async() (async)")
    print("  - Enhanced validators: validate_url(require_https=True)")
    print("  - Timedelta support: CacheOptions(ttl=timedelta(minutes=5))")
    print("  - PolicyConfig: Security policy configuration")
    print("  - Explicit types: ResolveResult, Resolver protocol")


if __name__ == "__main__":
    asyncio.run(main())

