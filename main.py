import os
import time
import datetime
import subprocess
import pygetwindow as gw
import pyautogui
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from threading import Thread, Event, Lock
from rich.box import ROUNDED

console = Console()

visit_count = 0
timers = {}
timers_done_event = Event()
all_roblox_closed_event = Event()

def log(text):
    timestamp = datetime.datetime.utcfromtimestamp(time.time()).strftime("%H:%M:%S")
    console.log(f"[{timestamp}] {text}")

def is_roblox_running():
    try:
        result = subprocess.run('tasklist /FI "IMAGENAME eq RobloxPlayerBeta.exe"', shell=True, capture_output=True, text=True)
        running_instances = [line for line in result.stdout.splitlines() if "RobloxPlayerBeta.exe" in line]
        return {line.split()[1] for line in running_instances}
    except subprocess.SubprocessError as e:
        log(f"Error checking if Roblox is running: {e}")
        return set()

def is_multiroblox_running():
    try:
        result = subprocess.run('tasklist /FI "IMAGENAME eq MultiRoblox.exe"', shell=True, capture_output=True, text=True)
        running_instances = [line for line in result.stdout.splitlines() if "MultiRoblox.exe" in line]
        return bool(running_instances)
    except subprocess.SubprocessError as e:
        log(f"Error checking if MultiRoblox is running: {e}")
        return False

def run_roblox_installer():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    utils_dir = os.path.join(script_dir, 'utils')
    installer_py = os.path.join(utils_dir, 'robloxinstaller.py')

    if not os.path.exists(installer_py):
        console.print("[bold red]Error: robloxinstaller.py not found in the 'utils' folder.[/bold red]")
        exit()

    try:
        console.print("[bold yellow]Opening Roblox installer...[/bold yellow]")
        os.system(f'start python "{installer_py}"')
        console.print("[bold yellow]Roblox installer is now running.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error opening robloxinstaller.py: {e}[/bold red]")
        exit()

def close_roblox(pid):
    global visit_count
    try:
        result = subprocess.run(f'tasklist /FI "PID eq {pid}"', shell=True, capture_output=True, text=True)
        if str(pid) in result.stdout:
            result = subprocess.run(f"taskkill /PID {pid} /F > nul 2>&1", shell=True, check=True, capture_output=True, text=True)
            if result.returncode == 0:
                visit_count += 1
                log(f"Closed Roblox with PID {pid}")
            else:
                log(f"Failed to close Roblox with PID {pid}. Exit code: {result.returncode}. Error: {result.stderr}")
        else:
            log(f"PID {pid} does not exist.")
        update_cmd_title()
    except subprocess.SubprocessError as e:
        log(f"Error closing Roblox with PID {pid}: {e}")

def update_cmd_title():
    os.system(f"title Visits made: {visit_count}")

def handle_timer(pid):
    time.sleep(15)
    if pid in timers:
        close_roblox(pid)
        del timers[pid]
        if not timers:
            timers_done_event.set()

timers_lock = Lock()

def monitor_roblox_instances():
    global timers_done_event
    while True:
        running_pids = is_roblox_running()

        new_pids = running_pids - timers.keys()
        with timers_lock:
            for pid in new_pids:
                log(f"New Roblox instance detected with PID {pid}. Setting timer.")
                timers[pid] = Thread(target=handle_timer, args=(pid,))
                timers[pid].start()

        completed_pids = []
        with timers_lock:
            completed_pids = [pid for pid in timers if pid not in running_pids]
            for pid in completed_pids:
                log(f"Removing timer for PID {pid} as it is no longer running.")
                timers[pid].join()
                if pid in timers:
                    del timers[pid]

        if not running_pids and not timers:
            log("All Roblox instances closed and timers finished.")
            timers_done_event.set()
            break

        time.sleep(2)

    timers_done_event.clear()

def wait_for_roblox_and_delay(wait_time):
    log("Waiting for Roblox to start...")
    while not is_roblox_running():
        time.sleep(2)

    log("Roblox is now running. Waiting for the specified time...")
    time.sleep(wait_time)

