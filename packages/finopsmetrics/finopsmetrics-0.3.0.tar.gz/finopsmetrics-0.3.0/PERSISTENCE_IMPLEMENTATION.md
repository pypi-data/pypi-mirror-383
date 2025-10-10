# Persistence Layer Implementation

## Overview

Added comprehensive database persistence support for finopsmetrics telemetry data, enabling historical analysis and long-term data retention.

## What Was Added

### 1. **Persistence Abstraction Layer** (`src/finopsmetrics/observability/persistence.py`)

**Pluggable Storage Backends:**
- ✅ **InMemoryBackend** - Fast, no persistence (default)
- ✅ **SQLiteBackend** - File-based, single-server deployments
- ✅ **PostgreSQLBackend** - Production-grade relational database
- ✅ **TimescaleDBBackend** - Optimized for time-series data with compression

**Key Features:**
- Automatic schema initialization
- Batch insertion for performance
- Query optimization for time-series data
- Data retention policies
- Connection pooling (PostgreSQL)
- Automatic compression (TimescaleDB)

### 2. **Updated Core Components**

**ObservabilityHub** (`src/finopsmetrics/observability/observability_hub.py`):
- Added `persistence_config` parameter
- Dual-layer storage (memory + database)
- New method: `query_historical_metrics()` for historical analysis
- New method: `cleanup_old_data()` for retention management
- New method: `close()` for proper connection cleanup

**CostObservatory** (`src/finopsmetrics/observability/cost_observatory.py`):
- Added `persistence_config` parameter
- Automatic persistence of cost entries
- New method: `query_historical_costs()` for cost analysis
- New method: `cleanup_old_data()` for retention management
- New method: `close()` for proper connection cleanup

### 3. **Database CLI Tools** (`src/finopsmetrics/cli/database.py`)

Command-line utilities for database management:
```bash
finopsmetrics database init           # Initialize database schema
finopsmetrics database test-connection # Test database connection
finopsmetrics database stats          # Show database statistics
finopsmetrics database query          # Query recent data
finopsmetrics database cleanup        # Remove old data
finopsmetrics database examples       # Show usage examples
```

### 4. **Documentation**

- **User Guide:** `docs/PERSISTENCE.md` - Complete guide for all storage backends
- **Examples:** `examples/persistence_config_examples.py` - 10 detailed examples
- **This File:** Implementation summary and quick start

### 5. **Tests** (`tests/test_persistence.py`)

Comprehensive test suite covering:
- In-memory backend
- SQLite backend
- Batch insertion
- Query filtering
- Data persistence across restarts
- Integration with ObservabilityHub
- Integration with CostObservatory
- Data cleanup/retention
- PostgreSQL backend (optional, requires server)

## Quick Start

### Default (In-Memory Only)

```python
from finopsmetrics.observability import ObservabilityHub, CostObservatory

# No configuration = in-memory only (data lost on restart)
hub = ObservabilityHub()
cost_obs = CostObservatory()
```

### SQLite (File-Based Persistence)

```python
from finopsmetrics.observability import ObservabilityHub, CostObservatory
from finopsmetrics.observability.persistence import PersistenceConfig, StorageBackend

config = PersistenceConfig(
    backend=StorageBackend.SQLITE,
    connection_string="sqlite:///finopsmetrics_telemetry.db",
    retention_days=90
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)

# Data persists across restarts!
```

### PostgreSQL (Production)

