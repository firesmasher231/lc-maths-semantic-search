#!/usr/bin/env python3
"""
Simple startup script for the LC Maths Question Search Web Application.
This script can be used as an alternative to running app.py directly.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from app import app, initialize_searcher
import threading

if __name__ == "__main__":
    print("=" * 60)
    print("LC Maths Question Search Web Application")
    print("=" * 60)
    print("Starting the application...")
    print("This may take a few minutes on first run while processing PDFs.")
    print("Open your browser to: http://localhost:5000")
    print("=" * 60)

    # Start initialization in background
    init_thread = threading.Thread(target=initialize_searcher)
    init_thread.daemon = True
    init_thread.start()

    # Run the Flask app
    try:
        app.run(debug=False, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("\nShutting down the application...")
    except Exception as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)