def refresh_all_chrome_tabs(wait_time): #de ce nu merge :(
    chrome_windows = [window for window in gw.getWindowsWithTitle('Google Chrome') if window.visible]
    
    for window in chrome_windows:
        log(f"Found Chrome window: {window.title}")
        try:
            window.activate()
            time.sleep(0.5)

            active_window = gw.getActiveWindow()
            if active_window and 'Google Chrome' in active_window.title:
                pyautogui.hotkey('ctrl', 'r')
                log("Sent Ctrl+R to Chrome")
                
                wait_for_roblox_and_delay(wait_time)
            else:
                log(f"Failed to focus on Chrome window '{window.title}', retrying...")
                window.activate()
                time.sleep(0.5)
                active_window = gw.getActiveWindow()
                if active_window and 'Google Chrome' in active_window.title:
                    pyautogui.hotkey('ctrl', 'r')
                    log("Sent Ctrl+R to Chrome after retrying")
                else:
                    log(f"Failed to focus on Chrome window '{window.title}' after retrying") 
        except Exception as e:
            log(f"Error sending Ctrl+R to Chrome window '{window.title}': {e}")

def start_visits_bot():
    log("Starting the Roblox visits bot...")
    wait_time = 1
    while True:
        refresh_all_chrome_tabs(wait_time)
        log("Successfully joined on all accounts.")
        timers_done_event.clear()
        monitor_thread = Thread(target=monitor_roblox_instances, daemon=True)
        monitor_thread.start()
        
        timers_done_event.wait()
        
        log("All Roblox instances closed. Restarting refresh process...")
        time.sleep(1)

def open_chrome_profiles():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    utils_dir = os.path.join(script_dir, 'utils')
    profile_py = os.path.join(utils_dir, 'profile.py')

    if not os.path.exists(profile_py):
        console.print("[bold red]Error: profile.py not found in the 'utils' folder.[/bold red]")
        return

    try:
        process = subprocess.Popen(['python', profile_py])
        process.wait()
        console.print("[bold yellow]Returning to main menu...[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error running profile.py: {e}[/bold red]")
    finally:
        start_menu()

def show_credits():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    console.print(Panel(
        "[bold cyan]Credits[/bold cyan]\n\n"
        "[bold]Script created by:[/bold] syn\n"
        "[bold]github:[/bold] https://github.com/synnno\n"
        "[bold]discord:[/bold] syn.00 ", 
        title="Credits",
        title_align="center",
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2),
        width=50
    ))
    
    choice = Prompt.ask("[bold yellow]Press 0 to return to the main menu:[/bold yellow]")
    
    if choice == '0':
        start_menu()
    else:
        console.print("[bold red]Invalid choice. Exiting...[/bold red]")
        exit()

def start_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    title_text = Text("Roblox Visit Botter", style="bold cyan", justify="center")
    console.print(Panel(title_text, expand=False, box=ROUNDED, padding=(1, 2), width=40))

    menu_text = Text("Choose an option:", style="bold magenta")
    menu_text.append("\n\n1. Start Botting Visits", style="bold green")
    menu_text.append("\n2. Open Chrome Profiles (Recommended)", style="bold green")
    menu_text.append("\n3. Credits", style="bold green")

    credits_message = Text("\n\nThis script was made with much 💖 by syn.", style="bold green", justify="center") #blablabla
    credits_message.append("\nAdd me on discord if u have issues syn.00", style="bold purple")

    full_menu_text = menu_text + credits_message

    console.print(Panel(full_menu_text, expand=False, box=ROUNDED, padding=(1, 2), width=60))

    choice = Prompt.ask("[bold yellow]Enter your choice (1, 2, or 3):[/bold yellow]")

    if choice == '1':
        start_visits_bot()
    elif choice == '2':
        open_chrome_profiles()
    elif choice == '3':
        show_credits()
    else:
        console.print("[bold red]Invalid choice. Please enter 1, 2, or 3.[/bold red]")
        start_menu()

def check_multiroblox():
    if not is_multiroblox_running():
        console.print("[bold red]MultiRoblox.exe is not running. Please open MultiRoblox.exe for the script to function properly.[/bold red]") #scary larry
        time.sleep(3)
        exit()

if __name__ == "__main__":
    run_roblox_installer()
    check_multiroblox()
    start_menu()
