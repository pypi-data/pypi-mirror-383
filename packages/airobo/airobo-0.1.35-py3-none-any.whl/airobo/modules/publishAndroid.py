"""
Android App Publishing Module  
"""
import subprocess
import os
from pathlib import Path
from airobo.modules.capacitorMacro import prepare_capacitor_app, sync_platform

def publish_android(app_path):
    print("Starting Android build process...")
    
    if not prepare_capacitor_app(app_path):
        return {"success": False, "message": "Capacitor preparation failed"}
    
    if not sync_platform(app_path, "android"):
        return {"success": False, "message": "Android sync failed"}

    aab_path = build_android_bundle(app_path)
    if not aab_path:
        return {"success": False, "message": "Android build failed"}
    
    print(f"Android build completed: {aab_path}")
    print("=======================================")
    return {"success": True, "aab_path": aab_path}

def build_android_bundle(app_path):
    print("Building Android App Bundle...")
    
    import subprocess
    import os
    
    try:
        # Handle version management first
        if not update_android_version(app_path):
            print("❌ Failed to update Android version")
            return None
        
        # Create output directory in app cache
        output_dir = create_build_output_dir(app_path)
        aab_filename = "app-release.aab"
        target_aab_path = os.path.join(output_dir, aab_filename)
        
        # Path to Android project
        android_path = os.path.join(app_path, "android")
        
        if not os.path.exists(android_path):
            print("❌ Android directory not found")
            return None
        
        # Change to android directory
        original_dir = os.getcwd()
        os.chdir(android_path)
        
        # Clean and build
        print("Cleaning previous builds...")
        gradle_cmd = "gradlew.bat" if os.name == 'nt' else "./gradlew"
        
        # Run clean completely silently
        subprocess.run([gradle_cmd, "clean"], 
                      cwd=android_path, 
                      capture_output=True, 
                      check=True, 
                      shell=(os.name == 'nt'),
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        
        print("Building release bundle...")
        
        # Run Gradle with real-time output filtering
        gradle_cmd = "gradlew.bat" if os.name == 'nt' else "./gradlew"
        
        # Use Popen to capture output in real-time
        process = subprocess.Popen(
            [gradle_cmd, "bundleRelease"],
            cwd=android_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=(os.name == 'nt')
        )
        
        # Filter and display only progress-related output
        progress_indicators = ['%', 'CONFIGURING', 'EXECUTING', 'BUILD SUCCESSFUL', 'BUILD FAILED']
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            # Show lines that contain progress indicators or are very short status updates
            if any(indicator in line.upper() for indicator in progress_indicators) or \
               (len(line) < 50 and ('>' in line or 'CONFIGURING' in line.upper())):
                print(f"  {line}")
        
        process.wait()
        
        if process.returncode != 0:
            print("❌ Build failed!")
            raise subprocess.CalledProcessError(process.returncode, gradle_cmd)
        
        print("✅ Build completed successfully!")
        
        # Find and copy the generated .aab file
        default_aab_path = os.path.join(android_path, "app/build/outputs/bundle/release/app-release.aab")
        
        if os.path.exists(default_aab_path):
            import shutil
            shutil.copy2(default_aab_path, target_aab_path)
            print(f"App Bundle created at: {target_aab_path}")
            return target_aab_path
        else:
            print("❌ App Bundle not found after build")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Gradle build failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        return None
    finally:
        os.chdir(original_dir)

def update_android_version(app_path):
    """Update Android version codes before building using git commit count"""
    import os
    import re
    import subprocess
    from datetime import datetime
    
    print("Updating Android version...")
    
    try:
        # Path to build.gradle file
        gradle_file = os.path.join(app_path, "android", "app", "build.gradle")
        
        if not os.path.exists(gradle_file):
            print("❌ build.gradle not found")
            return False
        
        # Get git commit count as version code
        original_dir = os.getcwd()
        os.chdir(app_path)
        
        try:
            git_result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            new_version_code = int(git_result.stdout.strip())
        except subprocess.CalledProcessError:
            print("❌ Failed to get git commit count, using timestamp fallback")
            new_version_code = int(datetime.now().timestamp())
        finally:
            os.chdir(original_dir)
        
        # Get git tag or branch for version name
        os.chdir(app_path)
        try:
            # Try to get latest git tag
            tag_result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"], 
                capture_output=True, 
                text=True
            )
            if tag_result.returncode == 0:
                version_name = tag_result.stdout.strip()
            else:
                # Fallback to branch name + commit count
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                    capture_output=True, 
                    text=True,
                    check=True
                )
                branch_name = branch_result.stdout.strip()
                version_name = f"{branch_name}-{new_version_code}"
        except subprocess.CalledProcessError:
            # Final fallback
            version_name = f"build-{new_version_code}"
        finally:
            os.chdir(original_dir)
        
        # Read current build.gradle
        with open(gradle_file, 'r') as f:
            content = f.read()
        
        # Update versionCode
        content = re.sub(
            r'versionCode\s+\d+',
            f'versionCode {new_version_code}',
            content
        )
        
        # Update versionName
        content = re.sub(
            r'versionName\s+["\'][^"\']*["\']',
            f'versionName "{version_name}"',
            content
        )
        
        # Write back to file
        with open(gradle_file, 'w') as f:
            f.write(content)
        
        print(f"Updated versionCode to: {new_version_code}")
        print(f"Updated versionName to: {version_name}")
        return True
        
    except Exception as e:
        print(f"❌ Version update failed: {e}")
        return False

def get_current_version_info(app_path):
    """Get current version info from build.gradle"""
    import os
    import re
    
    gradle_file = os.path.join(app_path, "android", "app", "build.gradle")
    
    if not os.path.exists(gradle_file):
        return None
    
    try:
        with open(gradle_file, 'r') as f:
            content = f.read()
        
        version_code_match = re.search(r'versionCode\s+(\d+)', content)
        version_name_match = re.search(r'versionName\s+["\']([^"\']*)["\']', content)
        
        return {
            "version_code": int(version_code_match.group(1)) if version_code_match else None,
            "version_name": version_name_match.group(1) if version_name_match else None
        }
    except:
        return None

def create_build_output_dir(app_path):
    """Create a build output directory in the app cache"""
    import os
    
    # Create builds directory in the same cache location as the app
    app_name = os.path.basename(app_path)
    cache_dir = os.path.dirname(app_path)  # This is the app-cache directory
    build_dir = os.path.join(cache_dir, f"{app_name}-builds", "android")
    
    # Create directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)
    
    print(f"Build output directory: {build_dir}")
    return build_dir