#!/usr/bin/env python3
"""
CloudForge CLI — Command-line tool for managing deployments.

Usage:
    cloudforge apps                     List all apps
    cloudforge create <name> [lang]     Create a new app
    cloudforge deploy <app_id>          Deploy an app
    cloudforge rollback <app_id>        Rollback to previous version
    cloudforge logs <app_id>            View app logs
    cloudforge status <app_id>          Get app status
    cloudforge delete <app_id>          Delete an app
    cloudforge env <app_id> set K=V     Set an environment variable
    cloudforge env <app_id> list        List environment variables
    cloudforge ai <question>            Ask the AI assistant
"""

import os
import sys

import httpx

API_URL = os.getenv("CLOUDFORGE_API_URL", "http://localhost:8080")
AI_URL = os.getenv("CLOUDFORGE_AI_URL", "http://localhost:8081")
API_KEY = os.getenv("CLOUDFORGE_API_KEY", "")


def headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def cmd_apps():
    r = httpx.get(f"{API_URL}/api/v1/apps", headers=headers())
    data = r.json()
    apps = data.get("apps", [])
    if not apps:
        print("No apps found. Create one with: cloudforge create <name>")
        return
    print(f"{'NAME':<20} {'STATUS':<12} {'LANGUAGE':<10} {'ID'}")
    print("-" * 60)
    for app in apps:
        print(f"{app['name']:<20} {app['status']:<12} {app['language']:<10} {app['id'][:8]}")


def cmd_create(name: str, language: str = "python"):
    r = httpx.post(f"{API_URL}/api/v1/apps", json={"name": name, "language": language}, headers=headers())
    if r.status_code == 201:
        app = r.json()["app"]
        print(f"App '{app['name']}' created (ID: {app['id'][:8]})")
    else:
        print(f"Error: {r.json().get('error', 'unknown')}")


def cmd_deploy(app_id: str):
    r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/deploy", headers=headers())
    if r.status_code == 202:
        dep = r.json()["deployment"]
        print(f"Deployment v{dep['version']} started (ID: {dep['id'][:8]})")
        print(f"Image: {dep['image']}")
        print("Status: pending -> building -> running")
    else:
        print(f"Error: {r.json().get('error', 'unknown')}")


def cmd_rollback(app_id: str):
    r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/rollback", headers=headers())
    if r.status_code == 200:
        dep = r.json()["deployment"]
        print(f"Rolled back to v{dep['version']}")
    else:
        print(f"Error: {r.json().get('error', 'unknown')}")


def cmd_logs(app_id: str):
    r = httpx.get(f"{API_URL}/api/v1/apps/{app_id}/logs?limit=30", headers=headers())
    logs = r.json().get("logs", [])
    for log in reversed(logs):
        level = log["level"].upper()
        print(f"[{log['timestamp']}] [{level}] {log['message']}")


def cmd_status(app_id: str):
    r = httpx.get(f"{API_URL}/api/v1/apps/{app_id}", headers=headers())
    if r.status_code == 200:
        app = r.json()["app"]
        print(f"Name:     {app['name']}")
        print(f"Status:   {app['status']}")
        print(f"Language: {app['language']}")
        print(f"Port:     {app.get('port', 'auto')}")
        print(f"ID:       {app['id']}")
    else:
        print(f"Error: {r.json().get('error', 'not found')}")


def cmd_delete(app_id: str):
    r = httpx.delete(f"{API_URL}/api/v1/apps/{app_id}", headers=headers())
    if r.status_code == 204:
        print("App deleted.")
    else:
        print(f"Error deleting app")


def cmd_env(app_id: str, action: str, kv: str = ""):
    if action == "list":
        r = httpx.get(f"{API_URL}/api/v1/apps/{app_id}/env", headers=headers())
        for v in r.json().get("env_vars", []):
            print(f"{v['key']}={v['value']}")
    elif action == "set" and "=" in kv:
        key, value = kv.split("=", 1)
        r = httpx.post(f"{API_URL}/api/v1/apps/{app_id}/env", json={"key": key, "value": value}, headers=headers())
        print(f"Set {key}")
    else:
        print("Usage: cloudforge env <app_id> set KEY=VALUE")


def cmd_ai(question: str):
    try:
        r = httpx.post(f"{AI_URL}/api/v1/ai/chat", json={"message": question}, timeout=30)
        print(r.json().get("reply", "No response"))
    except httpx.ConnectError:
        print("AI service not available. Start it with: uvicorn ai-service.main:app --port 8081")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "apps":
        cmd_apps()
    elif cmd == "create" and len(args) >= 2:
        cmd_create(args[1], args[2] if len(args) > 2 else "python")
    elif cmd == "deploy" and len(args) >= 2:
        cmd_deploy(args[1])
    elif cmd == "rollback" and len(args) >= 2:
        cmd_rollback(args[1])
    elif cmd == "logs" and len(args) >= 2:
        cmd_logs(args[1])
    elif cmd == "status" and len(args) >= 2:
        cmd_status(args[1])
    elif cmd == "delete" and len(args) >= 2:
        cmd_delete(args[1])
    elif cmd == "env" and len(args) >= 3:
        cmd_env(args[1], args[2], args[3] if len(args) > 3 else "")
    elif cmd == "ai" and len(args) >= 2:
        cmd_ai(" ".join(args[1:]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
