"""
API callbacks!
"""

# Declarations / modules
from airobo.modules import publishAndroid
from airobo.modules import publishIOS

# ======================================================================================

"""
Simulate publishing something.
"""
def publish(plat):
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
Simulate checking status.
"""
def version():
    print("2.2")