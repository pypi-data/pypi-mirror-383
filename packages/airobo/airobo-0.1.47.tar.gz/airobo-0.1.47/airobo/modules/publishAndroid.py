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
        
        # Ensure Android SDK is configured
        _ensure_android_sdk_config(android_path)
        
        # Set Gradle JVM args to handle Java compatibility
        _set_gradle_jvm_args(android_path)
        
        # Run Gradle with real-time output filtering
        gradle_cmd = "gradlew.bat" if os.name == 'nt' else "./gradlew"
        
        # Run Gradle build with compatibility flags
        gradle_args = [gradle_cmd, "bundleRelease", "-Dorg.gradle.java.home="]
        
        # Try to detect and use Java 11 specifically
        java_11_path = _find_java_11()
        if java_11_path:
            gradle_args = [gradle_cmd, "bundleRelease", f"-Dorg.gradle.java.home={java_11_path}"]
            print(f"✅ Using Java 11: {java_11_path}")
        
        result = subprocess.run(
            gradle_args,
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

def _ensure_android_sdk_config(android_path):
    """
    Ensure Android SDK is properly configured by creating local.properties file
    """
    local_properties_path = os.path.join(android_path, "local.properties")
    
    # Try to find Android SDK location
    android_home = None
    
    # Check environment variable first
    android_home = os.environ.get('ANDROID_HOME')
    
    if not android_home:
        # Try common Windows locations
        common_paths = [
            os.path.expanduser("~/AppData/Local/Android/Sdk"),
            "C:/Users/%s/AppData/Local/Android/Sdk" % os.getlogin(),
            "C:/Android/Sdk",
            "C:/Program Files/Android/Sdk",
            "C:/Program Files (x86)/Android/Sdk"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                android_home = path.replace("\\", "/")
                break
    
    if android_home:
        # Create or update local.properties
        with open(local_properties_path, 'w') as f:
            f.write(f"sdk.dir={android_home}\n")
        print(f"✅ Android SDK configured: {android_home}")
    else:
        print("⚠️ Android SDK not found. Please install Android Studio or set ANDROID_HOME")
        print("   Download from: https://developer.android.com/studio")

def _set_gradle_jvm_args(android_path):
    """
    Set Gradle JVM arguments to handle Java compatibility issues
    """
    gradle_properties_path = os.path.join(android_path, "gradle.properties")
    
    # Read existing properties
    properties = {}
    if os.path.exists(gradle_properties_path):
        with open(gradle_properties_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    properties[key] = value
    
    # Add JVM args to handle Java compatibility
    properties['org.gradle.jvmargs'] = '-Xmx2048m -Dfile.encoding=UTF-8'
    
    # Write updated properties
    with open(gradle_properties_path, 'w') as f:
        f.write("# Auto-generated by airobo\n")
        for key, value in properties.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Gradle JVM args configured")

def _find_java_11():
    """
    Try to find Java 11 installation
    """
    # Common Java 11 installation paths on Windows
    java_paths = [
        "C:/Program Files/Java/jdk-11",
        "C:/Program Files/Java/jdk-11.0.1",
        "C:/Program Files/Java/jdk-11.0.2", 
        "C:/Program Files/Java/jdk-11.0.3",
        "C:/Program Files/Java/jdk-11.0.4",
        "C:/Program Files/Java/jdk-11.0.5",
        "C:/Program Files/Java/jdk-11.0.6",
        "C:/Program Files/Java/jdk-11.0.7",
        "C:/Program Files/Java/jdk-11.0.8",
        "C:/Program Files/Java/jdk-11.0.9",
        "C:/Program Files/Java/jdk-11.0.10",
        "C:/Program Files/Java/jdk-11.0.11",
        "C:/Program Files/Java/jdk-11.0.12",
        "C:/Program Files/Java/jdk-11.0.13",
        "C:/Program Files/Java/jdk-11.0.14",
        "C:/Program Files/Java/jdk-11.0.15",
        "C:/Program Files/Java/jdk-11.0.16",
        "C:/Program Files/Java/jdk-11.0.17",
        "C:/Program Files/Java/jdk-11.0.18",
        "C:/Program Files/Java/jdk-11.0.19",
        "C:/Program Files/Java/jdk-11.0.20",
        "C:/Program Files/Java/jdk-11.0.21",
        "C:/Program Files/Java/jdk-11.0.22",
        "C:/Program Files/Java/jdk-11.0.23",
        "C:/Program Files/Java/jdk-11.0.24",
        "C:/Program Files/Java/jdk-11.0.25",
        "C:/Program Files (x86)/Java/jdk-11",
    ]
    
    for path in java_paths:
        if os.path.exists(path):
            return path
    
    return None

def _ensure_java_config(android_path):
    """
    Ensure Java version compatibility by updating gradle.properties
    """
    gradle_properties_path = os.path.join(android_path, "gradle.properties")
    
    # Check current Java version
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True, shell=True)
        java_version_output = result.stderr  # Java version is printed to stderr
        
        # Extract major version number
        import re
        version_match = re.search(r'"(\d+)\.?(\d+)?', java_version_output)
        if version_match:
            major_version = int(version_match.group(1))
            if major_version == 1:  # Handle old format like "1.8"
                major_version = int(version_match.group(2)) if version_match.group(2) else 8
        else:
            major_version = 11  # Default fallback
            
        print(f"✅ Detected Java version: {major_version}")
        
        # Read existing gradle.properties
        gradle_props = {}
        if os.path.exists(gradle_properties_path):
            with open(gradle_properties_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        gradle_props[key] = value
        
        # Set appropriate Java version settings
        # Remove org.gradle.java.home to let Gradle auto-detect Java
        if 'org.gradle.java.home' in gradle_props:
            del gradle_props['org.gradle.java.home']
            
        if major_version >= 17:
            # Use Java 17+ settings
            gradle_props['android.compileSdk'] = '34'
            gradle_props['android.targetSdk'] = '34'
            gradle_props['android.minSdk'] = '21'
        else:
            # Use Java 11 compatible settings
            gradle_props['android.compileSdk'] = '33'
            gradle_props['android.targetSdk'] = '33' 
            gradle_props['android.minSdk'] = '21'
        
        # Also ensure JAVA_HOME is set for this process
        if not os.environ.get('JAVA_HOME'):
            # Try to detect JAVA_HOME
            try:
                java_home_result = subprocess.run(['where', 'java'], capture_output=True, text=True, shell=True)
                if java_home_result.returncode == 0:
                    java_path = java_home_result.stdout.strip().split('\n')[0]
                    # Extract JAVA_HOME from java.exe path
                    java_home = os.path.dirname(os.path.dirname(java_path))
                    os.environ['JAVA_HOME'] = java_home
                    print(f"✅ Set JAVA_HOME: {java_home}")
            except:
                pass
        
        # Write updated gradle.properties
        with open(gradle_properties_path, 'w') as f:
            f.write("# Auto-generated by airobo\n")
            for key, value in gradle_props.items():
                f.write(f"{key}={value}\n")
        
        # Also update app-level build.gradle to force Java compatibility
        _force_java_compatibility(android_path, major_version)
                
        print(f"✅ Java compatibility configured")
        
    except Exception as e:
        print(f"⚠️ Could not detect Java version: {e}")
        print("   Make sure Java is installed and in your PATH")

def _force_java_compatibility(android_path, java_version):
    """
    Force Java compatibility in all build.gradle files
    """
    import re
    
    # Determine the Java version to use (11 is most compatible)
    target_java_version = 11 if java_version <= 11 else 17
    
    # Add compileOptions block
    compile_options = f"""
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_{target_java_version}
        targetCompatibility JavaVersion.VERSION_{target_java_version}
    }}"""
    
    # Find all build.gradle files in the android directory
    build_gradle_files = []
    for root, dirs, files in os.walk(android_path):
        for file in files:
            if file == "build.gradle":
                build_gradle_files.append(os.path.join(root, file))
    
    updated_count = 0
    for gradle_file in build_gradle_files:
        try:
            with open(gradle_file, 'r') as f:
                content = f.read()
            
            # Only update files that have an 'android' block (library modules)
            if 'android {' in content or 'android{' in content:
                original_content = content
                
                # Check if compileOptions already exists
                if 'compileOptions' in content:
                    # Replace existing compileOptions
                    pattern = r'compileOptions\s*\{[^}]*\}'
                    content = re.sub(pattern, compile_options.strip(), content)
                else:
                    # Add compileOptions after android block starts
                    android_pattern = r'(android\s*\{)'
                    content = re.sub(android_pattern, r'\1' + compile_options, content)
                
                # Only write if content changed
                if content != original_content:
                    with open(gradle_file, 'w') as f:
                        f.write(content)
                    
                    relative_path = os.path.relpath(gradle_file, android_path)
                    print(f"✅ Updated {relative_path} for Java {target_java_version} compatibility")
                    updated_count += 1
                    
        except Exception as e:
            print(f"⚠️ Could not update {gradle_file}: {e}")
    
    if updated_count == 0:
        print(f"⚠️ No build.gradle files were updated")
    else:
        print(f"✅ Updated {updated_count} build.gradle files")