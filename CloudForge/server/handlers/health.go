package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/pratushMukherjee/CloudForge/server/models"
)

// HealthCheck returns the server health status.
func HealthCheck(w http.ResponseWriter, r *http.Request) {
	resp := models.HealthResponse{
		Status:  "healthy",
		Service: "CloudForge API",
		Version: "1.0.0",
	}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}
