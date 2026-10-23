"""
Cloud Demo App - Microservice for Containerization & Kubernetes Orchestration
"""

import logging
import os
import socket
import sys
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template_string, request

# Initialize Flask application
app = Flask(__name__)

# Configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("cloud-demo")

# Application Start Timestamp for uptime calculation
START_TIME = time.time()

# Configuration from Environment Variables (with sensible defaults)
APP_TITLE = os.getenv("APP_TITLE", "Cloud-Based Containerization & Kubernetes Orchestration System")
APP_NAME = os.getenv("APP_NAME", "Cloud Demo App")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "Kubernetes Prototype")

# Kubernetes Downward API metadata (injected if running in k8s)
POD_NAME = os.getenv("POD_NAME", socket.gethostname())
POD_NAMESPACE = os.getenv("POD_NAMESPACE", "default")
POD_IP = os.getenv("POD_IP", "127.0.0.1")
NODE_NAME = os.getenv("NODE_NAME", "local-node")

# Simulated state for readiness & health toggles
APP_STATE = {
    "healthy": True,
    "ready": True,
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_title }}</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --primary-dark: #0284c7;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --code-bg: #0b1120;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 1.5rem;
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            width: 100%;
        }

        header {
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }

        header h1 {
            font-size: 1.85rem;
            color: var(--text-main);
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }

        header p {
            color: var(--text-muted);
            font-size: 1rem;
        }

        .badge-bar {
            display: flex;
            justify-content: center;
            gap: 0.75rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .badge-healthy {
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-version {
            background-color: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }

        .badge-env {
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: currentColor;
            display: inline-block;
            box-shadow: 0 0 8px currentColor;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
        }

        .card h3 {
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .metric-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-main);
            word-break: break-all;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }

        .metric-sub {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.4rem;
        }

        .k8s-banner {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(2, 132, 199, 0.05));
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .k8s-banner h2 {
            font-size: 1.25rem;
            color: var(--primary);
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .k8s-banner p {
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .k8s-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .feature-item {
            background-color: var(--code-bg);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 0.85rem;
        }

        .feature-item strong {
            display: block;
            color: var(--text-main);
            margin-bottom: 0.25rem;
        }

        .feature-item span {
            color: var(--text-muted);
        }

        .api-endpoints {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 2rem;
        }

        .api-endpoints h3 {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: var(--text-main);
        }

        .endpoint-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .endpoint-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.6rem 0.9rem;
            background-color: var(--code-bg);
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.9rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .endpoint-row a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }

        .endpoint-row a:hover {
            text-decoration: underline;
        }

        .method-badge {
            background-color: #0369a1;
            color: #e0f2fe;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }

        footer {
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            border-top: 1px solid var(--card-border);
            padding-top: 1.5rem;
            margin-top: 2rem;
        }

        .btn-refresh {
            background-color: var(--primary);
            color: #0f172a;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        .btn-refresh:hover {
            background-color: var(--primary-dark);
            color: #ffffff;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ app_name }}</h1>
            <p style="font-size: 1.15rem; font-weight: 600; color: var(--primary); margin-top: 0.25rem;">{{ app_title }}</p>
            <p style="margin-top: 0.5rem;">Demonstrating Microservices, Containerization &amp; Automated Kubernetes Orchestration</p>
            <div class="badge-bar">
                <div class="badge badge-healthy">
                    <span class="pulse-dot"></span> Status: {{ status }}
                </div>
                <div class="badge badge-version">
                    Version: v{{ app_version }}
                </div>
                <div class="badge badge-env">
                    Env: {{ environment }}
                </div>
            </div>
        </header>

        <section class="k8s-banner">
            <h2>☸ Kubernetes Managed Infrastructure</h2>
            <p>
                This application instance is running inside a Docker container orchestrated by Kubernetes.
                Kubernetes continuously monitors Pod health, automatically recovers failed instances,
                balances incoming network traffic across replicas, and performs zero-downtime rolling updates.
            </p>
            <div class="k8s-features">
                <div class="feature-item">
                    <strong>Autonomous Self-Healing</strong>
                    <span>If this Pod crashes or is deleted, the ReplicaSet immediately spawns a replacement.</span>
                </div>
                <div class="feature-item">
                    <strong>Elastic Scaling</strong>
                    <span>Scale horizontally from 1 to 10+ replicas with a single <code>kubectl</code> command.</span>
                </div>
                <div class="feature-item">
                    <strong>Rolling Deployments</strong>
                    <span>Transitions seamlessly between v1.0 and v1.1 without dropping active user connections.</span>
                </div>
                <div class="feature-item">
                    <strong>Health Probing</strong>
                    <span>Integrated <code>livenessProbe</code> and <code>readinessProbe</code> monitor process health.</span>
                </div>
            </div>
        </section>

        <section class="grid">
            <div class="card">
                <h3>Container / Pod Hostname</h3>
                <div class="metric-value">{{ pod_name }}</div>
                <div class="metric-sub">Assigned by Linux Container Namespace</div>
            </div>

            <div class="card">
                <h3>Pod IP Address</h3>
                <div class="metric-value">{{ pod_ip }}</div>
                <div class="metric-sub">Namespace: <code>{{ pod_namespace }}</code></div>
            </div>

            <div class="card">
                <h3>Cluster Node</h3>
                <div class="metric-value">{{ node_name }}</div>
                <div class="metric-sub">Kubernetes Worker / Master Host</div>
            </div>

            <div class="card">
                <h3>Instance Uptime</h3>
                <div class="metric-value">{{ uptime_str }}</div>
                <div class="metric-sub">Started: {{ start_time_str }} UTC</div>
            </div>
        </section>

        <section class="api-endpoints">
            <h3>Verified Health & Inspection Endpoints</h3>
            <div class="endpoint-list">
                <div class="endpoint-row">
                    <div>
                        <span class="method-badge">GET</span>
                        <a href="/health">/health</a> &mdash; Liveness Probe (HTTP 200 OK)
                    </div>
                    <span><code>status: UP</code></span>
                </div>
                <div class="endpoint-row">
                    <div>
                        <span class="method-badge">GET</span>
                        <a href="/ready">/ready</a> &mdash; Readiness Probe (Traffic Routing Gate)
                    </div>
                    <span><code>ready: true</code></span>
                </div>
                <div class="endpoint-row">
                    <div>
                        <span class="method-badge">GET</span>
                        <a href="/version">/version</a> &mdash; Application Semantic Version
                    </div>
                    <span><code>version: {{ app_version }}</code></span>
                </div>
                <div class="endpoint-row">
                    <div>
                        <span class="method-badge">GET</span>
                        <a href="/api/info">/api/info</a> &mdash; Complete System Diagnostics (JSON)
                    </div>
                    <span><code>runtime metadata</code></span>
                </div>
            </div>
        </section>

        <div style="text-align: center; margin-bottom: 1rem;">
            <button class="btn-refresh" onclick="window.location.reload();">🔄 Refresh Page to Test Load Balancing</button>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">
                When multiple replicas are running, refreshing routes traffic to different Pod Hostnames.
            </p>
        </div>

        <footer>
            <p>Cloud-Based Containerization Prototype &bull; Docker &bull; Kubernetes &bull; Python Flask</p>
            <p style="margin-top: 0.25rem;">Server Request Time: {{ request_time }} UTC</p>
        </footer>
    </div>
</body>
</html>
"""

def get_uptime_string():
    """Calculate human-readable uptime."""
    seconds = int(time.time() - START_TIME)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    if days > 0:
        return f"{days}d {hours}h {mins}m"
    if hours > 0:
        return f"{hours}h {mins}m {secs}s"
    return f"{mins}m {secs}s"


@app.before_request
def log_request_info():
    """Log incoming request path and client IP."""
    logger.debug(f"Request: {request.method} {request.path} from {request.remote_addr}")


@app.route("/")
def index():
    """Render the homepage displaying container and orchestration metadata."""
    logger.info("Serving homepage request")
    start_dt = datetime.fromtimestamp(START_TIME, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    now_dt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(
        HTML_TEMPLATE,
        app_title=APP_TITLE,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        environment=ENVIRONMENT,
        status="RUNNING" if APP_STATE["healthy"] else "DEGRADED",
        pod_name=POD_NAME,
        pod_namespace=POD_NAMESPACE,
        pod_ip=POD_IP,
        node_name=NODE_NAME,
        uptime_str=get_uptime_string(),
        start_time_str=start_dt,
        request_time=now_dt,
    )


@app.route("/health", methods=["GET"])
def health():
    """
    Kubernetes Liveness Probe Endpoint.
    Returns HTTP 200 when container process is healthy.
    Returns HTTP 503 if marked unhealthy (triggers Pod restart).
    """
    if not APP_STATE["healthy"]:
        logger.warning("Health check failed: Application marked unhealthy")
        return jsonify({
            "status": "DOWN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hostname": POD_NAME,
        }), 503

    return jsonify({
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": POD_NAME,
        "uptime": get_uptime_string(),
    }), 200


@app.route("/ready", methods=["GET"])
def ready():
    """
    Kubernetes Readiness Probe Endpoint.
    Returns HTTP 200 when ready to receive traffic.
    Returns HTTP 503 if not ready (Service stops sending traffic to this Pod).
    """
    if not APP_STATE["ready"]:
        logger.warning("Readiness check failed: Application not ready")
        return jsonify({
            "ready": False,
            "status": "NOT_READY",
            "hostname": POD_NAME,
        }), 503

    return jsonify({
        "ready": True,
        "status": "READY",
        "hostname": POD_NAME,
        "checks": {
            "application": "initialized",
            "network": "available",
        },
    }), 200


@app.route("/version", methods=["GET"])
def version():
    """
    Returns running application version and metadata.
    Essential for verifying rolling updates and rollback operations.
    """
    return jsonify({
        "appName": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "hostname": POD_NAME,
    }), 200


@app.route("/api/info", methods=["GET"])
def api_info():
    """Detailed JSON endpoint for diagnostic tools and automated tests."""
    return jsonify({
        "application": {
            "name": APP_NAME,
            "title": APP_TITLE,
            "version": APP_VERSION,
            "environment": ENVIRONMENT,
        },
        "system": {
            "hostname": POD_NAME,
            "podName": POD_NAME,
            "podNamespace": POD_NAMESPACE,
            "podIp": POD_IP,
            "nodeName": NODE_NAME,
            "uptime": get_uptime_string(),
            "serverTimeUtc": datetime.now(timezone.utc).isoformat(),
        },
        "health": {
            "healthy": APP_STATE["healthy"],
            "ready": APP_STATE["ready"],
        },
    }), 200


@app.errorhandler(404)
def not_found(e):
    """Graceful 404 handler returning JSON or HTML based on Accept header."""
    if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
        return jsonify({"error": "Resource not found", "path": request.path}), 404
    return (
        f"<div style='font-family:sans-serif;text-align:center;padding:3rem;background:#0f172a;color:#f8fafc;min-height:100vh;'>"
        f"<h2>404 - Not Found</h2><p>Endpoint <code>{request.path}</code> does not exist.</p>"
        f"<p><a href='/' style='color:#38bdf8;'>Return to Homepage</a></p></div>",
        404,
    )


@app.errorhandler(500)
def server_error(e):
    """Graceful 500 error handler."""
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} on port {port} (debug={debug_mode})")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
