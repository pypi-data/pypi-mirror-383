"""Migration executor for applying and rolling back database migrations."""

import time
from pathlib import Path

import psycopg

from confiture.exceptions import MigrationError
from confiture.models.migration import Migration


class Migrator:
    """Executes database migrations and tracks their state.

    The Migrator class is responsible for:
    - Creating and managing the confiture_migrations tracking table
    - Applying migrations (running up() methods)
    - Rolling back migrations (running down() methods)
    - Recording execution time and checksums
    - Ensuring transaction safety

    Example:
        >>> conn = psycopg.connect("postgresql://localhost/mydb")
        >>> migrator = Migrator(connection=conn)
        >>> migrator.initialize()
        >>> migrator.apply(my_migration)
    """

    def __init__(self, connection: psycopg.Connection):
        """Initialize migrator with database connection.

        Args:
            connection: psycopg3 database connection
        """
        self.connection = connection

    def initialize(self) -> None:
        """Create confiture_migrations tracking table with modern identity trinity.

        Identity pattern:
        - id: Auto-incrementing BIGINT (internal, sequential)
        - pk_migration: UUID (stable identifier, external APIs)
        - slug: Human-readable (migration_name + timestamp)

        This method is idempotent - safe to call multiple times.
        Handles migration from old table structure.

        Raises:
            MigrationError: If table creation fails
        """
        try:
            with self.connection.cursor() as cursor:
                # Enable UUID extension
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'confiture_migrations'
                    )
                """)
                result = cursor.fetchone()
                table_exists = result[0] if result else False

                if table_exists:
                    # Check if we need to migrate old table structure
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_name = 'confiture_migrations'
                            AND column_name = 'pk_migration'
                        )
                    """)
                    result = cursor.fetchone()
                    has_new_structure = result[0] if result else False

                    if not has_new_structure:
                        # Migrate old table structure to new trinity pattern
                        cursor.execute("""
                            ALTER TABLE confiture_migrations
                            ADD COLUMN pk_migration UUID DEFAULT uuid_generate_v4() UNIQUE,
                            ADD COLUMN slug TEXT,
                            ALTER COLUMN id SET DATA TYPE BIGINT,
                            ALTER COLUMN applied_at SET DATA TYPE TIMESTAMPTZ
                        """)

                        # Generate slugs for existing migrations
                        cursor.execute("""
                            UPDATE confiture_migrations
                            SET slug = name || '_' || to_char(applied_at, 'YYYYMMDD_HH24MISS')
                            WHERE slug IS NULL
                        """)

                        # Make slug NOT NULL and UNIQUE
                        cursor.execute("""
                            ALTER TABLE confiture_migrations
                            ALTER COLUMN slug SET NOT NULL,
                            ADD CONSTRAINT confiture_migrations_slug_unique UNIQUE (slug)
                        """)

                        # Create new indexes
                        cursor.execute("""
                            CREATE INDEX IF NOT EXISTS idx_confiture_migrations_pk_migration
                                ON confiture_migrations(pk_migration)
                        """)
                        cursor.execute("""
                            CREATE INDEX IF NOT EXISTS idx_confiture_migrations_slug
                                ON confiture_migrations(slug)
                        """)

                else:
                    # Create new table with trinity pattern
                    cursor.execute("""
                        CREATE TABLE confiture_migrations (
                            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            pk_migration UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
                            slug TEXT NOT NULL UNIQUE,
                            version VARCHAR(255) NOT NULL UNIQUE,
                            name VARCHAR(255) NOT NULL,
                            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            execution_time_ms INTEGER,
                            checksum VARCHAR(64)
                        )
                    """)

                    # Create indexes
                    cursor.execute("""
                        CREATE INDEX idx_confiture_migrations_pk_migration
                            ON confiture_migrations(pk_migration)
                    """)
                    cursor.execute("""
                        CREATE INDEX idx_confiture_migrations_slug
                            ON confiture_migrations(slug)
                    """)
                    cursor.execute("""
                        CREATE INDEX idx_confiture_migrations_version
                            ON confiture_migrations(version)
                    """)
                    cursor.execute("""
                        CREATE INDEX idx_confiture_migrations_applied_at
                            ON confiture_migrations(applied_at DESC)
                    """)

            self.connection.commit()
        except psycopg.Error as e:
            self.connection.rollback()
            raise MigrationError(f"Failed to initialize migrations table: {e}") from e

    def apply(self, migration: Migration) -> None:
        """Apply a migration and record it in the tracking table.

        This method:
        1. Checks if migration was already applied
        2. Executes migration.up() within a transaction
        3. Records migration metadata (version, name, execution time)
        4. Commits transaction

        Args:
            migration: Migration instance to apply

        Raises:
            MigrationError: If migration fails or was already applied
        """
        # Check if already applied
        if self._is_applied(migration.version):
            raise MigrationError(
                f"Migration {migration.version} ({migration.name}) has already been applied"
            )

        try:
            # Start timing
            start_time = time.perf_counter()

            # Execute migration within transaction
            migration.up()

            # Calculate execution time
            execution_time_ms = int((time.perf_counter() - start_time) * 1000)

            # Record in tracking table with human-readable slug
            # Format: migration-name_YYYYMMDD_HHMMSS
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            slug = f"{migration.name}_{timestamp}"

            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO confiture_migrations
                        (slug, version, name, execution_time_ms)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (slug, migration.version, migration.name, execution_time_ms),
                )

            # Commit transaction
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            raise MigrationError(
                f"Failed to apply migration {migration.version} ({migration.name}): {e}"
            ) from e

    def rollback(self, migration: Migration) -> None:
        """Rollback a migration and remove it from tracking table.

        This method:
        1. Checks if migration was applied
        2. Executes migration.down() within a transaction
        3. Removes migration record from tracking table
        4. Commits transaction

        Args:
            migration: Migration instance to rollback

        Raises:
            MigrationError: If migration fails or was not applied
        """
        # Check if applied
        if not self._is_applied(migration.version):
            raise MigrationError(
                f"Migration {migration.version} ({migration.name}) "
                "has not been applied, cannot rollback"
            )

        try:
            # Execute down() method
            migration.down()

            # Remove from tracking table
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM confiture_migrations
                    WHERE version = %s
                    """,
                    (migration.version,),
                )

            # Commit transaction
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            raise MigrationError(
                f"Failed to rollback migration {migration.version} ({migration.name}): {e}"
            ) from e

    def _is_applied(self, version: str) -> bool:
        """Check if migration version has been applied.

        Args:
            version: Migration version to check

        Returns:
            True if migration has been applied, False otherwise
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM confiture_migrations
                WHERE version = %s
                """,
                (version,),
            )
            result = cursor.fetchone()
            if result is None:
                return False
            count: int = result[0]
            return count > 0

    def get_applied_versions(self) -> list[str]:
        """Get list of all applied migration versions.

        Returns:
            List of migration versions, sorted by applied_at timestamp
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT version
                FROM confiture_migrations
                ORDER BY applied_at ASC
            """)
            return [row[0] for row in cursor.fetchall()]

    def find_migration_files(self, migrations_dir: Path | None = None) -> list[Path]:
        """Find all migration files in the migrations directory.

        Args:
            migrations_dir: Optional custom migrations directory.
                           If None, uses db/migrations/ (default)

        Returns:
            List of migration file paths, sorted by version number

        Example:
            >>> migrator = Migrator(connection=conn)
            >>> files = migrator.find_migration_files()
            >>> # [Path("db/migrations/001_create_users.py"), ...]
        """
        if migrations_dir is None:
            migrations_dir = Path("db") / "migrations"

        if not migrations_dir.exists():
            return []

        # Find all .py files (excluding __pycache__, __init__.py)
        migration_files = sorted(
            [
                f
                for f in migrations_dir.glob("*.py")
                if f.name != "__init__.py" and not f.name.startswith("_")
            ]
        )

        return migration_files

    def find_pending(self, migrations_dir: Path | None = None) -> list[Path]:
        """Find migrations that have not been applied yet.

        Args:
            migrations_dir: Optional custom migrations directory

        Returns:
            List of pending migration file paths

        Example:
            >>> migrator = Migrator(connection=conn)
            >>> pending = migrator.find_pending()
            >>> print(f"Found {len(pending)} pending migrations")
        """
        # Get all migration files
        all_migrations = self.find_migration_files(migrations_dir)

        # Get applied versions
        applied_versions = set(self.get_applied_versions())

        # Filter to pending only
        pending_migrations = [
            migration_file
            for migration_file in all_migrations
            if self._version_from_filename(migration_file.name) not in applied_versions
        ]

        return pending_migrations

    def _version_from_filename(self, filename: str) -> str:
        """Extract version from migration filename.

        Migration files follow the format: {version}_{name}.py
        Example: "001_create_users.py" -> "001"

        Args:
            filename: Migration filename

        Returns:
            Version string

        Example:
            >>> migrator._version_from_filename("042_add_column.py")
            "042"
        """
        # Split on first underscore
        version = filename.split("_")[0]
        return version
