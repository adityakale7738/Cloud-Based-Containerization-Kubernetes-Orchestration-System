"""
Unit and Integration Tests for Cloud Demo App
Run with: python -m unittest discover tests
Or with: pytest tests/
"""

import json
import unittest
from app import app, APP_STATE


class CloudDemoAppTestCase(unittest.TestCase):
    """Test suite verifying web routes, health endpoints, and JSON responses."""

    def setUp(self):
        """Set up Flask test client before each test."""
        app.config["TESTING"] = True
        self.client = app.test_client()
        # Reset state
        APP_STATE["healthy"] = True
        APP_STATE["ready"] = True

    def test_homepage_status_and_content(self):
        """Verify that the homepage loads successfully and contains project details."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Cloud Demo App", content)
        self.assertIn("Kubernetes Managed Infrastructure", content)
        self.assertIn("/health", content)
        self.assertIn("/ready", content)
        self.assertIn("/version", content)

    def test_health_endpoint_success(self):
        """Verify Kubernetes liveness endpoint returns HTTP 200 and UP status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "UP")
        self.assertIn("timestamp", data)
        self.assertIn("hostname", data)

    def test_health_endpoint_failure_state(self):
        """Verify liveness endpoint returns HTTP 503 when application is unhealthy."""
        APP_STATE["healthy"] = False
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "DOWN")

    def test_ready_endpoint_success(self):
        """Verify Kubernetes readiness endpoint returns HTTP 200 and ready state."""
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("ready"))
        self.assertEqual(data.get("status"), "READY")

    def test_ready_endpoint_not_ready_state(self):
        """Verify readiness endpoint returns HTTP 503 when application is not ready."""
        APP_STATE["ready"] = False
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertFalse(data.get("ready"))
        self.assertEqual(data.get("status"), "NOT_READY")

    def test_version_endpoint(self):
        """Verify version endpoint reports correct version and app metadata."""
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("version", data)
        self.assertEqual(data.get("appName"), "Cloud Demo App")

    def test_api_info_endpoint(self):
        """Verify complete diagnostic API response."""
        response = self.client.get("/api/info")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("application", data)
        self.assertIn("system", data)
        self.assertIn("health", data)
        self.assertEqual(data["health"]["healthy"], True)

    def test_404_not_found(self):
        """Verify handling of nonexistent route returns HTTP 404."""
        response = self.client.get("/nonexistent-endpoint-xyz")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
