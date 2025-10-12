"""
Tests for new features: prefix, file_env, ResolverNames, ResolveError.
"""

import os
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel

from python_env_resolver import (
    ResolverNames,
    file_env,
    process_env,
    resolve_async,
    safe_resolve_async,
)


class TestPrefixSupport:
    """Test prefix parameter in process_env()."""

    @pytest.mark.asyncio
    async def test_prefix_filters_and_strips(self):
        """Test that prefix filters and strips environment variables."""
        # Setup
        os.environ["APP_DATABASE_URL"] = "postgres://localhost/db"
        os.environ["APP_PORT"] = "3000"
        os.environ["OTHER_VAR"] = "should_not_appear"

        class Config(BaseModel):
            database_url: str
            port: int

        # Test
        config = await resolve_async(
            Config,
            resolvers=[process_env(prefix="APP_")]
        )

        assert config.database_url == "postgres://localhost/db"
        assert config.port == 3000

        # Cleanup
        del os.environ["APP_DATABASE_URL"]
        del os.environ["APP_PORT"]
        del os.environ["OTHER_VAR"]


class TestFileEnv:
    """Test file_env() resolver for _FILE convention."""

    @pytest.mark.asyncio
    async def test_file_env_loads_from_files(self):
        """Test that file_env loads values from files."""
        # Create temporary secret files
        with tempfile.TemporaryDirectory() as tmpdir:
            db_secret = Path(tmpdir) / "db_secret"
            db_secret.write_text("postgres://secret/db")

            api_secret = Path(tmpdir) / "api_secret"
            api_secret.write_text("secret_api_key_123")

            # Setup env vars pointing to files
            os.environ["DATABASE_URL_FILE"] = str(db_secret)
            os.environ["API_KEY_FILE"] = str(api_secret)

            class Config(BaseModel):
                database_url: str
                api_key: str

            # Test
            config = await resolve_async(
                Config,
                resolvers=[file_env()]
            )

            assert config.database_url == "postgres://secret/db"
            assert config.api_key == "secret_api_key_123"

            # Cleanup
            del os.environ["DATABASE_URL_FILE"]
            del os.environ["API_KEY_FILE"]

    @pytest.mark.asyncio
    async def test_file_env_with_process_env_override(self):
        """Test that process_env can override file_env."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_secret = Path(tmpdir) / "db_secret"
            db_secret.write_text("postgres://file/db")

            os.environ["DATABASE_URL_FILE"] = str(db_secret)
            os.environ["DATABASE_URL"] = "postgres://override/db"

            class Config(BaseModel):
                database_url: str

            # file_env first, then process_env (should override)
            config = await resolve_async(
                Config,
                resolvers=[file_env(), process_env()]
            )

            assert config.database_url == "postgres://override/db"

            # Cleanup
            del os.environ["DATABASE_URL_FILE"]
            del os.environ["DATABASE_URL"]


class TestResolverNames:
    """Test ResolverNames constants."""

    def test_resolver_names_constants(self):
        """Test that ResolverNames provides correct constants."""
        assert ResolverNames.PROCESS_ENV == "process.env"
        assert ResolverNames.FILE_ENV == "file.env"

    def test_resolver_names_dotenv_helper(self):
        """Test dotenv_for() helper method."""
        assert ResolverNames.dotenv_for(".env") == "dotenv(.env)"
        assert ResolverNames.dotenv_for(".env.local") == "dotenv(.env.local)"
        assert ResolverNames.dotenv_for(".env.production") == "dotenv(.env.production)"


class TestResolveError:
    """Test structured ResolveError."""

    @pytest.mark.asyncio
    async def test_resolve_error_structure(self):
        """Test that ResolveError provides structured error info."""
        # Missing required field
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

        class Config(BaseModel):
            database_url: str

        result = await safe_resolve_async(Config)

        assert not result.success
        assert result.error is not None
        assert result.error.type in ["validation_error", "policy_violation", "resolver_error"]
        assert result.error.message  # Should have a message
        assert str(result.error) == result.error.message  # __str__() works

    @pytest.mark.asyncio
    async def test_resolve_error_backward_compat(self):
        """Test that ResolveError is backward compatible (can be used as string)."""
        if "PORT" in os.environ:
            del os.environ["PORT"]

        class Config(BaseModel):
            port: int

        result = await safe_resolve_async(Config)

        assert not result.success
        # Should be able to use error as string
        error_str = str(result.error)
        assert isinstance(error_str, str)
        assert len(error_str) > 0

