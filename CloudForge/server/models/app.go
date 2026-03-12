package models

// CreateAppRequest is the JSON body for creating an app.
type CreateAppRequest struct {
	Name     string `json:"name"`
	Language string `json:"language,omitempty"`
}

// DeployRequest is the JSON body for triggering a deployment.
type DeployRequest struct {
	Source string `json:"source,omitempty"` // git URL or local path
}

// SetEnvRequest is the JSON body for setting an environment variable.
type SetEnvRequest struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}

// AppResponse wraps an app for API responses.
type AppResponse struct {
	App interface{} `json:"app"`
}

// AppsResponse wraps a list of apps.
type AppsResponse struct {
	Apps  interface{} `json:"apps"`
	Total int         `json:"total"`
}

// DeploymentResponse wraps a deployment.
type DeploymentResponse struct {
	Deployment interface{} `json:"deployment"`
}

// DeploymentsResponse wraps a list of deployments.
type DeploymentsResponse struct {
	Deployments interface{} `json:"deployments"`
	Total       int         `json:"total"`
}

// ErrorResponse is a standard error body.
type ErrorResponse struct {
	Error string `json:"error"`
}

// HealthResponse is the health check response.
type HealthResponse struct {
	Status  string `json:"status"`
	Service string `json:"service"`
	Version string `json:"version"`
}
