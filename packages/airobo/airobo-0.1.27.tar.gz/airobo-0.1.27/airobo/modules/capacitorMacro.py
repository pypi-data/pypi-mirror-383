# airobo/modules/capacitorBuild.py
"""
Shared Capacitor Build Module
"""
import subprocess
import os

def prepare_capacitor_app(app_path):
    print("Preparing Capacitor app...")
    
    try:
        original_dir = os.getcwd()
        os.chdir(app_path)
        
        print("Installing dependencies...")
        subprocess.run(["npm", "install"], check=True, capture_output=True, shell=True)
        
        print("Building web assets...")
        subprocess.run(["npm", "run", "build"], check=True, capture_output=True, shell=True)
        
        print("Capacitor app prepared")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Capacitor preparation failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def sync_platform(app_path, platform):
    print(f"Syncing to {platform}...")
    
    try:
        original_dir = os.getcwd()
        os.chdir(app_path)
        
        subprocess.run(["npx", "cap", "sync", platform], check=True, capture_output=True, shell=True)
        
        print(f"{platform} sync completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {platform} sync failed: {e}")
        return False
    finally:
        os.chdir(original_dir)