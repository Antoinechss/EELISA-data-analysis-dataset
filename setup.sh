#!/bin/bash
# Setup script for EELISA Dashboard

echo "Setting up EELISA European Job Market Dashboard..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "To run the dashboard:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run dashboard: ./run_dashboard.sh"
echo "   or: streamlit run dashboard/app.py"
