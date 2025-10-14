# airobo/modules/capacitorBuild.py
"""
Shared Capacitor Build Module
"""
import subprocess
import os
import platform


def run_npm_in_terminal(command, title="NPM Process", working_dir=None):
    """
    Run an npm command in a separate terminal window (cross-platform)
    
    Args:
        command (list): npm command to run
        title (str): Window title
        working_dir (str): Working directory for the command
    
    Returns:
        subprocess.Popen: Process object
    """
    if working_dir is None:
        working_dir = os.getcwd()
    
    cmd_str = ' '.join(command)
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


def prepare_capacitor_app(app_path):
    print("Preparing Capacitor app...")
    
    try:
        original_dir = os.getcwd()
        os.chdir(app_path)
        
        print("Installing dependencies...")
        show_npm_install = input("Show npm install in separate terminal? (y/n, default=n): ").strip().lower()
        if show_npm_install == 'y':
            print("📦 Opening npm install in separate terminal...")
            npm_process = run_npm_in_terminal(["npm", "install"], "NPM Install", app_path)
            if npm_process.wait() != 0:
                raise subprocess.CalledProcessError(1, "npm install")
        else:
            subprocess.run(["npm", "install"], check=True, capture_output=True, shell=True)
        
        print("Building web assets...")
        show_npm_build = input("Show npm build in separate terminal? (y/n, default=n): ").strip().lower()
        if show_npm_build == 'y':
            print("🔨 Opening npm build in separate terminal...")
            build_process = run_npm_in_terminal(["npm", "run", "build"], "NPM Build", app_path)
            if build_process.wait() != 0:
                raise subprocess.CalledProcessError(1, "npm run build")
        else:
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