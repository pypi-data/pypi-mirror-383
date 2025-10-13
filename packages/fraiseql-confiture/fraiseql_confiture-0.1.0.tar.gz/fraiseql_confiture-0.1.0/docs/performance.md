# Performance Guide

This guide documents Confiture's performance characteristics, benchmarks, and optimization strategies for production data synchronization.

## 📊 Performance Summary

Confiture delivers excellent performance for PostgreSQL data synchronization:

| Operation | Throughput | Notes |
|-----------|------------|-------|
| **COPY (no anonymization)** | **~70,000 rows/sec** | PostgreSQL native COPY command |
| **Anonymization (3 columns)** | **~6,500 rows/sec** | Batch processing with PII anonymization |
| **Multi-table sync** | **~10,600 rows/sec** | Mixed workload (fast + slow paths) |
| **Connection overhead** | **~29ms** | Negligible for long-running syncs |
| **Checkpoint overhead** | **~10%** | Resume functionality cost |

## 🎯 Benchmark Methodology

All benchmarks were conducted using:
- **PostgreSQL**: Version 16.3
- **Hardware**: Modern Linux system
- **Test data**: Realistic table structures with various column types
- **Measurement**: Python `time.perf_counter()` for high precision

### Test Scenarios

#### 1. Fast Path (COPY)
- 20,000 row table (products)
- No PII, no anonymization
- Direct PostgreSQL COPY command
- **Result**: 70,396 rows/sec

#### 2. Slow Path (Anonymization)
- 10,000 row table (users)
- 3 PII columns (email, phone, name)
- Fetch → Anonymize → Batch Insert
- **Result**: 6,515 rows/sec

#### 3. Mixed Workload
- 2 tables (30,000 total rows)
- 1 with anonymization, 1 without
- **Result**: 10,645 rows/sec overall

## 🚀 Optimization History

### Milestone 3.6: Performance Optimization (October 2025)

#### Batch Size Optimization

**Finding**: Default batch size of 10,000 rows was suboptimal.

**Experiment**: Tested batch sizes from 1,000 to 20,000 rows.

**Results**:
```
Batch Size | Throughput  | Duration
-----------|-------------|----------
1,000      | 4,133 r/s   | 2.420s
5,000      | 7,738 r/s   | 1.292s  ⭐ OPTIMAL
10,000     | 6,391 r/s   | 1.565s
20,000     | 7,042 r/s   | 1.420s
```

**Decision**: Changed default batch size to **5,000 rows** (~19% improvement).

**Reasoning**:
- 5K batch size balances memory usage vs. insert overhead
- Larger batches (>5K) see diminishing returns
- PostgreSQL `executemany` efficiency peaks around 5K rows

#### Connection Pooling Analysis

**Finding**: Connection overhead is minimal (~29ms per connection).

**Analysis**:
- Connection creation: ~29ms average
- Typical sync duration: seconds to minutes
- Connection cost: <1% of total sync time

**Decision**: No connection pooling implemented for now.

**Reasoning**:
- Single connection per sync is sufficient
- Connection pooling would add complexity
- May revisit for high-frequency sync scenarios

#### Memory Usage

**Current Behavior**: Batch-based processing keeps memory bounded.

**Measurements**:
- 1,000 row batch: ~0.2 MB peak memory
- 10,000 row batch: ~1.9 MB peak memory
- 5,000 row batch: ~1.0 MB peak memory (optimal)

**Status**: Memory usage is excellent; no streaming needed for typical tables.

## 📈 Performance Characteristics

### Scaling Behavior

#### COPY Performance (No Anonymization)

**Scales linearly with row count:**
- 10K rows: ~0.14s
- 20K rows: ~0.28s
- 100K rows: ~1.4s (estimated)
- 1M rows: ~14s (estimated)

**Bottlenecks**:
- Network bandwidth (local: ~300 MB/s)
- Disk I/O (target database writes)
- **NOT CPU-bound** (PostgreSQL COPY is highly optimized)

#### Anonymization Performance

**Scales with row count × columns anonymized:**
- 10K rows × 3 cols: ~1.5s
- 10K rows × 5 cols: ~2.5s (estimated)
- 100K rows × 3 cols: ~15s (estimated)

**Bottlenecks**:
- **CPU-bound** (Python anonymization logic)
- Hash computation (SHA256)
- Batch insert overhead

### Throughput by Table Size

```
Table Size | COPY Path   | Anonymization Path (3 cols)
-----------|-------------|------------------------------
1K rows    | ~1ms        | ~150ms
10K rows   | ~140ms      | ~1.5s
100K rows  | ~1.4s       | ~15s
1M rows    | ~14s        | ~2.5 minutes
10M rows   | ~2.3 minutes| ~25 minutes
```

## 🎯 Best Practices

### 1. Use COPY Path When Possible

**Avoid anonymization for non-PII tables:**

```python
# ✅ Good: No anonymization for public data
config = SyncConfig(
    tables=TableSelection(include=["products", "orders"]),
    # No anonymization rules
)

# ❌ Unnecessary: Anonymizing non-sensitive data
config = SyncConfig(
    tables=TableSelection(include=["products"]),
    anonymization={
        "products": [AnonymizationRule(column="sku", strategy="hash")]
    }  # SKU is not PII!
)
```

### 2. Minimize Anonymized Columns

**Only anonymize actual PII:**

```python
# ✅ Good: Only PII columns
anonymization={
    "users": [
        AnonymizationRule(column="email", strategy="email"),
        AnonymizationRule(column="ssn", strategy="redact"),
    ]
}

# ❌ Bad: Anonymizing everything
anonymization={
    "users": [
        AnonymizationRule(column="email", strategy="email"),
        AnonymizationRule(column="name", strategy="name"),
        AnonymizationRule(column="bio", strategy="redact"),
        AnonymizationRule(column="preferences", strategy="redact"),
        # Too many columns!
    ]
}
```

