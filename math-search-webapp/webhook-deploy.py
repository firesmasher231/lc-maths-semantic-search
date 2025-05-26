#!/usr/bin/env python3
"""
GitHub Webhook Deployment Server
Listens for GitHub webhook events and automatically deploys the application
"""

import os
import sys
import json
import hmac
import hashlib
import subprocess
from flask import Flask, request, jsonify
import logging

# Configuration
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "your-webhook-secret-here")
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
ALLOWED_BRANCHES = ["main", "master"]
PORT = int(os.environ.get("WEBHOOK_PORT", 9000))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("webhook-deploy.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def verify_signature(payload_body, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256 signature."""
    if not signature_header:
        return False

    hash_object = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        logger.info(f"Running command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or REPO_PATH,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            logger.info(f"Command succeeded: {result.stdout}")
            return True, result.stdout
        else:
            logger.error(f"Command failed: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return False, "Command timed out"
    except Exception as e:
        logger.error(f"Command error: {str(e)}")
        return False, str(e)


def deploy_application():
    """Deploy the application using our deployment script."""
    logger.info("Starting deployment process...")

    # Change to the repository directory
    os.chdir(REPO_PATH)

    # Pull latest changes
    success, output = run_command("git pull origin main")
    if not success:
        logger.error(f"Git pull failed: {output}")
        return False, f"Git pull failed: {output}"

    # Make sure deploy script is executable
    run_command("chmod +x deploy.sh")

    # Deploy using our script
    success, output = run_command("./deploy.sh update")
    if not success:
        logger.error(f"Deployment failed: {output}")
        return False, f"Deployment failed: {output}"

    logger.info("Deployment completed successfully")
    return True, "Deployment successful"


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle GitHub webhook events."""

    # Verify the request signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 401

    # Parse the payload
    try:
        payload = request.get_json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {str(e)}")
        return jsonify({"error": "Invalid JSON"}), 400

    # Check if this is a push event
    if request.headers.get("X-GitHub-Event") != "push":
        logger.info(f"Ignoring non-push event: {request.headers.get('X-GitHub-Event')}")
        return jsonify({"message": "Event ignored"}), 200

    # Check if the push is to an allowed branch
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")

    if branch not in ALLOWED_BRANCHES:
        logger.info(f"Ignoring push to branch: {branch}")
        return jsonify({"message": f"Branch {branch} ignored"}), 200

    logger.info(f"Received push event for branch: {branch}")

    # Deploy the application
    success, message = deploy_application()

    if success:
        return (
            jsonify(
                {
                    "message": "Deployment successful",
                    "branch": branch,
                    "details": message,
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {"error": "Deployment failed", "branch": branch, "details": message}
            ),
            500,
        )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return (
        jsonify(
            {"status": "healthy", "webhook_server": "running", "repo_path": REPO_PATH}
        ),
        200,
    )


@app.route("/deploy", methods=["POST"])
def manual_deploy():
    """Manual deployment endpoint (for testing)."""
    logger.info("Manual deployment triggered")

    success, message = deploy_application()

    if success:
        return (
            jsonify({"message": "Manual deployment successful", "details": message}),
            200,
        )
    else:
        return jsonify({"error": "Manual deployment failed", "details": message}), 500


if __name__ == "__main__":
    logger.info(f"Starting webhook deployment server on port {PORT}")
    logger.info(f"Repository path: {REPO_PATH}")
    logger.info(f"Allowed branches: {ALLOWED_BRANCHES}")

    app.run(host="0.0.0.0", port=PORT, debug=False)
