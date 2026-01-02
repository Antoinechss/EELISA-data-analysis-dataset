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

# Run dashboard (choose one)
streamlit run dashboard/app.py
python3 main.py
```

## Testing Deployment Readiness
```bash
python3 test_deployment.py
```

## Cloud Platform Deployment

### Streamlit Cloud / Streamlit Community Cloud
**Entry Point Options:**
1. `main.py` (recommended for cloud platforms)
2. `dashboard/app.py`

**Python Version:** 3.11+

**Setup:**
1. Fork/clone this repository
2. Connect to Streamlit Cloud
3. Set entry point to `main.py` or `dashboard/app.py`
4. Deploy

### Other Cloud Platforms (Heroku, Railway, etc.)
**Entry Point:** `main.py`
**Command:** `python main.py`
**Port:** 8501 (default Streamlit port)

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t eelisa-dashboard .

# Run container
docker run -p 8501:8501 eelisa-dashboard
```

## Troubleshooting

### Import Errors
- The app now includes automatic path setup for deployment environments
- All imports are handled dynamically to work in various deployment contexts
- If you see `ModuleNotFoundError`, try using `main.py` as entry point

### File Path Issues
- All file paths are now relative and work in any deployment environment
- Dataset and static files are automatically located

## Environment Requirements
- Python 3.11+
- All dependencies listed in requirements.txt
- Access to datasets folder
- Minimum 512MB RAM recommended
