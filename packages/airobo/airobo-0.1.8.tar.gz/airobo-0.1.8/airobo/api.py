"""
API callbacks!
"""
import os
import re

# Declarations / modules
from airobo.modules import publishAndroid
from airobo.modules import publishIOS

# ======================================================================================

"""
Simulate publishing something.
"""
def publish(plat=None):
    if plat != "ios" and plat != "android" and plat != None:
        return "Supply a valid platform type!"
    if plat == "ios":
        publishIOS()
    elif plat == "android":
        publishAndroid()
    else:                       #default : publish all.
        publishIOS()
        publishAndroid()

#----------------------------------------

"""
Get version from pyproject.toml
"""
def version():
    try:
        # First try to get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try multiple possible locations for pyproject.toml
        possible_paths = [
            # In development: go up one level from airobo/ to project root
            os.path.join(os.path.dirname(current_dir), 'pyproject.toml'),
            # Alternative: same directory as this file
            os.path.join(current_dir, 'pyproject.toml'),
            # Alternative: current working directory
            os.path.join(os.getcwd(), 'pyproject.toml')
        ]
        
        for toml_path in possible_paths:
            if os.path.exists(toml_path):
                with open(toml_path, 'r') as f:
                    content = f.read()
                    # Extract version using regex
                    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if version_match:
                        print(version_match.group(1))
                        return
        
        # If no file found, fallback
        print("0.1.7")  # Use current known version as fallback
    except Exception as e:
        # Fallback on any error
        print("0.1.7")
    except Exception:
        # Fallback on any error
        print("1337")