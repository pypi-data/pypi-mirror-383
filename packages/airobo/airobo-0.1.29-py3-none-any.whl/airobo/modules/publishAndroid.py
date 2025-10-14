"""
Android App Publishing Module  
"""
import subprocess
import os
import platform
import sys
from pathlib import Path
from airobo.modules.capacitorMacro import prepare_capacitor_app, sync_platform


def run_in_separate_terminal(command, title="Android Build", working_dir=None):
    """
    Run a command in a separate terminal window (cross-platform)
    
    Args:
        command (list or str): Command to run
        title (str): Window title
        working_dir (str): Working directory for the command
    
    Returns:
        subprocess.Popen: Process object
    """
    if working_dir is None:
        working_dir = os.getcwd()
    
    # Convert command to string if it's a list
    if isinstance(command, list):
        cmd_str = ' '.join(command)
    else:
        cmd_str = command
    
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows: Use PowerShell in new window
            ps_command = f"""
            Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd "{working_dir}"; Write-Host "=== {title} ===" -ForegroundColor Green; {cmd_str}'
            """
            return subprocess.Popen(
                ["powershell", "-Command", ps_command],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
        elif system == "darwin":  # macOS
            # macOS: Use Terminal.app
            applescript = f'''
            tell application "Terminal"
                do script "cd '{working_dir}' && echo '=== {title} ===' && {cmd_str}"
                activate
            end tell
            '''
            return subprocess.Popen(["osascript", "-e", applescript])
            
        else:  # Linux and other Unix-like systems
            # Try common terminal emulators
            terminals = [
                "gnome-terminal", "konsole", "xterm", "lxterminal", 
                "mate-terminal", "xfce4-terminal", "terminator"
            ]
            
            for terminal in terminals:
                if subprocess.run(["which", terminal], capture_output=True).returncode == 0:
                    if terminal == "gnome-terminal":
                        return subprocess.Popen([
                            terminal, "--title", title, "--", 
                            "bash", "-c", f"cd '{working_dir}' && echo '=== {title} ===' && {cmd_str} && read -p 'Press Enter to close...'"
                        ])
                    elif terminal == "konsole":
                        return subprocess.Popen([
                            terminal, "--title", title, "-e", 
                            "bash", "-c", f"cd '{working_dir}' && echo '=== {title} ===' && {cmd_str} && read -p 'Press Enter to close...'"
                        ])
                    else:  # xterm and others
                        return subprocess.Popen([
                            terminal, "-title", title, "-e", 
                            "bash", "-c", f"cd '{working_dir}' && echo '=== {title} ===' && {cmd_str} && read -p 'Press Enter to close...'"
                        ])
            
            # Fallback: run in current terminal
            print(f"⚠️ No suitable terminal found, running in current terminal")
            return subprocess.Popen(cmd_str, shell=True, cwd=working_dir)
            
    except Exception as e:
        print(f"⚠️ Failed to open separate terminal: {e}")
        print("Running in current terminal instead...")
        return subprocess.Popen(cmd_str, shell=True, cwd=working_dir)

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
        
        # Run clean in current terminal (quick operation)
        subprocess.run([gradle_cmd, "clean"], check=True, shell=(os.name == 'nt'))
        
        print("Building release bundle...")
        
        # Ask user if they want to see build output in separate terminal
        show_in_terminal = input("Show build output in separate terminal? (y/n, default=y): ").strip().lower()
        if show_in_terminal == '' or show_in_terminal == 'y':
            print("📱 Opening build in separate terminal window...")
            
            # Run build in separate terminal
            gradle_cmd = "gradlew.bat" if os.name == 'nt' else "./gradlew"
            build_process = run_in_separate_terminal(
                [gradle_cmd, "bundleRelease"],
                title="Android Build - Gradle Bundle",
                working_dir=android_path
            )
            
            # Wait for build to complete
            build_result_code = build_process.wait()
            
            if build_result_code != 0:
                raise subprocess.CalledProcessError(build_result_code, f"{gradle_cmd} bundleRelease")
                
        else:
            # Run build in current terminal (original behavior)
            if os.name == 'nt':  # Windows
                subprocess.run(["gradlew.bat", "bundleRelease"], check=True, shell=True)
            else:  # macOS/Linux
                subprocess.run(["./gradlew", "bundleRelease"], check=True)
        
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