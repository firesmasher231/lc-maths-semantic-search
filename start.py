#!/usr/bin/env python3
"""
Railway startup script for LC Maths Semantic Search
This script runs the existing run.py from the api directory.
"""

import sys
import os

# Add the api directory to Python path
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api")
sys.path.insert(0, api_dir)

# Change working directory to api
os.chdir(api_dir)

# Import and execute run.py
if __name__ == "__main__":
    exec(open("run.py").read())
