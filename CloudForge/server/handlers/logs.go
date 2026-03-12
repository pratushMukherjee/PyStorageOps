package handlers

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/pratushMukherjee/CloudForge/server/database"
	"github.com/pratushMukherjee/CloudForge/server/models"
)

// LogHandler holds the database connection for log endpoints.
type LogHandler struct {
	DB *sql.DB
}

// GetLogs handles GET /api/v1/apps/{id}/logs
func (h *LogHandler) GetLogs(w http.ResponseWriter, r *http.Request) {
	appID := chi.URLParam(r, "id")

	limit := 50
	if l := r.URL.Query().Get("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil && parsed > 0 {
			limit = parsed
		}
	}

	logs, err := database.GetLogs(h.DB, appID, limit)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to retrieve logs"})
		return
	}

	if logs == nil {
		logs = []map[string]interface{}{}
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"app_id": appID,
		"logs":   logs,
		"total":  len(logs),
	})
}
