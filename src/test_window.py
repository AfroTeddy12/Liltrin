import tkinter as tk
from tkinter import ttk, messagebox
import sys
import time
import threading

def keep_alive():
    """Keep the window alive by periodically checking its state"""
    while True:
        try:
            if not root.winfo_exists():
                print("Window was destroyed!")
                break
            print("Window is still alive")
            root.update()
            time.sleep(1)
        except Exception as e:
            print(f"Keep alive error: {str(e)}")
            break

def main():
    global root
    try:
        print("Creating root window...")
        root = tk.Tk()
        root.title("Test Window")
        root.geometry("300x200")
        
        # Make window stay on top
        root.attributes('-topmost', True)
        
        print("Creating frame...")
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        print("Creating label...")
        label = ttk.Label(frame, text="Test Window")
        label.grid(row=0, column=0, pady=5)
        
        print("Creating button...")
        button = ttk.Button(frame, text="Close", command=root.destroy)
        button.grid(row=1, column=0, pady=5)
        
        print("Setting up window...")
        root.protocol("WM_DELETE_WINDOW", lambda: print("Window closed"))
        
        # Start keep-alive thread
        print("Starting keep-alive thread...")
        keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        keep_alive_thread.start()
        
        print("Starting mainloop...")
        root.mainloop()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 