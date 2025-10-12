"""
Built-in resolvers for environment variable resolution.

Provides resolvers for common sources: os.environ and .env files.
"""

import os
from pathlib import Path
from typing import Dict

from dotenv import dotenv_values


class ProcessEnvResolver:
    """
    Resolver that loads from os.environ (process environment variables).

    This is the default resolver and works in all environments.

    Args:
        prefix: Optional prefix to filter environment variables (e.g., "APP_" loads only APP_* vars)
    """

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.name = "process.env"
        self.metadata: Dict = {}

    async def load(self) -> Dict[str, str]:
        """Load from os.environ, optionally filtering by prefix."""
        result = {}
        for k, v in os.environ.items():
            if v is not None:
                # If prefix is set, only include vars that start with it
                if self.prefix:
                    if k.startswith(self.prefix):
                        # Strip the prefix from the key
                        key_without_prefix = k[len(self.prefix):]
                        result[key_without_prefix] = v
                else:
                    result[k] = v
        return result


class DotenvResolver:
    """
    Resolver that loads from .env files.

    Args:
        path: Path to .env file (default: ".env")
    """

    def __init__(self, path: str = ".env"):
        self.path = path
        self.name = f"dotenv({path})"
        self.metadata: Dict = {}

    async def load(self) -> Dict[str, str]:
        """Load from .env file."""
        env_path = Path(self.path)
        if not env_path.exists():
            return {}

        values = dotenv_values(self.path)
        # Filter out None values
        return {k: v for k, v in values.items() if v is not None}


class FileEnvResolver:
    """
    Resolver that loads from files referenced by *_FILE environment variables.

    This follows the Docker/Kubernetes secrets convention where:
    - DATABASE_URL_FILE=/run/secrets/db reads the file and injects DATABASE_URL
    - API_KEY_FILE=/run/secrets/api reads the file and injects API_KEY

    Common in containerized environments for loading secrets from mounted volumes.
    """

    def __init__(self) -> None:
        self.name = "file.env"
        self.metadata: Dict = {}

    async def load(self) -> Dict[str, str]:
        """Load from files referenced by *_FILE env vars."""
        result = {}
        for key, file_path in os.environ.items():
            if key.endswith("_FILE") and file_path:
                # Strip _FILE suffix to get the target variable name
                target_key = key[:-5]  # Remove "_FILE"

                try:
                    # Read the file content
                    file_path_obj = Path(file_path)

                    # Security: Only read regular files (no symlinks, devices, etc.)
                    if (file_path_obj.exists() and
                        file_path_obj.is_file() and
                        not file_path_obj.is_symlink()):
                        content = file_path_obj.read_text().strip()
                        result[target_key] = content
                except Exception:
                    # Silently skip files that can't be read
                    # This allows graceful degradation
                    pass

        return result


def process_env(prefix: str = "") -> ProcessEnvResolver:
    """
    Create a resolver for os.environ.

    Args:
        prefix: Optional prefix to filter environment variables.
                If set to "APP_", only loads APP_* vars and strips the prefix.
                Example: APP_DATABASE_URL becomes DATABASE_URL

    Returns:
        ProcessEnvResolver instance

    Example:
        >>> from python_env_resolver import resolve, process_env
        >>> # Load all env vars
        >>> config = await resolve(AppConfig, resolvers=[process_env()])
        >>>
        >>> # Load only APP_* vars (strips prefix)
        >>> config = await resolve(AppConfig, resolvers=[process_env(prefix="APP_")])
    """
    return ProcessEnvResolver(prefix=prefix)


def dotenv(path: str = ".env") -> DotenvResolver:
    """
    Create a resolver for .env files.

    Args:
        path: Path to .env file (default: ".env")

    Returns:
        DotenvResolver instance

    Example:
        >>> from python_env_resolver import resolve, dotenv
        >>> config = await resolve.with_sources(
        ...     [dotenv(".env.local"), {"DATABASE_URL": str}]
        ... )
    """
    return DotenvResolver(path)


def file_env() -> FileEnvResolver:
    """
    Create a resolver for Docker/Kubernetes file-based secrets.

    Loads environment variables from files referenced by *_FILE env vars.
    This is commonly used in containerized environments where secrets are
    mounted as files.

    Returns:
        FileEnvResolver instance

    Example:
        >>> from python_env_resolver import resolve, file_env, process_env
        >>> # export DATABASE_URL_FILE=/run/secrets/db
        >>> config = await resolve(
        ...     AppConfig,
        ...     resolvers=[file_env(), process_env()]
        ... )
        >>> # DATABASE_URL will contain the contents of /run/secrets/db
    """
    return FileEnvResolver()
