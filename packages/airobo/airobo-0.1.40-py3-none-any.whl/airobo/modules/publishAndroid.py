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
        
        # Stop any running Gradle daemons first
        try:
            subprocess.run([gradle_cmd, "--stop"], 
                          cwd=android_path, 
                          shell=(os.name == 'nt'),
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
        except:
            pass  # Ignore if daemon stop fails
        
        # Try Gradle clean first
        try:
            subprocess.run([gradle_cmd, "clean"], 
                          cwd=android_path, 
                          check=True, 
                          shell=(os.name == 'nt'),
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            print("✅ Clean completed")
        except subprocess.CalledProcessError:
            print("⚠️ Gradle clean failed, attempting force clean...")
            
            # Force clean by manually deleting build directories
            import shutil
            import time
            
            build_dirs = [
                os.path.join(android_path, "app", "build"),
                os.path.join(android_path, "build"),
                os.path.join(android_path, ".gradle")
            ]
            
            for build_dir in build_dirs:
                if os.path.exists(build_dir):
                    try:
                        # Wait a moment and try to delete
                        time.sleep(1)
                        shutil.rmtree(build_dir, ignore_errors=True)
                        print(f"🗑️ Removed {os.path.basename(build_dir)} directory")
                    except Exception as e:
                        print(f"⚠️ Could not remove {os.path.basename(build_dir)}: {str(e)[:50]}...")
            
            print("✅ Force clean completed")
        
        print("Building release bundle...")
        
        # Run Gradle with real-time output filtering
        gradle_cmd = "gradlew.bat" if os.name == 'nt' else "./gradlew"
        
        # Run Gradle build and capture all output for error analysis
        result = subprocess.run(
            [gradle_cmd, "bundleRelease"],
            cwd=android_path,
            capture_output=True,
            text=True,
            shell=(os.name == 'nt')
        )
        
        if result.returncode != 0:
            print("❌ Build failed! Error details:")
            print("STDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            raise subprocess.CalledProcessError(result.returncode, gradle_cmd)
        else:
            # Show only success-related output on successful build
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if 'BUILD SUCCESSFUL' in line or '%' in line or 'bundleRelease' in line:
                    print(f"  {line}")
            print("✅ Build completed successfully!")
        
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