-- CloudForge database schema (SQLite)
-- This file documents the schema; migrations are handled in Go code.

CREATE TABLE IF NOT EXISTS apps (
    id          TEXT PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    language    TEXT NOT NULL DEFAULT 'unknown',
    status      TEXT NOT NULL DEFAULT 'created',
    port        INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deployments (
    id          TEXT PRIMARY KEY,
    app_id      TEXT NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    version     INTEGER NOT NULL DEFAULT 1,
    status      TEXT NOT NULL DEFAULT 'pending',
    image       TEXT DEFAULT '',
    container_id TEXT DEFAULT '',
    build_log   TEXT DEFAULT '',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME
);

CREATE TABLE IF NOT EXISTS env_vars (
    id      TEXT PRIMARY KEY,
    app_id  TEXT NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    key     TEXT NOT NULL,
    value   TEXT NOT NULL,
    UNIQUE(app_id, key)
);

CREATE TABLE IF NOT EXISTS app_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id      TEXT NOT NULL REFERENCES apps(id) ON DELETE CASCADE,
    deployment_id TEXT,
    level       TEXT DEFAULT 'info',
    message     TEXT NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deployments_app ON deployments(app_id);
CREATE INDEX IF NOT EXISTS idx_logs_app ON app_logs(app_id);
CREATE INDEX IF NOT EXISTS idx_env_app ON env_vars(app_id);
