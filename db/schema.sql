-- PyStorageOps metadata database schema (SQLite)

CREATE TABLE IF NOT EXISTS volumes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT UNIQUE NOT NULL,
    size_blocks INTEGER NOT NULL,
    block_size  INTEGER NOT NULL DEFAULT 4096,
    status      TEXT NOT NULL DEFAULT 'online',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    volume_id   INTEGER NOT NULL REFERENCES volumes(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    size_bytes  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS io_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    volume_id   INTEGER NOT NULL REFERENCES volumes(id) ON DELETE CASCADE,
    operation   TEXT NOT NULL CHECK(operation IN ('read', 'write', 'flush')),
    block_index INTEGER,
    block_count INTEGER DEFAULT 1,
    latency_us  REAL,
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_io_events_volume ON io_events(volume_id);
CREATE INDEX IF NOT EXISTS idx_io_events_timestamp ON io_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_snapshots_volume ON snapshots(volume_id);
