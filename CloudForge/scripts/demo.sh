#!/usr/bin/env bash
# CloudForge — Demo Script
# Demonstrates the platform by creating and deploying a sample app.
set -euo pipefail

API="http://localhost:8080"
AI="http://localhost:8081"

echo "=== CloudForge Demo ==="
echo ""

# Health check
echo "1. Health Check"
curl -s "$API/health" | python3 -m json.tool
echo ""

# Create app
echo "2. Creating app 'demo-api'..."
APP=$(curl -s -X POST "$API/api/v1/apps" \
    -H "Content-Type: application/json" \
    -d '{"name":"demo-api","language":"python"}')
echo "$APP" | python3 -m json.tool
APP_ID=$(echo "$APP" | python3 -c "import sys,json; print(json.load(sys.stdin)['app']['id'])")
echo "   App ID: $APP_ID"
echo ""

# Set env var
echo "3. Setting environment variable..."
curl -s -X POST "$API/api/v1/apps/$APP_ID/env" \
    -H "Content-Type: application/json" \
    -d '{"key":"DATABASE_URL","value":"sqlite:///app.db"}' | python3 -m json.tool
echo ""

# Deploy
echo "4. Deploying..."
curl -s -X POST "$API/api/v1/apps/$APP_ID/deploy" \
    -H "Content-Type: application/json" | python3 -m json.tool
echo ""

# Wait for deployment
echo "5. Waiting for deployment to complete..."
sleep 3

# Check status
echo "6. App status:"
curl -s "$API/api/v1/apps/$APP_ID" | python3 -m json.tool
echo ""

# View logs
echo "7. Logs:"
curl -s "$API/api/v1/apps/$APP_ID/logs" | python3 -m json.tool
echo ""

# AI assistant
echo "8. Asking AI for help..."
curl -s -X POST "$AI/api/v1/ai/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"How do I deploy a Python Flask app?"}' | python3 -m json.tool
echo ""

echo "=== Demo Complete ==="
