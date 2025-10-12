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
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get to the project root
        project_root = os.path.dirname(current_dir)
        toml_path = os.path.join(project_root, 'pyproject.toml')
        
        if os.path.exists(toml_path):
            with open(toml_path, 'r') as f:
                content = f.read()
                # Extract version using regex
                version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if version_match:
                    print(version_match.group(1))
                    return
        
        # Fallback if file not found or version not found
        print("1337")
    except Exception:
        # Fallback on any error
        print("1337")