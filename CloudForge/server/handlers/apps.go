package handlers

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
	"github.com/pratushMukherjee/CloudForge/server/database"
	"github.com/pratushMukherjee/CloudForge/server/models"
)

// AppHandler holds the database connection for app endpoints.
type AppHandler struct {
	DB *sql.DB
}

// CreateApp handles POST /api/v1/apps
func (h *AppHandler) CreateApp(w http.ResponseWriter, r *http.Request) {
	var req models.CreateAppRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "invalid JSON body"})
		return
	}

	if req.Name == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "name is required"})
		return
	}

	if req.Language == "" {
		req.Language = "unknown"
	}

	app := database.App{
		ID:        uuid.New().String(),
		Name:      req.Name,
		Language:  req.Language,
		Status:    "created",
		Port:      0,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := database.CreateApp(h.DB, app); err != nil {
		w.WriteHeader(http.StatusConflict)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "app name already exists"})
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(models.AppResponse{App: app})
}

// ListApps handles GET /api/v1/apps
func (h *AppHandler) ListApps(w http.ResponseWriter, r *http.Request) {
	apps, err := database.ListApps(h.DB)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to list apps"})
		return
	}

	if apps == nil {
		apps = []database.App{}
	}

	json.NewEncoder(w).Encode(models.AppsResponse{Apps: apps, Total: len(apps)})
}

// GetApp handles GET /api/v1/apps/{id}
func (h *AppHandler) GetApp(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	app, err := database.GetApp(h.DB, id)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "app not found"})
		return
	}

	json.NewEncoder(w).Encode(models.AppResponse{App: app})
}

// DeleteApp handles DELETE /api/v1/apps/{id}
func (h *AppHandler) DeleteApp(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := database.DeleteApp(h.DB, id); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to delete app"})
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// SetEnvVar handles POST /api/v1/apps/{id}/env
func (h *AppHandler) SetEnvVar(w http.ResponseWriter, r *http.Request) {
	appID := chi.URLParam(r, "id")

	var req models.SetEnvRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "invalid JSON body"})
		return
	}

	ev := database.EnvVar{
		ID:    uuid.New().String(),
		AppID: appID,
		Key:   req.Key,
		Value: req.Value,
	}

	if err := database.SetEnvVar(h.DB, ev); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to set env var"})
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "set", "key": req.Key})
}

// GetEnvVars handles GET /api/v1/apps/{id}/env
func (h *AppHandler) GetEnvVars(w http.ResponseWriter, r *http.Request) {
	appID := chi.URLParam(r, "id")
	vars, err := database.GetEnvVars(h.DB, appID)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to get env vars"})
		return
	}
	if vars == nil {
		vars = []database.EnvVar{}
	}
	json.NewEncoder(w).Encode(map[string]interface{}{"env_vars": vars})
}