### 3. Use Optimal Batch Size

**Default of 5,000 is optimized, but can be tuned:**

```python
# ✅ Default is good for most cases
config = SyncConfig(
    tables=TableSelection(include=["users"]),
    # batch_size=5000 (default, optimized)
)

# ⚙️ Tune for specific scenarios
config = SyncConfig(
    tables=TableSelection(include=["very_wide_table"]),
    batch_size=2000  # Reduce for wide tables (many columns)
)

config = SyncConfig(
    tables=TableSelection(include=["narrow_table"]),
    batch_size=10000  # Increase for narrow tables
)
```

### 4. Sync During Off-Peak Hours

**Production sync is I/O intensive:**

- Schedule syncs during low-traffic periods
- Monitor source database load
- Use read replicas if available

### 5. Enable Progress Reporting for Large Syncs

**Visibility is important for long-running operations:**

```python
config = SyncConfig(
    tables=TableSelection(include=["huge_table"]),
    show_progress=True,  # ✅ Enable for large syncs
    checkpoint_file=Path("/tmp/sync_checkpoint.json"),  # ✅ Enable resume
)
```

### 6. Monitor Performance Consistency

**Performance can vary based on:**
- Database load
- Network conditions
- System resources

**Our benchmarks show 41% variance** - this is expected in real-world conditions.

## 🔬 Advanced Optimization

### Future Improvements (Not Yet Implemented)

#### 1. Rust-based Anonymization

**Potential**: 10-50x faster anonymization

**Status**: Planned for Phase 2

**Expected Impact**:
- Current: 6,500 rows/sec
- With Rust: 65,000-325,000 rows/sec

#### 2. Parallel Table Sync

**Potential**: Near-linear scaling with CPU cores

**Status**: Under consideration

**Expected Impact**:
- Current: Sequential table processing
- With parallelism: 4x speedup on 4-core system

#### 3. Connection Pooling

**Potential**: Marginal improvement (<5%)

**Status**: Deferred (minimal benefit currently)

**When to implement**:
- High-frequency sync scenarios (multiple syncs per minute)
- Micro-service architectures with many sync workers

## 📊 Comparison with Competitors

### pg_dump/pg_restore

**Confiture vs pg_dump for data sync:**

| Feature | Confiture | pg_dump/pg_restore |
|---------|-----------|-------------------|
| **Throughput** | ~70K rows/sec | ~100K rows/sec |
| **PII Anonymization** | ✅ Built-in | ❌ Manual scripting |
| **Selective Sync** | ✅ Table selection | ⚠️ Schema-level only |
| **Progress Reporting** | ✅ Rich UI | ⚠️ Basic |
| **Resume Support** | ✅ Checkpoint-based | ❌ All-or-nothing |
| **Schema Validation** | ✅ Automatic | ⚠️ Manual |

**Verdict**: Confiture is slightly slower but offers far superior developer experience and safety.

### Alembic (for migrations)

**Note**: Alembic is a migration tool, not a data sync tool.

| Feature | Confiture | Alembic |
|---------|-----------|---------|
| **Data Sync** | ✅ Primary feature | ❌ Not designed for this |
| **Anonymization** | ✅ Built-in | ❌ Not available |
| **Migration Speed** | ~70K rows/sec data | N/A (schema only) |
| **Use Case** | Data sync | Schema migrations |

**Verdict**: Different tools for different jobs. Use Confiture for data sync, Alembic for schema migrations.

### Other Python Tools

Most Python database tools (Django ORM, SQLAlchemy) are **10-100x slower** for bulk data operations.

**Why Confiture is faster**:
1. Uses PostgreSQL COPY (native bulk loading)
2. Minimizes Python overhead
3. Batch processing optimized via benchmarks
4. Direct psycopg3 usage (no ORM overhead)

## 🛠️ Troubleshooting Performance Issues

### Slow COPY Performance (<10K rows/sec)

**Possible causes**:
1. Network latency (remote database)
2. Slow disk I/O (target database)
3. Concurrent load on database

**Solutions**:
```bash
# Check network latency
ping your-database-host

# Check database performance
psql -c "EXPLAIN ANALYZE SELECT * FROM large_table LIMIT 1000"

# Monitor database load
psql -c "SELECT * FROM pg_stat_activity"
```

### Slow Anonymization (<2K rows/sec)

**Possible causes**:
1. Too many columns being anonymized
2. Complex anonymization strategies
3. CPU throttling

**Solutions**:
```python
# Profile anonymization
import cProfile
cProfile.run('syncer.sync_table("users", rules)')

# Reduce anonymized columns
# Only anonymize actual PII

# Check CPU usage
htop  # Should see Python at ~100% CPU during anonymization
```

### High Memory Usage

**Possible causes**:
1. Batch size too large
2. Very wide tables (many columns)

**Solutions**:
```python
# Reduce batch size
config = SyncConfig(
    tables=TableSelection(include=["wide_table"]),
    batch_size=1000  # Reduced from default 5000
)

# Monitor memory
import psutil
print(f"Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB")
```

## 📚 Additional Resources

- [Production Sync Guide](./production-sync.md) - Complete guide to syncing production data
- [Anonymization Strategies](./anonymization.md) - PII handling best practices
- [Benchmarking Guide](../tests/performance/README.md) - How to run your own benchmarks

---

**Last Updated**: October 2025
**Benchmark Version**: Confiture 0.2.0-alpha
**Test Environment**: PostgreSQL 16.3, Python 3.11, Linux x86_64
