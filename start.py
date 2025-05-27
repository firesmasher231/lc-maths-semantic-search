#!/usr/bin/env python3
"""
Railway startup script for LC Maths Semantic Search
This script starts the application from the root directory.
"""

import sys
import os
import threading

# Add the api directory to Python path
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api")
sys.path.insert(0, api_dir)

# Change working directory to api
os.chdir(api_dir)

# Import the app and initialization function
from api.app import app, initialize_searcher

if __name__ == "__main__":
    print("=" * 60)
    print("LC Maths Question Search Web Application")
    print("=" * 60)
    print("Starting the application...")
    print("This may take a few minutes on first run while processing PDFs.")
    print("=" * 60)

    # Start initialization in background
    init_thread = threading.Thread(target=initialize_searcher)
    init_thread.daemon = True
    init_thread.start()

    # Get port from environment (Railway sets this)
    port = int(os.environ.get("PORT", 5000))

    # Run the Flask app
    app.run(host="0.0.0.0", port=port, debug=False)
