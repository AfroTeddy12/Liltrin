import os
import sys
import ctypes
from pathlib import Path
import winshell
from win32com.client import Dispatch

def create_shortcut():
    try:
        # Get paths
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        launcher_path = script_dir / "launch_trin.pyw"
        desktop = Path(winshell.desktop())
        shortcut_path = desktop / "Trin Assistant.lnk"
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(sys.executable)
        shortcut.Arguments = f'"{launcher_path}"'
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = str(script_dir / "trin_icon.ico")
        shortcut.save()
        
        # Add to startup
        startup = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_shortcut = startup / "Trin Assistant.lnk"
        
        if not startup_shortcut.exists():
            shortcut = shell.CreateShortCut(str(startup_shortcut))
            shortcut.Targetpath = str(sys.executable)
            shortcut.Arguments = f'"{launcher_path}"'
            shortcut.WorkingDirectory = str(script_dir)
            shortcut.IconLocation = str(script_dir / "trin_icon.ico")
            shortcut.save()
            
        return True
        
    except Exception as e:
        print(f"Error creating shortcut: {str(e)}")
        return False

if __name__ == "__main__":
    if create_shortcut():
        print("Shortcuts created successfully!")
    else:
        print("Failed to create shortcuts.") 