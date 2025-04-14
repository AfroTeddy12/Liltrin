import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os
from pathlib import Path
import psutil
import threading
import time
import math
import ctypes
from ctypes import wintypes
from PIL import Image, ImageTk
import io
import base64

def set_process_name(name):
    """Set the process name for better identification in Task Manager"""
    try:
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.SetConsoleTitleW(name)
    except:
        pass

class AnimatedCanvas(tk.Canvas):
    def __init__(self, parent, width, height):
        super().__init__(parent, width=width, height=height, bg='white', highlightthickness=0)
        self.width = width
        self.height = height
        self.animation_running = False
        self.current_state = "idle"
        self.wave_points = []
        self.animation_thread = None
        
    def start_animation(self, state):
        self.current_state = state
        if not self.animation_running:
            self.animation_running = True
            self.animation_thread = threading.Thread(target=self._animate, daemon=True)
            self.animation_thread.start()
            
    def stop_animation(self):
        self.animation_running = False
        self.delete("all")
        
    def _animate(self):
        while self.animation_running:
            self.delete("all")
            
            if self.current_state == "idle":
                self._draw_idle()
            elif self.current_state == "listening":
                self._draw_listening()
            elif self.current_state == "processing":
                self._draw_processing()
            elif self.current_state == "responding":
                self._draw_wave()
            elif self.current_state == "error":
                self._draw_error()
                
            self.update()
            time.sleep(0.05)
            
    def _draw_idle(self):
        # Draw a calm wave
        points = []
        for x in range(0, self.width + 1, 5):
            y = self.height/2 + math.sin(x/20 + time.time()) * 10
            points.extend([x, y])
        self.create_line(points, fill='blue', width=2, smooth=True)
        
    def _draw_listening(self):
        # Draw pulsing circles
        for i in range(3):
            radius = 10 + math.sin(time.time() * 2 + i) * 5
            self.create_oval(
                self.width/2 - radius, self.height/2 - radius,
                self.width/2 + radius, self.height/2 + radius,
                outline='green', width=2
            )
            
    def _draw_processing(self):
        # Draw rotating dots
        center_x, center_y = self.width/2, self.height/2
        for i in range(8):
            angle = time.time() * 2 + i * math.pi/4
            x = center_x + math.cos(angle) * 20
            y = center_y + math.sin(angle) * 20
            self.create_oval(x-3, y-3, x+3, y+3, fill='orange')
            
    def _draw_wave(self):
        # Draw animated wave
        points = []
        for x in range(0, self.width + 1, 5):
            y = self.height/2 + math.sin(x/10 + time.time() * 2) * 20
            points.extend([x, y])
        self.create_line(points, fill='blue', width=3, smooth=True)
        
    def _draw_error(self):
        # Draw error symbol
        self.create_line(
            self.width/2 - 15, self.height/2 - 15,
            self.width/2 + 15, self.height/2 + 15,
            fill='red', width=3
        )
        self.create_line(
            self.width/2 - 15, self.height/2 + 15,
            self.width/2 + 15, self.height/2 - 15,
            fill='red', width=3
        )

class TrinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trin Assistant")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Set process name
        set_process_name("Trin Assistant")
        
        # Set window icon (if you have one)
        # self.root.iconbitmap('trin_icon.ico')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create animation canvas
        self.canvas = AnimatedCanvas(self.main_frame, width=360, height=150)
        self.canvas.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Status: Stopped")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Start/Stop button
        self.toggle_button = ttk.Button(self.main_frame, text="Start Assistant", command=self.toggle_assistant)
        self.toggle_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Minimize to tray button
        self.minimize_button = ttk.Button(self.main_frame, text="Minimize to Tray", command=self.minimize_to_tray)
        self.minimize_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Exit button
        self.exit_button = ttk.Button(self.main_frame, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Initialize variables
        self.assistant_process = None
        self.is_running = False
        self.script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lil_trin.py")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_assistant, daemon=True)
        self.monitor_thread.start()
        
        # Start with idle animation
        self.canvas.start_animation("idle")
        
        # Prevent window from closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_assistant()
        self.root.destroy()
    
    def toggle_assistant(self):
        if not self.is_running:
            self.start_assistant()
        else:
            self.stop_assistant()
    
    def start_assistant(self):
        try:
            # Start the assistant script
            self.assistant_process = subprocess.Popen([sys.executable, self.script_path])
            self.is_running = True
            self.status_label.config(text="Status: Running")
            self.toggle_button.config(text="Stop Assistant")
            self.canvas.start_animation("listening")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.canvas.start_animation("error")
    
    def stop_assistant(self):
        if self.assistant_process:
            # Find and terminate all Python processes running the assistant script
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and self.script_path in ' '.join(proc.info['cmdline']):
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            self.assistant_process = None
            self.is_running = False
            self.status_label.config(text="Status: Stopped")
            self.toggle_button.config(text="Start Assistant")
            self.canvas.start_animation("idle")
    
    def monitor_assistant(self):
        while True:
            if self.is_running and self.assistant_process:
                if self.assistant_process.poll() is not None:
                    # Process has ended
                    self.is_running = False
                    self.assistant_process = None
                    self.status_label.config(text="Status: Stopped")
                    self.toggle_button.config(text="Start Assistant")
                    self.canvas.start_animation("idle")
            time.sleep(1)
    
    def minimize_to_tray(self):
        self.root.withdraw()  # Hide the window
    
    def exit_app(self):
        self.stop_assistant()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TrinGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 