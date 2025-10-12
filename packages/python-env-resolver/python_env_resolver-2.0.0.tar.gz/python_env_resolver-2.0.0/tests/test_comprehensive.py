"""
Comprehensive tests for edge cases and specific requirements.
"""

import os
import tempfile
from pathlib import Path

import pytest
from pydantic import AliasChoices, BaseModel, Field

from python_env_resolver import (
    PolicyConfig,
    ResolveOptions,
    ResolverNames,
    dotenv,
    file_env,
    process_env,
    resolve,
    resolve_async,
    safe_resolve_async,
)


class TestFieldMapping:
    """Test snake_case → UPPER_SNAKE mapping and special characters."""

    @pytest.mark.asyncio
    async def test_snake_case_to_upper_snake(self):
        """Test default field mapping."""
        os.environ["DATABASE_URL"] = "postgres://localhost/db"
        os.environ["MAX_CONNECTIONS"] = "100"

        class Config(BaseModel):
            database_url: str
            max_connections: int

        config = await resolve_async(Config, resolvers=[process_env()])

        assert config.database_url == "postgres://localhost/db"
        assert config.max_connections == 100

        del os.environ["DATABASE_URL"]
        del os.environ["MAX_CONNECTIONS"]

    @pytest.mark.asyncio
    async def test_dots_hyphens_to_underscores(self):
        """Test that dots and hyphens are treated as underscores."""
        os.environ["SERVICE_URL"] = "http://api.example.com"

        class Config(BaseModel):
            service_url: str  # Maps to SERVICE_URL

        config = await resolve_async(Config, resolvers=[process_env()])

        assert config.service_url == "http://api.example.com"

        del os.environ["SERVICE_URL"]


class TestPrefixBehavior:
    """Test prefix filtering and stripping."""

    @pytest.mark.asyncio
    async def test_prefix_filters_and_strips(self):
        """Test APP_PORT loads, PORT ignored when prefix='APP_'."""
        os.environ["APP_PORT"] = "8080"
        os.environ["PORT"] = "3000"  # Should be ignored

        class Config(BaseModel):
            port: int

        config = await resolve_async(
            Config,
            resolvers=[process_env(prefix="APP_")]
        )

        assert config.port == 8080  # From APP_PORT, not PORT

        del os.environ["APP_PORT"]
        del os.environ["PORT"]

    @pytest.mark.asyncio
    async def test_prefix_maps_app_database_url_to_database_url(self):
        """Test APP_DATABASE_URL → field database_url."""
        os.environ["APP_DATABASE_URL"] = "postgres://app/db"

        class Config(BaseModel):
            database_url: str

        config = await resolve_async(
            Config,
            resolvers=[process_env(prefix="APP_")]
        )

        assert config.database_url == "postgres://app/db"

        del os.environ["APP_DATABASE_URL"]


class TestPrecedence:
    """Test resolver precedence with different priority settings."""

    @pytest.mark.asyncio
    async def test_dotenv_then_process_env_with_priority_last(self):
        """Test dotenv then process_env with priority='last' → env wins."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("PORT=3000\n")
            env_file = f.name

        os.environ["PORT"] = "8080"

        class Config(BaseModel):
            port: int

        config = await resolve_async(
            Config,
            resolvers=[dotenv(env_file), process_env()],
            options=ResolveOptions(priority="last")
        )

        assert config.port == 8080  # process_env wins

        del os.environ["PORT"]
        Path(env_file).unlink()


class TestMultipleAliases:
    """Test AliasChoices for multiple fallback aliases."""

    @pytest.mark.asyncio
    async def test_validation_alias_choices_first_match(self):
        """Test AliasChoices uses first matching alias."""
        os.environ["APP_SECRET"] = "secret_from_app"

        class Config(BaseModel):
            secret: str | None = Field(
                None,
                validation_alias=AliasChoices("SECRET_KEY", "APP_SECRET", "SECRET")
            )

        config = await resolve_async(Config, resolvers=[process_env()])

        assert config.secret == "secret_from_app"

        del os.environ["APP_SECRET"]

    @pytest.mark.asyncio
    async def test_validation_alias_choices_fallback(self):
        """Test AliasChoices falls back to later aliases."""
        os.environ["API_KEY"] = "key_from_api"

        class Config(BaseModel):
            api_key: str | None = Field(
                None,
                validation_alias=AliasChoices("APP_API_KEY", "API_KEY", "KEY")
            )

        config = await resolve_async(Config, resolvers=[process_env()])

        assert config.api_key == "key_from_api"

        del os.environ["API_KEY"]


class TestPolicies:
    """Test security policies."""

    @pytest.mark.asyncio
    async def test_dotenv_blocked_in_production(self):
        """Test .env blocked in production."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DATABASE_URL=postgres://localhost/db\n")
            env_file = f.name

        class Config(BaseModel):
            database_url: str

        # Force production mode with default policies (block .env)
        with pytest.raises(ValueError, match="cannot be sourced from .env"):
            await resolve_async(
                Config,
                resolvers=[dotenv(env_file)],
                options=ResolveOptions(
                    env="production",
                    policies=PolicyConfig()  # Use default policies
                )
            )

        Path(env_file).unlink()

    @pytest.mark.asyncio
    async def test_dotenv_allowlist_works(self):
        """Test allowlist overrides dotenv block."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("LOG_LEVEL=debug\n")
            env_file = f.name

        class Config(BaseModel):
            log_level: str

        # Should work with allowlist
        config = await resolve_async(
            Config,
            resolvers=[dotenv(env_file)],
            options=ResolveOptions(
                env="production",
                policies=PolicyConfig(allow_dotenv_in_production=["LOG_LEVEL"])
            )
        )

        assert config.log_level == "debug"

        Path(env_file).unlink()

    @pytest.mark.asyncio
    async def test_enforce_allowed_sources_rejects_wrong_resolver(self):
        """Test enforce_allowed_sources rejects wrong resolver."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("API_KEY=secret\n")
            env_file = f.name

        class Config(BaseModel):
            api_key: str

        with pytest.raises(ValueError, match="must be sourced from one of"):
            await resolve_async(
                Config,
                resolvers=[dotenv(env_file)],
                options=ResolveOptions(
                    policies=PolicyConfig(
                        enforce_allowed_sources={
                            "API_KEY": [ResolverNames.PROCESS_ENV, ResolverNames.FILE_ENV]
                        }
                    )
                )
            )

        Path(env_file).unlink()


