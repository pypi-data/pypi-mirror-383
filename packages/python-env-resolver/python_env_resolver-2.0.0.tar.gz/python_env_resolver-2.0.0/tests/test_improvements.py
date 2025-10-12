"""
Test the new improvements: from_env, PolicyConfig, timedelta support, etc.
"""

import os
from datetime import timedelta

import pytest
from pydantic import BaseModel

from python_env_resolver import (
    CacheOptions,
    PolicyConfig,
    ResolveResult,
    from_env,
    from_env_async,
    safe_resolve_async,
    validate_number_range,
    validate_port,
    validate_url,
)


class SampleConfig(BaseModel):
    """Sample config for testing (renamed to avoid pytest collection warning)."""
    port: int = 3000
    debug: bool = False
    api_key: str | None = None


class StrictConfig(BaseModel):
    """Config without defaults for testing errors."""

    database_url: str  # Required field
    port: int  # Required field


class TestAPIShortcuts:
    """Test from_env() and from_env() shortcuts."""

    def test_from_env(self):
        os.environ["PORT"] = "8080"
        os.environ["DEBUG"] = "true"
        os.environ["API_KEY"] = "secret123"

        config = from_env(SampleConfig)
        assert config.port == 8080
        assert config.debug is True
        assert config.api_key == "secret123"

        # Cleanup
        del os.environ["PORT"]
        del os.environ["DEBUG"]
        del os.environ["API_KEY"]

    @pytest.mark.asyncio
    async def test_from_env_async(self):
        os.environ["PORT"] = "9090"
        os.environ["DEBUG"] = "false"

        config = await from_env_async(SampleConfig)
        assert config.port == 9090
        assert config.debug is False

        # Cleanup
        del os.environ["PORT"]
        del os.environ["DEBUG"]


class TestResolveResult:
    """Test ResolveResult type."""

    @pytest.mark.asyncio
    async def test_resolve_result_success(self):
        os.environ["PORT"] = "3000"

        result = await safe_resolve_async(SampleConfig)
        assert isinstance(result, ResolveResult)
        assert result.success is True
        assert result.data is not None
        assert result.data.port == 3000
        assert result.error is None

        # Cleanup
        del os.environ["PORT"]

    @pytest.mark.asyncio
    async def test_resolve_result_error(self):
        # Missing required field should fail
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        if "PORT" in os.environ:
            del os.environ["PORT"]

        result = await safe_resolve_async(StrictConfig)
        assert isinstance(result, ResolveResult)
        assert result.success is False
        assert result.data is None
        assert result.error is not None
        error_str = str(result.error).lower()
        assert "validation" in error_str or "database" in error_str


class TestPolicyConfig:
    """Test PolicyConfig (renamed from PolicyOptions)."""

    def test_policy_config_creation(self):
        policy = PolicyConfig(
            allow_dotenv_in_production=["LOG_LEVEL"],
            enforce_allowed_sources={"DATABASE_URL": ["vault-secrets"]},
        )
        assert policy.allow_dotenv_in_production == ["LOG_LEVEL"]
        assert policy.enforce_allowed_sources == {"DATABASE_URL": ["vault-secrets"]}


class TestTimedeltaSupport:
    """Test timedelta support in CacheOptions."""

    def test_timedelta_ttl(self):
        opts = CacheOptions(
            ttl=timedelta(minutes=5), max_age=timedelta(hours=1), stale_while_revalidate=True
        )
        assert opts.get_ttl_seconds() == 300.0
        assert opts.get_max_age_seconds() == 3600.0

    def test_numeric_ttl(self):
        opts = CacheOptions(ttl=300, max_age=3600)
        assert opts.get_ttl_seconds() == 300.0
        assert opts.get_max_age_seconds() == 3600.0


class TestEnhancedValidators:
    """Test enhanced validators with new parameters."""

    def test_validate_url_require_https(self):
        # Should pass
        assert validate_url("https://example.com", require_https=True) == "https://example.com"

        # Should fail - not HTTPS
        with pytest.raises(ValueError, match="must use HTTPS"):
            validate_url("http://example.com", require_https=True)

    def test_validate_port_with_range(self):
        # Should pass
        assert validate_port(8080, min_port=1024, max_port=65535) == 8080

        # Should fail - below min
        with pytest.raises(ValueError, match="between 1024 and 65535"):
            validate_port(80, min_port=1024, max_port=65535)

    def test_validate_number_range(self):
        # Should pass
        assert validate_number_range(50, min_val=1, max_val=100) == 50
        assert validate_number_range(50.5, min_val=1.0, max_val=100.0) == 50.5

        # From string
        assert validate_number_range("75", min_val=1, max_val=100) == 75

        # Should fail - out of range
        with pytest.raises(ValueError, match="at least"):
            validate_number_range(0, min_val=1, max_val=100)

        with pytest.raises(ValueError, match="at most"):
            validate_number_range(150, min_val=1, max_val=100)

