# CLI Reference

Complete reference for all Confiture command-line interface commands.

---

## Global Options

Available for all commands:

```bash
--version       Show version and exit
--help          Show help message and exit
```

---

## `confiture init`

Initialize a new Confiture project with recommended directory structure.

### Usage

```bash
confiture init [PATH]
```

### Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `PATH` | Path | `.` (current directory) | Project directory to initialize |

### What It Creates

```
db/
├── schema/
│   ├── 00_common/
│   │   └── extensions.sql (example)
│   └── 10_tables/
│       └── example.sql (example users table)
├── migrations/
│   └── (empty, ready for migrations)
├── seeds/
│   ├── common/
│   │   └── 00_example.sql
│   ├── development/
│   └── test/
├── environments/
│   └── local.yaml (example configuration)
└── README.md (database documentation)
```

### Examples

```bash
# Initialize in current directory
confiture init

# Initialize in specific directory
confiture init /path/to/project

# Initialize and view structure
confiture init && tree db/
```

### Interactive Behavior

If the `db/` directory already exists, Confiture will:
1. Warn that files may be overwritten
2. Prompt for confirmation: "Continue? [y/N]"
3. Proceed only if you confirm

### Next Steps After Init

1. **Edit schema files** in `db/schema/`
2. **Configure environments** in `db/environments/`
3. **Build schema**: `confiture build`
4. **Generate migrations**: `confiture migrate diff`

---

## `confiture build`

Build complete schema from DDL files (Medium 1: Build from DDL).

This is the **fastest way** to create or recreate a database from scratch (<1 second for 1000 files).

### Usage

```bash
confiture build [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--env` | `-e` | String | `local` | Environment to build (references `db/environments/{env}.yaml`) |
| `--output` | `-o` | Path | `db/generated/schema_{env}.sql` | Custom output file path |
| `--project-dir` | - | Path | `.` | Project directory containing `db/` folder |
| `--show-hash` | - | Flag | `false` | Display schema content hash after build |
| `--schema-only` | - | Flag | `false` | Build schema only, exclude seed data |

### How It Works

1. **Load environment config** from `db/environments/{env}.yaml`
2. **Discover SQL files** in configured `include_dirs` (alphabetical order)
3. **Concatenate files** with metadata headers
4. **Write output** to generated file
5. **Display summary** (file count, size, hash)

### Examples

```bash
# Build local environment (default)
confiture build
# Output: db/generated/schema_local.sql

# Build for production
confiture build --env production
# Output: db/generated/schema_production.sql

# Custom output location
confiture build --output /tmp/schema.sql

# Build with hash for change detection
confiture build --show-hash
# Shows: 🔐 Hash: a3f5c9d2e8b1...

# Build schema only (no seed data)
confiture build --schema-only

# Build from different project directory
confiture build --project-dir /path/to/project
```

### Output Format

Generated SQL file includes:

```sql
-- Schema built by Confiture 🍓
-- Environment: local
-- Generated: 2025-10-12 14:30:00 UTC
-- Files: 42
-- Base directory: db/schema

-- File: 00_common/extensions.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- File: 10_tables/users.sql
CREATE TABLE users (...);

-- ... more files ...
```

### Performance

- **Speed**: <1 second for 1000+ files
- **Deterministic**: Same input = same output (order guaranteed)
- **Cacheable**: Use `--show-hash` to detect changes

### Environment Configuration

The `--env` option loads configuration from `db/environments/{env}.yaml`:

```yaml
name: local
include_dirs:
  - db/schema/00_common
  - db/schema/10_tables
  - db/seeds/common  # Excluded with --schema-only
exclude_dirs: []

database:
  host: localhost
  port: 5432
  database: myapp_local
  user: postgres
  password: postgres
```

### Use Cases

- **Local development**: Fresh database in <1 second
- **CI/CD**: Build test databases quickly
- **Disaster recovery**: Recreate production schema
- **Documentation**: Generate single-file schema snapshot

---

## `confiture migrate`

Migration management commands (Medium 2: Incremental Migrations).

All migration commands are subcommands of `confiture migrate`:

- `confiture migrate status` - View migration status
- `confiture migrate generate` - Create new migration template
- `confiture migrate diff` - Compare schemas and detect changes
- `confiture migrate up` - Apply pending migrations
- `confiture migrate down` - Rollback applied migrations

---

### `confiture migrate status`

Display migration status (pending vs applied).

#### Usage

```bash
confiture migrate status [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--migrations-dir` | - | Path | `db/migrations` | Directory containing migration files |
| `--config` | `-c` | Path | (none) | Config file to check applied status from database |

