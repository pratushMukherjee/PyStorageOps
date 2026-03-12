package router

import (
	"database/sql"
	"net/http"

	"github.com/go-chi/chi/v5"
	chimw "github.com/go-chi/chi/v5/middleware"
	"github.com/pratushMukherjee/CloudForge/server/handlers"
	"github.com/pratushMukherjee/CloudForge/server/middleware"
)

// New creates and configures the chi router with all routes.
func New(db *sql.DB) http.Handler {
	r := chi.NewRouter()

	// Middleware stack
	r.Use(chimw.Logger)
	r.Use(chimw.Recoverer)
	r.Use(chimw.RequestID)
	r.Use(middleware.JSONContentType)
	r.Use(middleware.CORS)
	r.Use(middleware.APIKeyAuth)

	// Handlers
	appH := &handlers.AppHandler{DB: db}
	depH := &handlers.DeploymentHandler{DB: db}
	logH := &handlers.LogHandler{DB: db}

	// Health
	r.Get("/health", handlers.HealthCheck)

	// API v1
	r.Route("/api/v1", func(r chi.Router) {
		// Apps
		r.Post("/apps", appH.CreateApp)
		r.Get("/apps", appH.ListApps)
		r.Get("/apps/{id}", appH.GetApp)
		r.Delete("/apps/{id}", appH.DeleteApp)

		// Environment variables
		r.Post("/apps/{id}/env", appH.SetEnvVar)
		r.Get("/apps/{id}/env", appH.GetEnvVars)

		// Deployments
		r.Post("/apps/{id}/deploy", depH.Deploy)
		r.Get("/apps/{id}/deployments", depH.ListDeployments)
		r.Get("/deployments/{id}", depH.GetDeployment)
		r.Post("/apps/{id}/rollback", depH.Rollback)

		// Logs
		r.Get("/apps/{id}/logs", logH.GetLogs)
	})

	return r
}
