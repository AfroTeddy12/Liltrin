import sys
import os
import subprocess
import psutil
import ctypes
from ctypes import wintypes
import time

def set_process_name(name):
    """Set the process name for better identification in Task Manager"""
    try:
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.SetConsoleTitleW(name)
    except:
        pass

def main():
    # Set the process name
    set_process_name("Trin Assistant")
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the GUI script
    gui_script = os.path.join(script_dir, "trin_gui.py")
    
    try:
        # Start the GUI
        process = subprocess.Popen([sys.executable, gui_script])
        
        # Keep checking if the process is still running
        while True:
            if process.poll() is not None:  # Process has ended
                break
            time.sleep(1)  # Check every second
            
    except Exception as e:
        print(f"Error: {str(e)}")
        time.sleep(5)  # Wait before closing to see any error messages

if __name__ == "__main__":
    main() 