#### Examples

```bash
# Show all migrations (file-based status only)
confiture migrate status

# Show applied vs pending (requires database connection)
confiture migrate status --config db/environments/local.yaml

# Custom migrations directory
confiture migrate status --migrations-dir custom/migrations
```

#### Output

**Without config (file list only):**

```
                 Migrations
┌─────────┬────────────────────┬─────────┐
│ Version │ Name               │ Status  │
├─────────┼────────────────────┼─────────┤
│ 001     │ create_users       │ unknown │
│ 002     │ add_user_bio       │ unknown │
│ 003     │ add_timestamps     │ unknown │
└─────────┴────────────────────┴─────────┘

📊 Total: 3 migrations
```

**With config (database status):**

```
                 Migrations
┌─────────┬────────────────────┬──────────────┐
│ Version │ Name               │ Status       │
├─────────┼────────────────────┼──────────────┤
│ 001     │ create_users       │ ✅ applied   │
│ 002     │ add_user_bio       │ ✅ applied   │
│ 003     │ add_timestamps     │ ⏳ pending   │
└─────────┴────────────────────┴──────────────┘

📊 Total: 3 migrations (2 applied, 1 pending)
```

#### Use Cases

- Check which migrations need to be applied
- Verify migration history before deployment
- Debug migration issues
- Document current database state

---

### `confiture migrate generate`

Create a new empty migration template.

#### Usage

```bash
confiture migrate generate NAME [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `NAME` | String | ✅ Yes | Migration name in snake_case (e.g., `add_user_bio`) |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--migrations-dir` | - | Path | `db/migrations` | Directory to create migration file in |

#### Examples

```bash
# Generate new migration
confiture migrate generate add_user_bio
# Creates: db/migrations/003_add_user_bio.py

# Custom migrations directory
confiture migrate generate add_timestamps --migrations-dir custom/migrations
```

#### Generated Template

```python
"""Migration: add_user_bio

Version: 003
"""

from confiture.models.migration import Migration


class AddUserBio(Migration):
    """Migration: add_user_bio."""

    version = "003"
    name = "add_user_bio"

    def up(self) -> None:
        """Apply migration."""
        # TODO: Add your SQL statements here
        # Example:
        # self.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        pass

    def down(self) -> None:
        """Rollback migration."""
        # TODO: Add your rollback SQL statements here
        # Example:
        # self.execute("ALTER TABLE users DROP COLUMN bio")
        pass
```

#### Naming Conventions

**Good names** (descriptive, snake_case):
- `add_user_bio`
- `create_posts_table`
- `add_email_index`
- `rename_status_to_state`

**Bad names** (vague, unclear):
- `update` (too vague)
- `fix` (what fix?)
- `AddUserBio` (use snake_case, not PascalCase)

#### Workflow

1. **Generate**: `confiture migrate generate add_user_bio`
2. **Edit**: Add SQL to `up()` and `down()` methods
3. **Test**: `confiture migrate up --config test.yaml`
4. **Verify**: `confiture migrate status`
5. **Rollback** (if needed): `confiture migrate down`

---

### `confiture migrate diff`

Compare two schema files and show differences (schema diff detection).

Optionally generate a migration from the detected changes.

#### Usage

```bash
confiture migrate diff OLD_SCHEMA NEW_SCHEMA [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `OLD_SCHEMA` | Path | ✅ Yes | Path to old schema SQL file |
| `NEW_SCHEMA` | Path | ✅ Yes | Path to new schema SQL file |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--generate` | - | Flag | `false` | Generate migration file from diff |
| `--name` | - | String | (none) | Migration name (required with `--generate`) |
| `--migrations-dir` | - | Path | `db/migrations` | Directory to generate migration in |

#### Examples

```bash
# Show differences only
confiture migrate diff old_schema.sql new_schema.sql

# Generate migration from diff
confiture migrate diff old_schema.sql new_schema.sql --generate --name update_users

# Custom migrations directory
confiture migrate diff old.sql new.sql \
  --generate \
  --name add_posts \
  --migrations-dir custom/migrations
```

#### Output (No Changes)

```
✅ No changes detected. Schemas are identical.
```

#### Output (With Changes)

```
📊 Schema differences detected:

┌──────────────┬─────────────────────────────────────────┐
│ Type         │ Details                                  │
├──────────────┼─────────────────────────────────────────┤
│ table_added  │ Table 'posts' added                     │
│ column_added │ Column 'users.bio' added (type: TEXT)   │
│ index_added  │ Index 'idx_users_email' added on users │
└──────────────┴─────────────────────────────────────────┘

📈 Total changes: 3

✅ Migration generated: 003_update_users.py
```

