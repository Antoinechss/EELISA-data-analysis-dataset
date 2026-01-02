#!/usr/bin/env python3
"""
Deployment entry point for EELISA Dashboard
This file ensures proper path setup for cloud deployment platforms
"""

import sys
import os

# Get the directory where this script is located (project root)
project_root = os.path.dirname(os.path.abspath(__file__))

# Add project root to Python path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import and run the main app
if __name__ == "__main__":
    import subprocess
    import sys
    
    # Run streamlit with the corrected app path
    app_path = os.path.join(project_root, "dashboard", "app.py")
    
    # Execute streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", app_path] + sys.argv[1:]
    subprocess.run(cmd)
