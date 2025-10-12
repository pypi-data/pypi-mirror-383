"""
Constants for python-env-resolver.

Provides canonical names for built-in resolvers to avoid typos in policy configuration.
"""


class ResolverNames:
    """
    Canonical names for built-in resolvers.

    Use these constants when configuring policies to avoid typos.
    Note: dotenv() includes the file path in its name, so use dotenv_for() helper.

    Example:
        >>> from python_env_resolver import ResolverNames, PolicyConfig, ResolveOptions
        >>>
        >>> options = ResolveOptions(
        ...     policies=PolicyConfig(
        ...         enforce_allowed_sources={
        ...             "DATABASE_URL": [ResolverNames.PROCESS_ENV, "vault-secrets"],
        ...             "LOG_LEVEL": [ResolverNames.dotenv_for(".env"), ResolverNames.PROCESS_ENV]
        ...         }
        ...     )
        ... )
    """

    PROCESS_ENV = "process.env"
    FILE_ENV = "file.env"

    @staticmethod
    def dotenv_for(path: str = ".env") -> str:
        """
        Get the canonical name for a dotenv resolver with a specific path.

        Args:
            path: Path to .env file (default: ".env")

        Returns:
            Canonical resolver name like "dotenv(.env)" or "dotenv(.env.local)"

        Example:
            >>> ResolverNames.dotenv_for(".env")
            'dotenv(.env)'
            >>> ResolverNames.dotenv_for(".env.production")
            'dotenv(.env.production)'
        """
        return f"dotenv({path})"
