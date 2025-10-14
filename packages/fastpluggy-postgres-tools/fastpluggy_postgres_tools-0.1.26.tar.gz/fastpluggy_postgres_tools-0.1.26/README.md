# Postgres Tools for FastPluggy

![Postgres Tools](https://img.shields.io/badge/FastPluggy-Postgres%20Tools-blue)
![Version](https://img.shields.io/badge/version-0.1.13-blue)

A powerful PostgreSQL database monitoring and management plugin for FastPluggy applications.
This plugin provides a user-friendly interface to monitor and manage various aspects of your PostgreSQL databases.

## Features

### Implemented Features

- **PostgreSQL Sequences Monitoring**:
  - View comprehensive sequence information including name, last value, max value, and remaining capacity
  - Monitor sequence usage with percentage metrics (percent used and percent remaining)
  - Identify sequences that are close to reaching their maximum value
  - Filter sequences by schema (excludes system schemas like pg_catalog and information_schema)
  - Sort sequences by remaining capacity to prioritize attention

- **Database Size & Tablespace Usage**:
  - View total database size and breakdown by schema and tablespace
  - Identify the largest tables in your database
  - See detailed size information for tables and their indexes
  - Filter by schema and include/exclude system schemas
  - Sort by size to identify storage usage patterns

- **Index Usage Statistics**:
  - Track per-index scan counts and rows read
  - Highlight unused indexes below a scan threshold
  - Show index sizes and offer one-click drop operations
  - Filter by schema (excludes system schemas like pg_catalog and information_schema)
  - Sort by scan count to identify unused indexes

- **Table Statistics & Bloat**:
  - Monitor table health by reporting live vs. dead rows
  - Estimate bloat percentage and show disk size
  - Surface last vacuum/analyze times
  - Optional pgstattuple integration for exact bloat measurement
  - Highlight tables with high bloat percentage
  - Filter by schema (excludes system schemas like pg_catalog and information_schema)

- **Query Performance Analysis**:
  - Leverage pg_stat_statements to list top slow queries
  - View queries by total/mean time
  - Option to include 95th percentile statistics
  - Automatic detection of pg_stat_statements extension
  - Installation instructions if extension is not available

- **Connection & Lock Monitoring**:
  - Display all active sessions (state, duration, query)
  - Show current lock contention
  - Flag long-running queries
  - Filter connections by minimum duration and state
  - View detailed information about blocking and waiting queries

- **Vacuum/Autovacuum Status**:
  - Show last manual/autovacuum times per table
  - Display dead-tuple counts
  - Monitor live progress of ongoing autovacuum jobs
  - View autovacuum settings
  - Highlight tables that haven't been vacuumed recently
  - **NEW**: Trigger manual vacuum operations with one-click buttons
  - **NEW**: Support for both regular VACUUM ANALYZE and VACUUM FULL ANALYZE operations
  - **NEW**: Built-in confirmation dialogs for safety

- **Replication & Backups**:
  - Report replication status and lag metrics (write_lag, replay_lag)
  - Track backup history and recency
  - Alert for stale backups or high lag
  - Detect primary/replica status automatically
  - Show replication slots and retained WAL size

- **Custom Hooks & Webhooks**:
  - Define threshold-based alerts on any metric
  - Post notifications to Slack, Discord, Microsoft Teams, PagerDuty, or custom endpoints
  - Test webhook functionality
  - Enable/disable alerts individually
  - Store alert configuration in the database

- **Global Dashboard & Recommendations**:
  - One-page health overview with combined alert list
  - Actionable recommendations for database improvements
  - Extension installation suggestions
  - Database configuration recommendations
  - Key metrics summary

### Planned Features

For detailed specifications of each feature, see the individual files in the `docs/feature/` directory.

## Installation

Install the official plugin package:

```bash
pip install fastpluggy-postgres-tools
```

## Configuration

The plugin uses the same database connection that is configured for your FastPluggy application.
No additional configuration is required if your application is already connected to a PostgreSQL database.

## Usage

### Web Interface

Once installed, access the PostgreSQL tools at `/postgres/` in your FastPluggy application. The interface allows you to:

1. View detailed information about PostgreSQL sequences
2. Monitor sequence usage and remaining capacity
3. Identify sequences that may need attention (approaching maximum value)
4. View database size information and breakdown by schema and tablespace
5. Identify the largest tables in your database
6. Monitor storage usage patterns

### API Access

The plugin also provides API endpoints for programmatic access to all features. See the [API Endpoints Documentation](docs/api-endpoints.md) for details on available endpoints, parameters, and response formats.

## Development

### Requirements

- Python 3.10+
- FastPluggy
- SQLAlchemy 2.0.0+
- PostgreSQL database

### Setup

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Run your FastPluggy application with this plugin enabled

### Building

```bash
python -m build
```


## License

This project is licensed under the MIT License.


## Recommended PostgreSQL extensions

These extensions enable or enhance specific features in this plugin. If you run on a managed PostgreSQL service, you may need to enable them from your provider’s control panel and/or restart the database.

- pg_stat_statements — Required for the Query Performance view
  - Purpose: Collects per-SQL statistics such as total/mean execution time and call counts.
  - How to enable:
    1. Ensure it is preloaded in postgresql.conf: shared_preload_libraries = 'pg_stat_statements' (may require a restart).
    2. Then in each database where you want stats, run:
       CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
  - In-app shortcut: Go to /postgres/queries and use the “Install Extension” button if available.

- pgstattuple — Optional, for more accurate table bloat metrics
  - Purpose: Provides functions to inspect the exact amount of bloat and tuple statistics.
  - How to enable:
       CREATE EXTENSION IF NOT EXISTS pgstattuple;

Notes
- You need sufficient privileges (often a superuser or a role with CREATE privilege) to install extensions.
- If an extension cannot be installed, the corresponding views will still work in a degraded mode (e.g., approximate bloat estimates without pgstattuple, or no query performance data without pg_stat_statements).
