# 🎉 finopsmetrics v0.2.1 Released: Database Persistence for Historical Analytics!

We're excited to announce **finopsmetrics v0.2.1** with a major new feature: **configurable database persistence** for telemetry data!

## 🔥 What's New

Previously, finopsmetrics stored all telemetry data **in-memory only**, which meant:
- ❌ Data lost on restart
- ❌ Limited to RAM capacity
- ❌ No historical analysis beyond buffer limits

Now with v0.2.1, you can **persist telemetry data to databases** for long-term storage and historical analysis!

## 📊 Storage Backend Options

Choose the backend that fits your needs:

### 1️⃣ **In-Memory** (Default)
- ⚡ Fastest performance
- Perfect for development & testing
- No persistence (same as before)

### 2️⃣ **SQLite**
- 📁 Simple file-based storage
- Ideal for single-server deployments
- No database server required

### 3️⃣ **PostgreSQL**
- 🏢 Production-grade reliability
- Multi-server support
- Enterprise-ready

### 4️⃣ **TimescaleDB** (Recommended for Production)
- ⚡ Optimized for time-series data
- 🗜️ Automatic compression (90%+ storage savings)
- 📈 Best query performance for analytics

## 🚀 Quick Start

### SQLite (Easiest)
```python
from finopsmetrics.observability import ObservabilityHub, CostObservatory
from finopsmetrics.observability.persistence import PersistenceConfig, StorageBackend

config = PersistenceConfig(
    backend=StorageBackend.SQLITE,
    connection_string="sqlite:///finopsmetrics.db",
    retention_days=90  # Keep 90 days of history
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)

# That's it! Your data now persists across restarts
```

### PostgreSQL/TimescaleDB (Production)
```python
config = PersistenceConfig(
    backend=StorageBackend.TIMESCALEDB,
    connection_string="postgresql://user:pass@localhost:5432/finopsmetrics",
    retention_days=365,  # 1 year of history
    enable_compression=True  # Save 90%+ storage
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

## 🔍 Query Historical Data

Now you can analyze historical trends:

```python
import time

# Query last 30 days of metrics
thirty_days_ago = time.time() - (30 * 24 * 3600)
metrics = hub.query_historical_metrics(
    start_time=thirty_days_ago,
    cluster_id="production",
    limit=10000
)

# Analyze cost trends
costs = cost_obs.query_historical_costs(
    start_time=thirty_days_ago,
    category="compute"
)

# Calculate total cost
total = sum(entry['amount'] for entry in costs)
print(f"30-day compute cost: ${total:.2f}")
```

## 🛠️ Database CLI Tools

New command-line utilities included:

```bash
# Initialize database
finopsmetrics database init --backend sqlite

# View statistics
finopsmetrics database stats --backend sqlite \
  --connection-string "sqlite:///finopsmetrics.db"

# Query recent data
finopsmetrics database query --backend sqlite \
  --connection-string "sqlite:///finopsmetrics.db" --days 7

# Cleanup old data
finopsmetrics database cleanup --retention-days 90
```

## 📈 Use Cases

### 1. Historical Cost Analysis
Track cost trends over months to identify patterns and optimize spending.

### 2. Capacity Planning
Analyze historical resource usage to plan future capacity needs.

### 3. Anomaly Detection
Compare current metrics against historical baselines to detect anomalies.

### 4. Compliance & Auditing
Maintain long-term records for compliance and financial auditing.

### 5. Training Run Comparison
Compare AI training runs over time to optimize hyperparameters.

## 📊 Performance Comparison

| Backend | Write Speed | Query Speed | Concurrency | Storage Efficiency |
|---------|-------------|-------------|-------------|-------------------|
| In-Memory | ⚡ Fastest | ⚡ Fastest | Limited | N/A (RAM) |
| SQLite | Fast | Fast | Single writer | Good |
| PostgreSQL | Fast | Fast | Excellent | Good |
| TimescaleDB | Fast | ⚡ Fastest* | Excellent | ⚡ Excellent** |

\* For time-series queries
\*\* 90%+ compression with automatic tiering

## ✅ Key Features

- ✨ **Pluggable Architecture** - Switch backends easily
- 🔄 **Automatic Schema Management** - No manual setup
- 📦 **Batch Processing** - High-performance bulk inserts
- 🗓️ **Data Retention Policies** - Automatic cleanup
- 🔍 **Rich Query API** - Filter by time, cluster, resource
- 🧪 **Fully Tested** - Comprehensive test suite
- 📚 **Well Documented** - Complete guides and examples

## 📦 Installation

```bash
# Basic installation
pip install --upgrade finopsmetrics

# With PostgreSQL support
pip install finopsmetrics[postgres]

# With all features
pip install finopsmetrics[all]
```

## 🎓 Learn More

- **📖 Complete Guide:** [`docs/PERSISTENCE.md`](docs/PERSISTENCE.md)
- **💡 Examples:** [`examples/persistence_config_examples.py`](examples/persistence_config_examples.py)
- **🏗️ Implementation:** [`PERSISTENCE_IMPLEMENTATION.md`](PERSISTENCE_IMPLEMENTATION.md)
- **📦 PyPI:** https://pypi.org/project/finopsmetrics/0.2.1/

## 🔄 Migration

**100% Backward Compatible!** No breaking changes.

Existing code works as-is. To enable persistence, just add the config:

```python
# Before (still works)
hub = ObservabilityHub()

# After (with persistence)
config = PersistenceConfig(backend=StorageBackend.SQLITE)
hub = ObservabilityHub(persistence_config=config)
```

## 🎯 Try It Now!

1. Upgrade: `pip install --upgrade finopsmetrics`
2. Check examples: `examples/persistence_config_examples.py`
3. Read docs: `docs/PERSISTENCE.md`
4. Share feedback here! 👇

## 💬 Discussion

What are you planning to use the persistence layer for?
- Historical cost analysis?
- Capacity planning?
- Compliance auditing?
- Something else?

Let us know in the comments! We'd love to hear your use cases and feedback.

---

⭐ **Star the repo** if you find this useful!
🐛 **Found a bug?** Open an issue!
💡 **Have ideas?** Start a discussion!

**Happy FinOps-ing!** 🚀