#### Detected Change Types

The differ detects:

- **Tables**: `table_added`, `table_removed`, `table_renamed`
- **Columns**: `column_added`, `column_removed`, `column_type_changed`, `column_renamed`
- **Indexes**: `index_added`, `index_removed`
- **Constraints**: `constraint_added`, `constraint_removed`
- **Functions**: `function_added`, `function_removed`, `function_changed`

#### Workflow with Build

```bash
# 1. Build current schema
confiture build --env local --output old.sql

# 2. Edit schema files in db/schema/
vim db/schema/10_tables/users.sql  # Add bio column

# 3. Build new schema
confiture build --env local --output new.sql

# 4. Generate migration from diff
confiture migrate diff old.sql new.sql --generate --name add_user_bio

# 5. Apply migration
confiture migrate up
```

#### Use Cases

- **Auto-generate migrations** from schema changes
- **Review changes** before committing
- **Detect drift** between environments
- **Document schema evolution**

---

### `confiture migrate up`

Apply pending migrations (forward migrations).

#### Usage

```bash
confiture migrate up [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--migrations-dir` | - | Path | `db/migrations` | Directory containing migration files |
| `--config` | `-c` | Path | `db/environments/local.yaml` | Configuration file with database credentials |
| `--target` | `-t` | String | (none) | Target migration version (applies all if not specified) |

#### Examples

```bash
# Apply all pending migrations
confiture migrate up

# Apply up to specific version
confiture migrate up --target 003

# Use custom config
confiture migrate up --config db/environments/production.yaml

# Custom migrations directory
confiture migrate up --migrations-dir custom/migrations
```

#### Output (Success)

```
📦 Found 2 pending migration(s)

⚡ Applying 002_add_user_bio... ✅
⚡ Applying 003_add_timestamps... ✅

✅ Successfully applied 2 migration(s)!
```

#### Output (No Pending)

```
✅ No pending migrations. Database is up to date.
```

#### Output (Error)

```
📦 Found 2 pending migration(s)

⚡ Applying 002_add_user_bio... ✅
⚡ Applying 003_add_timestamps... ❌ Error: column "bio" already exists
```

#### Transaction Behavior

- Each migration runs in a **separate transaction**
- If a migration fails, **previous migrations remain applied**
- **Rollback** failed migration with `confiture migrate down`

#### Target Version Behavior

```bash
# Migrations: 001, 002, 003, 004, 005
# Applied: 001, 002
# Pending: 003, 004, 005

# Apply all pending
confiture migrate up
# Applies: 003, 004, 005

# Apply up to 004 only
confiture migrate up --target 004
# Applies: 003, 004
# Skips: 005
```

#### Use Cases

- **Local development**: Apply schema changes
- **CI/CD**: Automated database updates
- **Production deployment**: Apply migrations safely
- **Environment sync**: Update staging to match production

---

### `confiture migrate down`

Rollback applied migrations (reverse migrations).

#### Usage

```bash
confiture migrate down [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--migrations-dir` | - | Path | `db/migrations` | Directory containing migration files |
| `--config` | `-c` | Path | `db/environments/local.yaml` | Configuration file with database credentials |
| `--steps` | `-n` | Integer | `1` | Number of migrations to rollback |

#### Examples

```bash
# Rollback last migration
confiture migrate down

# Rollback last 3 migrations
confiture migrate down --steps 3

# Use custom config
confiture migrate down --config db/environments/staging.yaml

# Custom migrations directory
confiture migrate down --migrations-dir custom/migrations
```

#### Output (Success)

```
📦 Rolling back 2 migration(s)

⚡ Rolling back 003_add_timestamps... ✅
⚡ Rolling back 002_add_user_bio... ✅

✅ Successfully rolled back 2 migration(s)!
```

#### Output (No Applied Migrations)

```
⚠️  No applied migrations to rollback.
```

#### Rollback Order

Migrations are rolled back in **reverse order** (newest first):

```bash
# Applied migrations: 001, 002, 003, 004, 005

# Rollback 1 step
confiture migrate down --steps 1
# Rolls back: 005
# Remaining: 001, 002, 003, 004

# Rollback 3 steps
confiture migrate down --steps 3
# Rolls back: 005, 004, 003 (in that order)
# Remaining: 001, 002
```

#### Safety Considerations

⚠️ **Warning**: Rollbacks can be **destructive**:

- **Data loss**: `DROP TABLE` deletes all data
- **Production risk**: Always test rollbacks in staging first
- **Irreversible**: Some changes (like data type conversions) may lose information

