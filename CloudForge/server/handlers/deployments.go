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

// DeploymentHandler holds the database connection for deployment endpoints.
type DeploymentHandler struct {
	DB *sql.DB
}

// Deploy handles POST /api/v1/apps/{id}/deploy — triggers a new deployment.
func (h *DeploymentHandler) Deploy(w http.ResponseWriter, r *http.Request) {
	appID := chi.URLParam(r, "id")

	// Verify app exists
	app, err := database.GetApp(h.DB, appID)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "app not found"})
		return
	}

	// Get next version number
	latestVersion, err := database.GetLatestDeploymentVersion(h.DB, appID)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to get deployment version"})
		return
	}

	dep := database.Deployment{
		ID:        uuid.New().String(),
		AppID:     appID,
		Version:   latestVersion + 1,
		Status:    "pending",
		Image:     "cloudforge/" + app.Name + ":v" + itoa(latestVersion+1),
		CreatedAt: time.Now(),
	}

	if err := database.CreateDeployment(h.DB, dep); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to create deployment"})
		return
	}

	// Update app status
	database.UpdateAppStatus(h.DB, appID, "deploying")

	// Log the deployment
	database.InsertLog(h.DB, appID, dep.ID, "info", "Deployment v"+itoa(dep.Version)+" started")

	// Simulate build pipeline: pending -> building -> running
	go func() {
		time.Sleep(500 * time.Millisecond)
		database.UpdateDeploymentStatus(h.DB, dep.ID, "building", false)
		database.InsertLog(h.DB, appID, dep.ID, "info", "Building container image...")

		time.Sleep(1 * time.Second)
		database.UpdateDeploymentStatus(h.DB, dep.ID, "running", true)
		database.UpdateAppStatus(h.DB, appID, "running")
		database.InsertLog(h.DB, appID, dep.ID, "info", "Deployment v"+itoa(dep.Version)+" is running")
	}()

	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(models.DeploymentResponse{Deployment: dep})
}

// ListDeployments handles GET /api/v1/apps/{id}/deployments
func (h *DeploymentHandler) ListDeployments(w http.ResponseWriter, r *http.Request) {
	appID := chi.URLParam(r, "id")
	deps, err := database.ListDeployments(h.DB, appID)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "failed to list deployments"})
		return
	}

	if deps == nil {
		deps = []database.Deployment{}
	}

	json.NewEncoder(w).Encode(models.DeploymentsResponse{Deployments: deps, Total: len(deps)})
}

// GetDeployment handles GET /api/v1/deployments/{id}
func (h *DeploymentHandler) GetDeployment(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	dep, err := database.GetDeployment(h.DB, id)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "deployment not found"})
		return
	}

	json.NewEncoder(w).Encode(models.DeploymentResponse{Deployment: dep})
}

// Rollback handles POST /api/v1/apps/{id}/rollback — rolls back to previous version.
func (h *DeploymentHandler) Rollback(w http.ResponseWriter, r *http.Request) {
	appID := chi.URLParam(r, "id")

	deps, err := database.ListDeployments(h.DB, appID)
	if err != nil || len(deps) < 2 {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(models.ErrorResponse{Error: "no previous deployment to rollback to"})
		return
	}

	// Mark current as stopped, previous as running
	database.UpdateDeploymentStatus(h.DB, deps[0].ID, "stopped", true)
	database.UpdateDeploymentStatus(h.DB, deps[1].ID, "running", false)
	database.UpdateAppStatus(h.DB, appID, "running")
	database.InsertLog(h.DB, appID, deps[1].ID, "info", "Rolled back to v"+itoa(deps[1].Version))

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(models.DeploymentResponse{Deployment: deps[1]})
}

func itoa(n int) string {
	return json.Number(json.Number(string(rune('0'+n%10)))).String()
}
