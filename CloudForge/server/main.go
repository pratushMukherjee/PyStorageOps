package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/pratushMukherjee/CloudForge/server/database"
	"github.com/pratushMukherjee/CloudForge/server/router"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	db, err := database.Init("cloudforge.db")
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	r := router.New(db)

	fmt.Printf("CloudForge API server starting on :%s\n", port)
	fmt.Printf("API docs: http://localhost:%s/health\n", port)

	if err := http.ListenAndServe(":"+port, r); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