```python
config = PersistenceConfig(
    backend=StorageBackend.POSTGRESQL,
    connection_string="postgresql://user:password@localhost:5432/finopsmetrics",
    retention_days=365
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

### TimescaleDB (Time-Series Optimized)

```python
config = PersistenceConfig(
    backend=StorageBackend.TIMESCALEDB,
    connection_string="postgresql://user:password@localhost:5432/finopsmetrics",
    retention_days=730,  # 2 years
    enable_compression=True  # Automatic compression
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

## Querying Historical Data

### System Metrics

```python
import time

# Query last 7 days
seven_days_ago = time.time() - (7 * 24 * 3600)
metrics = hub.query_historical_metrics(
    start_time=seven_days_ago,
    cluster_id="production-cluster",
    limit=10000
)

print(f"Retrieved {len(metrics)} metrics")
```

### Cost Data

```python
# Query last 30 days of compute costs
thirty_days_ago = time.time() - (30 * 24 * 3600)
costs = cost_obs.query_historical_costs(
    start_time=thirty_days_ago,
    category="compute",
    limit=10000
)

# Calculate total
total_cost = sum(entry['amount'] for entry in costs)
print(f"Total compute cost (30 days): ${total_cost:.2f}")
```

## Database Setup

### SQLite

No setup required! Just specify the database file path:

```bash
# Initialize database
finopsmetrics database init --backend sqlite --connection-string "sqlite:///finopsmetrics.db"
```

### PostgreSQL

```bash
# 1. Install PostgreSQL
sudo apt-get install postgresql

# 2. Create database
sudo -u postgres createdb finopsmetrics

# 3. Create user and grant privileges
sudo -u postgres psql
postgres=# CREATE USER finopsmetrics_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE finopsmetrics TO finopsmetrics_user;

# 4. Initialize schema
finopsmetrics database init --backend postgresql \
  --connection-string "postgresql://finopsmetrics_user:your_password@localhost:5432/finopsmetrics"
```

### TimescaleDB

```bash
# 1. Install TimescaleDB
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update
sudo apt-get install timescaledb-postgresql-14

# 2. Initialize
sudo timescaledb-tune

# 3. Enable extension
sudo -u postgres psql -d finopsmetrics
finopsmetrics=# CREATE EXTENSION IF NOT EXISTS timescaledb;

# 4. Initialize schema (automatic hypertables + compression)
finopsmetrics database init --backend timescaledb \
  --connection-string "postgresql://user:pass@localhost:5432/finopsmetrics"
```

## Dependencies

**Core (included):**
- No additional dependencies for in-memory or SQLite

**PostgreSQL/TimescaleDB:**
```bash
pip install psycopg2-binary
# or
pip install finopsmetrics[postgres]
# or
pip install finopsmetrics[all]
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | StorageBackend | IN_MEMORY | Storage backend |
| `connection_string` | str | Auto | Database connection |
| `retention_days` | int | 90 | Data retention period |
| `batch_size` | int | 100 | Batch size for writes |
| `batch_interval_seconds` | float | 60.0 | Max flush interval |
| `enable_compression` | bool | False | Enable compression (TimescaleDB) |
| `max_memory_entries` | int | 10000 | In-memory buffer size |

## Performance Characteristics

### Storage Backend Comparison

| Backend | Write Speed | Query Speed | Concurrency | Scalability | Storage Efficiency |
|---------|-------------|-------------|-------------|-------------|--------------------|
| In-Memory | ⚡ Fastest | ⚡ Fastest | ⚠️ Limited | ❌ Single process | N/A (RAM) |
| SQLite | ✅ Fast | ✅ Fast | ⚠️ Single writer | ⚠️ Single server | ✅ Good |
| PostgreSQL | ✅ Fast | ✅ Fast | ✅ Excellent | ✅ Clustered | ✅ Good |
| TimescaleDB | ✅ Fast | ⚡ Fastest* | ✅ Excellent | ✅ Clustered | ⚡ Excellent** |

\* For time-series queries
\*\* With compression enabled (90%+ reduction)

### Recommended Use Cases

- **In-Memory**: Development, testing, ephemeral workloads
- **SQLite**: Single-server, small teams, < 1M metrics/day
- **PostgreSQL**: Multi-server, production, > 1M metrics/day
- **TimescaleDB**: High volume, long retention, analytics

## Migration Between Backends

To switch backends, update your configuration and restart. The new backend will start collecting new data.

For historical data migration, use the query methods:

```python
# Export from old backend
old_metrics = old_hub.query_historical_metrics(limit=1000000)
old_costs = old_cost_obs.query_historical_costs(limit=1000000)

# Import to new backend
for metric in old_metrics:
    new_hub.collect_system_metrics(SystemMetrics(**metric))

for cost in old_costs:
    new_cost_obs.add_cost_entry(CostEntry(**cost))
```

## Testing

Run the persistence tests:

```bash
# All tests
pytest tests/test_persistence.py -v

# Specific backend
pytest tests/test_persistence.py::TestSQLiteBackend -v

# With PostgreSQL (requires server)
TEST_POSTGRESQL=1 POSTGRESQL_URL=postgresql://localhost/finopsmetrics_test \
  pytest tests/test_persistence.py::TestPostgreSQLBackend -v
```

## Files Created/Modified

### New Files
- `src/finopsmetrics/observability/persistence.py` - Persistence layer
- `src/finopsmetrics/cli/database.py` - CLI tools
- `examples/persistence_config_examples.py` - Usage examples
- `docs/PERSISTENCE.md` - Complete documentation
- `tests/test_persistence.py` - Comprehensive tests
- `PERSISTENCE_IMPLEMENTATION.md` - This file

### Modified Files
- `src/finopsmetrics/observability/observability_hub.py` - Added persistence support
- `src/finopsmetrics/observability/cost_observatory.py` - Added persistence support

## Backward Compatibility

✅ **100% Backward Compatible**

Existing code continues to work without changes:
- Default behavior: in-memory only (same as before)
- Persistence is opt-in via configuration
- All existing APIs unchanged
- No breaking changes

## Next Steps

1. **Choose your backend** based on your deployment needs
2. **Configure persistence** in your application
3. **Initialize the database** using CLI or automatically
4. **Start collecting data** - it persists automatically
5. **Query historical data** for analysis and reporting

## Support

For issues or questions:
- See `docs/PERSISTENCE.md` for detailed documentation
- Check `examples/persistence_config_examples.py` for code examples
- Run `finopsmetrics database examples` for CLI help
- File issues at https://github.com/finopsmetrics/finopsmetrics/issues
