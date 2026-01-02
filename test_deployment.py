#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""

import sys
import os

# Simulate deployment environment
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test if all imports work correctly"""
    try:
        # Test utils
        from dashboard.utils import get_dataset_path, get_static_path, get_project_root
        print("✓ Utils import successful")
        
        # Test path resolution
        print(f"✓ Project root: {os.path.basename(get_project_root())}")
        print(f"✓ Dataset path: {os.path.basename(get_dataset_path('european_jobs.csv'))}")
        
        # Test main app imports (without actually running streamlit)
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "dashboard/app.py")
        print("✓ App file can be loaded")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_file_existence():
    """Test if all required files exist"""
    from dashboard.utils import get_dataset_path, get_static_path
    
    required_files = [
        get_dataset_path('european_jobs.csv'),
        get_dataset_path('extractions.csv'),
        get_static_path('eelisa_logo.png'),
        get_static_path('DigComp.pdf'),
        get_static_path('GreenComp.pdf')
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {os.path.basename(file_path)}")
        else:
            print(f"✗ {os.path.basename(file_path)} - NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    print("EELISA Dashboard Deployment Test")
    print("=" * 40)
    
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing file existence...")
    files_ok = test_file_existence()
    
    print("\n" + "=" * 40)
    if imports_ok and files_ok:
        print("✅ All tests passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
