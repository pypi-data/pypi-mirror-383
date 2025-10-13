"""Environment configuration management

Handles loading and validation of environment-specific configuration from YAML files.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

from confiture.exceptions import ConfigurationError


class DatabaseConfig(BaseModel):
    """Database connection configuration.

    Can be initialized from a connection URL or individual parameters.
    """

    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str = ""

    @classmethod
    def from_url(cls, url: str) -> "DatabaseConfig":
        """Parse database configuration from PostgreSQL URL.

        Args:
            url: PostgreSQL connection URL (postgresql://user:pass@host:port/dbname)

        Returns:
            DatabaseConfig instance

        Example:
            >>> config = DatabaseConfig.from_url("postgresql://user:pass@localhost:5432/mydb")
            >>> config.host
            'localhost'
        """
        import re

        # Parse URL: postgresql://user:pass@host:port/dbname
        pattern = r"(?:postgresql|postgres)://(?:([^:]+):([^@]+)@)?([^:/]+)(?::(\d+))?/(.+)"
        match = re.match(pattern, url)

        if not match:
            raise ValueError(f"Invalid PostgreSQL URL: {url}")

        user, password, host, port, database = match.groups()

        return cls(
            host=host or "localhost",
            port=int(port) if port else 5432,
            database=database,
            user=user or "postgres",
            password=password or "",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for use with create_connection."""
        return {
            "database": {
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "user": self.user,
                "password": self.password,
            }
        }


class Environment(BaseModel):
    """Environment configuration

    Loaded from db/environments/{env_name}.yaml files.

    Attributes:
        name: Environment name (e.g., "local", "production")
        database_url: PostgreSQL connection URL
        include_dirs: Directories to include when building schema
        exclude_dirs: Directories to exclude from schema build
        migration_table: Table name for tracking migrations
        auto_backup: Whether to automatically backup before migrations
        require_confirmation: Whether to require user confirmation for risky operations
    """

    name: str
    database_url: str
    include_dirs: list[str]
    exclude_dirs: list[str] = Field(default_factory=list)
    migration_table: str = "confiture_migrations"
    auto_backup: bool = True
    require_confirmation: bool = True

    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration from database_url.

        Returns:
            DatabaseConfig instance
        """
        return DatabaseConfig.from_url(self.database_url)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate PostgreSQL connection URL format"""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                f"Invalid database_url: must start with postgresql:// or postgres://, got: {v}"
            )
        return v

    @classmethod
    def load(cls, env_name: str, project_dir: Path | None = None) -> "Environment":
        """Load environment configuration from YAML file

        Args:
            env_name: Environment name (e.g., "local", "production")
            project_dir: Project root directory. If None, uses current directory.

        Returns:
            Environment configuration object

        Raises:
            ConfigurationError: If config file not found, invalid, or missing required fields

        Example:
            >>> env = Environment.load("local")
            >>> print(env.database_url)
            postgresql://localhost/myapp_local
        """
        if project_dir is None:
            project_dir = Path.cwd()

        # Find config file
        config_path = project_dir / "db" / "environments" / f"{env_name}.yaml"

        if not config_path.exists():
            raise ConfigurationError(
                f"Environment config not found: {config_path}\n"
                f"Expected: db/environments/{env_name}.yaml"
            )

        # Load YAML
        try:
            with open(config_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_path}: {e}") from e

        if not isinstance(data, dict):
            raise ConfigurationError(
                f"Invalid config format in {config_path}: expected dictionary, got {type(data)}"
            )

        # Validate required fields
        if "database_url" not in data:
            raise ConfigurationError(f"Missing required field 'database_url' in {config_path}")

        if "include_dirs" not in data:
            raise ConfigurationError(f"Missing required field 'include_dirs' in {config_path}")

        # Resolve paths to absolute
        include_dirs = []
        for dir_path in data["include_dirs"]:
            abs_path = (project_dir / dir_path).resolve()
            if not abs_path.exists():
                raise ConfigurationError(
                    f"Include directory does not exist: {abs_path}\nSpecified in {config_path}"
                )
            include_dirs.append(str(abs_path))

        data["include_dirs"] = include_dirs

        # Resolve exclude_dirs if present
        if "exclude_dirs" in data:
            exclude_dirs = []
            for dir_path in data["exclude_dirs"]:
                abs_path = (project_dir / dir_path).resolve()
                exclude_dirs.append(str(abs_path))
            data["exclude_dirs"] = exclude_dirs

        # Create Environment instance
        try:
            return cls(**data)
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration in {config_path}: {e}") from e
