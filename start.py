#!/usr/bin/env python3
"""
Railway startup script for LC Maths Semantic Search
This script starts the application from the root directory.
"""

import sys
import os

# Add the api directory to Python path
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api")
sys.path.insert(0, api_dir)

# Change working directory to api
os.chdir(api_dir)

# Import and run the application
from api.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
