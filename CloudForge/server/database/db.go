package database

import (
	"database/sql"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// Init opens the SQLite database and creates tables.
func Init(path string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", path+"?_journal_mode=WAL")
	if err != nil {
		return nil, err
	}

	if err := migrate(db); err != nil {
		return nil, err
	}
	return db, nil
}

func migrate(db *sql.DB) error {
	schema := `
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
	`
	_, err := db.Exec(schema)
	return err
}

// App represents a deployed application.
type App struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Language  string    `json:"language"`
	Status    string    `json:"status"`
	Port      int       `json:"port"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Deployment represents a single deployment of an app.
type Deployment struct {
	ID          string     `json:"id"`
	AppID       string     `json:"app_id"`
	Version     int        `json:"version"`
	Status      string     `json:"status"`
	Image       string     `json:"image"`
	ContainerID string     `json:"container_id"`
	BuildLog    string     `json:"build_log"`
	CreatedAt   time.Time  `json:"created_at"`
	FinishedAt  *time.Time `json:"finished_at,omitempty"`
}

// EnvVar represents an environment variable for an app.
type EnvVar struct {
	ID    string `json:"id"`
	AppID string `json:"app_id"`
	Key   string `json:"key"`
	Value string `json:"value"`
}

// CreateApp inserts a new app into the database.
func CreateApp(db *sql.DB, app App) error {
	_, err := db.Exec(
		"INSERT INTO apps (id, name, language, status, port, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
		app.ID, app.Name, app.Language, app.Status, app.Port, app.CreatedAt, app.UpdatedAt,
	)
	return err
}

// GetApp retrieves an app by ID.
func GetApp(db *sql.DB, id string) (*App, error) {
	app := &App{}
	err := db.QueryRow("SELECT id, name, language, status, port, created_at, updated_at FROM apps WHERE id = ?", id).
		Scan(&app.ID, &app.Name, &app.Language, &app.Status, &app.Port, &app.CreatedAt, &app.UpdatedAt)
	if err != nil {
		return nil, err
	}
	return app, nil
}

// ListApps returns all apps.
func ListApps(db *sql.DB) ([]App, error) {
	rows, err := db.Query("SELECT id, name, language, status, port, created_at, updated_at FROM apps ORDER BY created_at DESC")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var apps []App
	for rows.Next() {
		var a App
		if err := rows.Scan(&a.ID, &a.Name, &a.Language, &a.Status, &a.Port, &a.CreatedAt, &a.UpdatedAt); err != nil {
			return nil, err
		}
		apps = append(apps, a)
	}
	return apps, nil
}

// DeleteApp removes an app by ID.
func DeleteApp(db *sql.DB, id string) error {
	_, err := db.Exec("DELETE FROM apps WHERE id = ?", id)
	return err
}

// UpdateAppStatus updates the status of an app.
func UpdateAppStatus(db *sql.DB, id, status string) error {
	_, err := db.Exec("UPDATE apps SET status = ?, updated_at = ? WHERE id = ?", status, time.Now(), id)
	return err
}

// CreateDeployment inserts a new deployment.
func CreateDeployment(db *sql.DB, dep Deployment) error {
	_, err := db.Exec(
		"INSERT INTO deployments (id, app_id, version, status, image, container_id, build_log, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
		dep.ID, dep.AppID, dep.Version, dep.Status, dep.Image, dep.ContainerID, dep.BuildLog, dep.CreatedAt,
	)
	return err
}

// GetDeployment retrieves a deployment by ID.
func GetDeployment(db *sql.DB, id string) (*Deployment, error) {
	dep := &Deployment{}
	err := db.QueryRow(
		"SELECT id, app_id, version, status, image, container_id, build_log, created_at, finished_at FROM deployments WHERE id = ?", id,
	).Scan(&dep.ID, &dep.AppID, &dep.Version, &dep.Status, &dep.Image, &dep.ContainerID, &dep.BuildLog, &dep.CreatedAt, &dep.FinishedAt)
	if err != nil {
		return nil, err
	}
	return dep, nil
}

// ListDeployments returns all deployments for an app.
func ListDeployments(db *sql.DB, appID string) ([]Deployment, error) {
	rows, err := db.Query(
		"SELECT id, app_id, version, status, image, container_id, build_log, created_at, finished_at FROM deployments WHERE app_id = ? ORDER BY version DESC", appID,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var deps []Deployment
	for rows.Next() {
		var d Deployment
		if err := rows.Scan(&d.ID, &d.AppID, &d.Version, &d.Status, &d.Image, &d.ContainerID, &d.BuildLog, &d.CreatedAt, &d.FinishedAt); err != nil {
			return nil, err
		}
		deps = append(deps, d)
	}
	return deps, nil
}

// UpdateDeploymentStatus updates a deployment's status and optionally sets finished_at.
func UpdateDeploymentStatus(db *sql.DB, id, status string, finished bool) error {
	if finished {
		now := time.Now()
		_, err := db.Exec("UPDATE deployments SET status = ?, finished_at = ? WHERE id = ?", status, now, id)
		return err
	}
	_, err := db.Exec("UPDATE deployments SET status = ? WHERE id = ?", status, id)
	return err
}

// GetLatestDeploymentVersion returns the latest version number for an app.
func GetLatestDeploymentVersion(db *sql.DB, appID string) (int, error) {
	var version int
	err := db.QueryRow("SELECT COALESCE(MAX(version), 0) FROM deployments WHERE app_id = ?", appID).Scan(&version)
	return version, err
}

// SetEnvVar upserts an environment variable for an app.
func SetEnvVar(db *sql.DB, ev EnvVar) error {
	_, err := db.Exec(
		"INSERT INTO env_vars (id, app_id, key, value) VALUES (?, ?, ?, ?) ON CONFLICT(app_id, key) DO UPDATE SET value = ?",
		ev.ID, ev.AppID, ev.Key, ev.Value, ev.Value,
	)
	return err
}

// GetEnvVars returns all env vars for an app.
func GetEnvVars(db *sql.DB, appID string) ([]EnvVar, error) {
	rows, err := db.Query("SELECT id, app_id, key, value FROM env_vars WHERE app_id = ?", appID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var vars []EnvVar
	for rows.Next() {
		var v EnvVar
		if err := rows.Scan(&v.ID, &v.AppID, &v.Key, &v.Value); err != nil {
			return nil, err
		}
		vars = append(vars, v)
	}
	return vars, nil
}

// InsertLog adds a log entry.
func InsertLog(db *sql.DB, appID, deploymentID, level, message string) error {
	_, err := db.Exec(
		"INSERT INTO app_logs (app_id, deployment_id, level, message) VALUES (?, ?, ?, ?)",
		appID, deploymentID, level, message,
	)
	return err
}

// GetLogs returns recent logs for an app.
func GetLogs(db *sql.DB, appID string, limit int) ([]map[string]interface{}, error) {
	rows, err := db.Query(
		"SELECT level, message, timestamp FROM app_logs WHERE app_id = ? ORDER BY timestamp DESC LIMIT ?",
		appID, limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var logs []map[string]interface{}
	for rows.Next() {
		var level, message, ts string
		if err := rows.Scan(&level, &message, &ts); err != nil {
			return nil, err
		}
		logs = append(logs, map[string]interface{}{
			"level":     level,
			"message":   message,
			"timestamp": ts,
		})
	}
	return logs, nil
}