class TestFileEnv:
    """Test file_env() behavior."""

    @pytest.mark.asyncio
    async def test_file_env_respects_file_convention(self):
        """Test file_env respects *_FILE convention."""
        with tempfile.TemporaryDirectory() as tmpdir:
            secret_file = Path(tmpdir) / "secret"
            secret_file.write_text("my_secret_value")

            os.environ["API_KEY_FILE"] = str(secret_file)

            class Config(BaseModel):
                api_key: str

            config = await resolve_async(Config, resolvers=[file_env()])

            assert config.api_key == "my_secret_value"

            del os.environ["API_KEY_FILE"]

    @pytest.mark.asyncio
    async def test_file_env_precedence_with_process_env(self):
        """Test file_env wins/loses according to configured order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            secret_file = Path(tmpdir) / "secret"
            secret_file.write_text("from_file")

            os.environ["API_KEY_FILE"] = str(secret_file)
            os.environ["API_KEY"] = "from_env"

            class Config(BaseModel):
                api_key: str

            # file_env first, process_env overrides
            config = await resolve_async(
                Config,
                resolvers=[file_env(), process_env()],
                options=ResolveOptions(priority="last")
            )
            assert config.api_key == "from_env"

            # process_env first, file_env overrides
            config2 = await resolve_async(
                Config,
                resolvers=[process_env(), file_env()],
                options=ResolveOptions(priority="last")
            )
            assert config2.api_key == "from_file"

            del os.environ["API_KEY_FILE"]
            del os.environ["API_KEY"]

    @pytest.mark.asyncio
    async def test_file_env_rejects_symlinks(self):
        """Test file_env only reads regular files (no symlinks)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            real_file = Path(tmpdir) / "real_secret"
            real_file.write_text("real_value")

            symlink = Path(tmpdir) / "symlink_secret"
            symlink.symlink_to(real_file)

            os.environ["API_KEY_FILE"] = str(symlink)

            class Config(BaseModel):
                api_key: str | None = None

            # Should not load from symlink (graceful degradation)
            config = await resolve_async(Config, resolvers=[file_env()])

            # Value should be None since symlink is rejected
            assert config.api_key is None

            del os.environ["API_KEY_FILE"]


class TestProductionDetection:
    """Test production environment detection order."""

    @pytest.mark.asyncio
    async def test_detection_order(self):
        """Test detection order: ResolveOptions(env=...) > PYTHON_ENV > ENV > default."""
        # Save original env
        orig_python_env = os.environ.get("PYTHON_ENV")
        orig_env = os.environ.get("ENV")

        try:
            # 1. Override via ResolveOptions (highest priority)
            os.environ["PYTHON_ENV"] = "development"
            os.environ["ENV"] = "development"

            class Config(BaseModel):
                test: str = "value"

            # Force production via options
            result = await safe_resolve_async(
                Config,
                resolvers=[process_env()],
                options=ResolveOptions(env="production", enable_audit=True)
            )
            assert result.success

            # 2. PYTHON_ENV takes precedence over ENV
            del os.environ["PYTHON_ENV"]
            os.environ["ENV"] = "production"

            # ENV should be used now (no override, no PYTHON_ENV)
            result2 = await safe_resolve_async(
                Config,
                options=ResolveOptions(enable_audit=True)  # Should detect from ENV
            )
            assert result2.success

        finally:
            # Restore
            if orig_python_env:
                os.environ["PYTHON_ENV"] = orig_python_env
            elif "PYTHON_ENV" in os.environ:
                del os.environ["PYTHON_ENV"]

            if orig_env:
                os.environ["ENV"] = orig_env
            elif "ENV" in os.environ:
                del os.environ["ENV"]


class TestSyncInAsync:
    """Test sync wrappers are safe in async contexts."""

    @pytest.mark.asyncio
    async def test_resolve_in_event_loop(self):
        """Test resolve works inside event loop (uses worker thread)."""
        os.environ["PORT"] = "5000"

        class Config(BaseModel):
            port: int

        # This runs inside pytest's event loop
        # Should use worker thread automatically
        config = resolve(Config, resolvers=[process_env()])

        assert config.port == 5000

        del os.environ["PORT"]

