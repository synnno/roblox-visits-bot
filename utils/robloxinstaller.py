import os
import subprocess
from pathlib import Path
import psutil
from colorama import Fore
import datetime
import time

# THIS SCRIPT DELETES ROBLOXPLAYERINSTALLER BECAUSE IT INTERFERES WITH THE MULTIPLE ROBLOX INSTANCES AND MAKES THE SCRIPT INEFFICIENT
# THIS SCRIPT DELETES ROBLOXPLAYERINSTALLER BECAUSE IT INTERFERES WITH THE MULTIPLE ROBLOX INSTANCES AND MAKES THE SCRIPT INEFFICIENT 
# THIS SCRIPT DELETES ROBLOXPLAYERINSTALLER BECAUSE IT INTERFERES WITH THE MULTIPLE ROBLOX INSTANCES AND MAKES THE SCRIPT INEFFICIENT
#syn

def log(text, color=Fore.WHITE):
    timestamp = datetime.datetime.utcfromtimestamp(time.time()).strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {text}{Fore.RESET}")

def search_for_installer_in_versions(versions_path):
    installer_filename = 'RobloxPlayerInstaller.exe'
    for root, dirs, files in os.walk(versions_path):
        if installer_filename in files:
            file_path = Path(root) / installer_filename
            try:
                file_path.unlink()
                log(f"Successfully deleted {file_path}", color=Fore.GREEN)
                return True
            except Exception as e:
                log(f"Error deleting installer at {file_path}: {e}", color=Fore.RED)
                return False
    return False

def find_versions_directory_from_process():
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'RobloxPlayerBeta.exe':
                cmdline = proc.info['cmdline']
                for arg in cmdline:
                    if 'RobloxPlayerBeta.exe' in arg:
                        install_path = Path(arg).parent
                        versions_path = install_path / 'Versions'
                        if versions_path.exists():
                            return versions_path
    except Exception as e:
        log(f"Error accessing processes: {e}", color=Fore.RED)
    return None

def find_and_delete_installer():
    log("Starting search for RobloxPlayerInstaller.exe...", color=Fore.CYAN)

    versions_path = find_versions_directory_from_process()
    if versions_path:
        log(f"Found Versions directory: {versions_path}", color=Fore.CYAN)
        if not search_for_installer_in_versions(versions_path):
            log(f"Installer not found in {versions_path}. Searching other common directories...", color=Fore.YELLOW)
            possible_paths = [
                Path(os.environ['USERPROFILE']) / 'Downloads',
                Path(os.environ['PROGRAMFILES']),
                Path(os.environ['PROGRAMFILES(X86)']),
                Path(os.environ['LOCALAPPDATA']) / 'Roblox'
            ]
            for path in possible_paths:
                if (path / 'Versions').exists():
                    if search_for_installer_in_versions(path / 'Versions'):
                        return
            log("RobloxPlayerInstaller.exe not found.", color=Fore.RED)
    else:
        log("Unable to find Roblox Versions directory. Searching common directories...", color=Fore.YELLOW)
        possible_paths = [
            Path(os.environ['USERPROFILE']) / 'Downloads',
            Path(os.environ['PROGRAMFILES']),
            Path(os.environ['PROGRAMFILES(X86)']),
            Path(os.environ['LOCALAPPDATA']) / 'Roblox'
        ]
        for path in possible_paths:
            if (path / 'Versions').exists():
                if search_for_installer_in_versions(path / 'Versions'):
                    return
        log("RobloxPlayerInstaller.exe not found.", color=Fore.RED)

if __name__ == "__main__":
    find_and_delete_installer()