**Best practices**:
1. **Test rollbacks** in development/staging before production
2. **Backup data** before rolling back in production
3. **Review `down()` methods** for destructive operations
4. **Use transactions** (automatic in Confiture)

#### Use Cases

- **Undo mistakes**: Revert failed migrations
- **Development iteration**: Test migration changes
- **Production hotfix**: Emergency rollback of problematic changes
- **Environment reset**: Return to known-good state

---

## Error Handling

### Common Errors and Solutions

#### File Not Found

```
❌ File not found: db/schema/
💡 Tip: Run 'confiture init' to create project structure
```

**Solution**: Run `confiture init` to create the project structure.

#### Configuration Error

```
❌ Error building schema: Invalid environment configuration
```

**Solution**: Check `db/environments/{env}.yaml` for syntax errors.

#### Database Connection Failed

```
❌ Error: could not connect to server: Connection refused
```

**Solutions**:
- Verify PostgreSQL is running: `pg_isready`
- Check connection details in `db/environments/{env}.yaml`
- Test connection: `psql -h localhost -U postgres`

#### Migration Already Applied

```
❌ Error: migration 003 is already applied
```

**Solution**: Check status with `confiture migrate status --config {env}.yaml`

#### Migration Failed

```
❌ Error: column "bio" already exists
```

**Solutions**:
1. Review migration SQL for errors
2. Rollback: `confiture migrate down`
3. Fix migration file
4. Reapply: `confiture migrate up`

---

## Exit Codes

Confiture uses standard exit codes:

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success |
| `1` | Error (file not found, database error, etc.) |

Use in scripts:

```bash
# Exit on error
confiture build --env production || exit 1

# Conditional execution
if confiture migrate up --config prod.yaml; then
  echo "Migrations applied successfully"
else
  echo "Migration failed!"
  exit 1
fi
```

---

## Shell Completion

Confiture supports shell completion for bash, zsh, and fish.

### Setup

```bash
# Bash
eval "$(_CONFITURE_COMPLETE=bash_source confiture)"

# Zsh
eval "$(_CONFITURE_COMPLETE=zsh_source confiture)"

# Fish
_CONFITURE_COMPLETE=fish_source confiture | source
```

### Add to Shell RC

```bash
# Add to ~/.bashrc
echo 'eval "$(_CONFITURE_COMPLETE=bash_source confiture)"' >> ~/.bashrc

# Add to ~/.zshrc
echo 'eval "$(_CONFITURE_COMPLETE=zsh_source confiture)"' >> ~/.zshrc

# Add to ~/.config/fish/config.fish
echo '_CONFITURE_COMPLETE=fish_source confiture | source' >> ~/.config/fish/config.fish
```

---

## Environment Variables

Confiture supports environment variables for common options:

| Variable | Description | Example |
|----------|-------------|---------|
| `CONFITURE_ENV` | Default environment | `export CONFITURE_ENV=production` |
| `CONFITURE_PROJECT_DIR` | Default project directory | `export CONFITURE_PROJECT_DIR=/app` |
| `DATABASE_URL` | PostgreSQL connection URL | `export DATABASE_URL=postgresql://...` |

**Note**: Command-line options always override environment variables.

---

## Examples

### Development Workflow

```bash
# 1. Initialize project
confiture init

# 2. Edit schema files
vim db/schema/10_tables/users.sql

# 3. Build schema
confiture build

# 4. Apply to local database
psql -f db/generated/schema_local.sql

# 5. Generate migration
confiture migrate diff old.sql new.sql --generate --name add_users

# 6. Apply migration
confiture migrate up
```

### CI/CD Pipeline

```bash
#!/bin/bash
set -e

# Build schema
confiture build --env test --schema-only

# Run tests
pytest tests/

# Apply migrations
confiture migrate up --config test.yaml

# Verify database
psql -c "SELECT version FROM confiture_version"
```

### Production Deployment

```bash
#!/bin/bash
set -e

# Check pending migrations
confiture migrate status --config production.yaml

# Backup database
pg_dump -Fc myapp_production > backup.dump

# Apply migrations
confiture migrate up --config production.yaml

# Verify
confiture migrate status --config production.yaml
```

---

## Further Reading

- **[Getting Started Guide](../guides/getting-started.md)** - Step-by-step tutorial
- **[Migration Strategies](../guides/migration-strategies.md)** - Choosing the right strategy
- **[Configuration Reference](./configuration.md)** - Environment configuration
- **[API Reference](./api.md)** - Python API documentation

---

**Last Updated**: October 12, 2025
**Version**: 1.0
