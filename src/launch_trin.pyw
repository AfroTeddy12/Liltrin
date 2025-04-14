import os
import sys
import subprocess
import ctypes
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Get the directory where the script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if running as admin
    if not is_admin():
        # Re-run the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return
        
    try:
        # Start the assistant
        assistant_script = script_dir / "trin_assistant.py"
        subprocess.Popen([sys.executable, str(assistant_script)])
        
    except Exception as e:
        # Show error message
        ctypes.windll.user32.MessageBoxW(0, str(e), "Trin Assistant Error", 0x10)
        
if __name__ == "__main__":
    main() 