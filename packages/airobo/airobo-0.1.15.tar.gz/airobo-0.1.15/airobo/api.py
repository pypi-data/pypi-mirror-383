"""
API callbacks!
"""

# Declarations / modules
from airobo.modules.publishAndroid import publish_android
from airobo.modules.publishIOS import publish_ios

# ======================================================================================

"""
Simulate publishing something.
"""
def publish(plat=None):
    if plat != "ios" and plat != "android" and plat != None:
        return "Supply a valid platform type!"
    if plat == "ios":
        publish_ios()
    elif plat == "android":
        publish_android()
    else:                       #default : publish all.
        publish_ios()
        publish_android()

#----------------------------------------

"""
Get version from package metadata
"""
def version():
    try:
        import importlib.metadata
        # Get version from installed package metadata
        print(importlib.metadata.version('airobo'))
    except Exception:
        # Fallback if package not installed or other error
        print("0.1.10")