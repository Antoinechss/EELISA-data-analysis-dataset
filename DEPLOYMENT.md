# EELISA Dashboard Deployment Guide

## Quick Start

### Local Development
1. Run setup: `./setup.sh`
2. Start dashboard: `./run_dashboard.sh`

### Alternative Method
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard/app.py
```

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t eelisa-dashboard .

# Run container
docker run -p 8501:8501 eelisa-dashboard
```

## Production Deployment

### Streamlit Cloud
1. Fork/clone this repository
2. Connect to Streamlit Cloud
3. Deploy from `dashboard/app.py`

### Other Platforms
- Configure entry point: `streamlit run dashboard/app.py`
- Required Python version: 3.11+
- Memory requirement: ~512MB minimum

## Environment Requirements
- Python 3.11+
- All dependencies listed in requirements.txt
- Access to datasets folder
