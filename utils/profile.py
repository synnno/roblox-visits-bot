import os
import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
import time
import pyautogui
import sys
import psutil

console = Console()

def get_chrome_profiles(base_path):
    profiles = []
    for entry in os.listdir(base_path):
        profile_path = os.path.join(base_path, entry)
        if os.path.isdir(profile_path) and (entry.startswith('Profile ') or entry == 'Default'):
            profiles.append(profile_path)
    return profiles

def get_profile_name(profile_path):
    preferences_file = os.path.join(profile_path, 'Preferences')
    if not os.path.exists(preferences_file):
        return None
    
    try:
        with open(preferences_file, 'r', encoding='utf-8') as file:
            preferences = json.load(file)
        
        profile_info = preferences.get('profile', {})
        profile_name = profile_info.get('name', 'Unknown Profile')
        return profile_name
    except (json.JSONDecodeError, KeyError):
        return 'Error reading Preferences file'

def display_profiles(profiles, selected_profiles):
    console.clear()
    
    table = Table(title="Available Chrome Profiles", title_style="bold cyan")
    table.add_column("Number", style="bold green", width=10)
    table.add_column("Profile Name", style="bold yellow", width=30)
    
    for idx, profile in enumerate(profiles):
        table.add_row(str(idx + 1), profile['profile_name'])
    
    console.print(table)

    if selected_profiles:
        selected_table = Table(title="Opened Profiles", title_style="bold magenta")
        selected_table.add_column("Profile Name", style="bold green", width=30)
        
        for profile_name in selected_profiles:
            selected_table.add_row(profile_name)
        
        console.print(selected_table)
    
    console.print(Panel("[bold yellow]Type 'close' to close all roblox instances.[/bold yellow]", style="yellow"))

def open_with_profile(profile_path, roblox_link):
    chrome_path = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    profile_dir = os.path.basename(profile_path)
    
    command = [
        str(chrome_path),
        f'--profile-directory={profile_dir}',
        roblox_link
    ]
    
    try:
        subprocess.Popen(command)
        time.sleep(0.5)
        pyautogui.hotkey('alt', 'tab')
        
    except FileNotFoundError:
        console.print("[bold red]Error: Chrome executable not found. Please check the path.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def close_all_roblox_instances():
    try:
        # Use taskkill to terminate Roblox processes
        result = subprocess.run(['taskkill', '/F', '/IM', 'robloxPlayerBeta.exe'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[bold green]All Roblox instances have been closed.[/bold green]")
        else:
            console.print(f"[bold yellow]No Roblox instances were found to close or an error occurred.[/bold yellow]")
            console.print(f"[bold red]{result.stderr}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error closing Roblox instances: {e}[/bold red]")

def profile_selection(roblox_link):
    base_path = str(Path.home() / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data')
    
    profiles = get_chrome_profiles(base_path)
    all_profile_names = []
    
    for idx, profile in enumerate(profiles):
        profile_name = get_profile_name(profile)
        if profile_name:
            display_name = f'Person {idx + 1}'
            all_profile_names.append({
                'profile_path': profile,
                'profile_name': display_name
            })

    selected_profiles = []

    if all_profile_names:
        while True:
            display_profiles(all_profile_names, selected_profiles)

            try:
                choice = Prompt.ask("[bold yellow]Enter the number of your choice (or 0 to return to the main menu):", default='0')
                
                if choice.lower() == 'close':
                    close_all_roblox_instances()
                    continue
                
                choice = int(choice)
                
                if choice == 0:
                    console.print(Panel("[bold red]Returning to the main menu.[/bold red]", style="red"))
                    sys.exit()
                elif 1 <= choice <= len(all_profile_names):
                    selected_profile = all_profile_names[choice - 1]
                    profile_name = selected_profile['profile_name']
                    
                    if profile_name not in selected_profiles:
                        selected_profiles.append(profile_name)
                    
                    console.print(Panel(f"You selected: [bold green]{profile_name}[/bold green]", title="Profile Selected", style="green"))
                    open_with_profile(selected_profile['profile_path'], roblox_link)
                    
                else:
                    console.print("[bold red]Invalid choice. please enter a valid number.[/bold red]")
            except ValueError:
                console.print("[bold red]Invalid input.[/bold red]")
    else:
        console.print(Panel("[bold red]No Chrome profiles found.[/bold red]", style="red"))

def main():
    console.clear() 
    
    intro_text = Text("https://github.com/synnno", style="bold bright_cyan")
    intro_text.append("\n\nPlease enter the roblox vip server link for the game you want to visit bot.", style="dim")
    console.print(intro_text, justify="center")

    while True:
        roblox_link = Prompt.ask("[bold yellow]roblox vip server Link:[/bold yellow]")
        if "roblox.com" in roblox_link:
            break
        else:
            console.print(Panel("[bold red]Invalid link![/bold red]\n[bold yellow]Please enter a valid roblox vip server link.[/bold yellow]", style="red"))
            time.sleep(1)
            console.clear()
            console.print(intro_text, justify="center")
    
    console.print(Panel(f"[bold green]roblox vip Server Link:[/bold green] {roblox_link}", title="Link Entered", style="green"))
    console.print("\n[bold cyan]Proceeding with Chrome profile selection...[/bold cyan]")
    
    time.sleep(1)  

    while True:
        profile_selection(roblox_link)
        console.print(Panel("[bold yellow]Returning to the main menu...[/bold yellow]", style="yellow"))
        time.sleep(1)

if __name__ == "__main__":
    main()
