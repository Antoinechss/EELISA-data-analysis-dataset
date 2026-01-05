import os

def get_project_root():
    """Get the root directory of the project."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_dataset_path(filename):
    """Get the full path to a dataset file."""
    return os.path.join(get_project_root(), 'datasets', filename)


def get_static_path(filename):
    """Get the full path to a static file in the dashboard."""
    return os.path.join(get_project_root(), 'dashboard', 'static', filename)
