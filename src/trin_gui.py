import tkinter as tk
from tkinter import ttk, messagebox
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
        super().__init__(parent, width=width, height=height, bg='#FFF0F5', highlightthickness=0)
        self.width = width
        self.height = height
        self.current_state = "idle"
        self.after_id = None
        self.animation_speed = 100  # milliseconds between frames
        self.last_frame_time = 0
        self.start_animation("idle")

    def start_animation(self, state):
        """Start or change the animation state"""
        self.current_state = state
        if self.after_id:
            self.after_cancel(self.after_id)
        self._animate()

    def stop_animation(self):
        """Stop the animation"""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.delete("all")

    def _animate(self):
        """Animate the canvas using Tkinter's after method"""
        current_time = time.time()
        if current_time - self.last_frame_time < self.animation_speed / 1000:
            self.after_id = self.after(10, self._animate)
            return
            
        self.last_frame_time = current_time
        self.delete("all")
        
        try:
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
        except Exception as e:
            print(f"Error in animation drawing: {str(e)}")
            self.current_state = "error"
        
        self.after_id = self.after(self.animation_speed, self._animate)

    def _draw_idle(self):
        """Draw idle animation"""
        center_x, center_y = self.width/2, self.height/2
        radius = 20
        self.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline='#FF69B4', width=2
        )

    def _draw_listening(self):
        """Draw listening animation"""
        center_x, center_y = self.width/2, self.height/2
        radius = 15 + math.sin(time.time() * 2) * 5
        self.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline='#FF1493', width=2
        )

    def _draw_processing(self):
        """Draw processing animation"""
        center_x, center_y = self.width/2, self.height/2
        angle = time.time() * 2
        for i in range(4):
            x = center_x + math.cos(angle + i * math.pi/2) * 15
            y = center_y + math.sin(angle + i * math.pi/2) * 15
            self.create_oval(x-3, y-3, x+3, y+3, fill='#FFB6C1')

    def _draw_wave(self):
        """Draw wave animation"""
        points = []
        for x in range(0, self.width + 1, 10):
            y = self.height/2 + math.sin(x/20 + time.time()) * 15
            points.extend([x, y])
        self.create_line(points, fill='#FF69B4', width=2, smooth=True)

    def _draw_error(self):
        """Draw error animation"""
        center_x, center_y = self.width/2, self.height/2
        self.create_line(
            center_x - 15, center_y - 15,
            center_x + 15, center_y + 15,
            fill='#FF1493', width=3
        )
        self.create_line(
            center_x - 15, center_y + 15,
            center_x + 15, center_y - 15,
            fill='#FF1493', width=3
        )

class TrinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trin Assistant")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # Set theme colors
        self.PRIMARY_COLOR = "#FF69B4"  # Hot Pink
        self.SECONDARY_COLOR = "#FFB6C1"  # Light Pink
        self.ACCENT_COLOR = "#FF1493"  # Deep Pink
        self.BACKGROUND_COLOR = "#FFF0F5"  # Lavender Blush
        self.TEXT_COLOR = "#4B0082"  # Indigo
        
        # Configure root window background
        self.root.configure(bg=self.BACKGROUND_COLOR)
        
        # Create main frame with pink background
        self.main_frame = tk.Frame(root, bg=self.BACKGROUND_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header with gradient
        self.header_frame = tk.Frame(self.main_frame, bg=self.PRIMARY_COLOR)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add title with custom font
        self.title_label = tk.Label(self.header_frame,
                                  text="Trin Assistant",
                                  font=("Helvetica", 24, "bold"),
                                  bg=self.PRIMARY_COLOR,
                                  fg="white")
        self.title_label.pack(pady=10)
        
        # Create status frame
        self.status_frame = tk.Frame(self.main_frame, bg=self.BACKGROUND_COLOR)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status label with custom styling
        self.status_label = tk.Label(self.status_frame,
                                   text="Status: Ready",
                                   font=("Helvetica", 12),
                                   bg=self.BACKGROUND_COLOR,
                                   fg=self.TEXT_COLOR)
        self.status_label.pack(side=tk.LEFT)
        
        # Create animation canvas with pink border
        self.canvas_frame = tk.Frame(self.main_frame, bg=self.BACKGROUND_COLOR)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = AnimatedCanvas(self.canvas_frame,
                                   width=360,
                                   height=150)
        self.canvas.pack(pady=10)
        
        # Create button frame with custom styling
        self.button_frame = tk.Frame(self.main_frame, bg=self.BACKGROUND_COLOR)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start button with custom styling
        self.start_button = tk.Button(self.button_frame,
                                    text="Start Assistant",
                                    command=self.start_assistant,
                                    bg=self.PRIMARY_COLOR,
                                    fg="white",
                                    font=("Helvetica", 12, "bold"),
                                    relief=tk.RAISED,
                                    borderwidth=2,
                                    padx=20,
                                    pady=10,
                                    activebackground=self.ACCENT_COLOR,
                                    activeforeground="white")
        self.start_button.pack(pady=5)
        
        # Exit button with custom styling
        self.exit_button = tk.Button(self.button_frame,
                                   text="Exit",
                                   command=self.exit_app,
                                   bg=self.SECONDARY_COLOR,
                                   fg=self.TEXT_COLOR,
                                   font=("Helvetica", 10),
                                   relief=tk.RAISED,
                                   borderwidth=2,
                                   padx=20,
                                   pady=5,
                                   activebackground=self.ACCENT_COLOR,
                                   activeforeground="white")
        self.exit_button.pack(pady=5)
        
        # Add decorative elements
        self.add_decorative_elements()
        
        # Set process name
        set_process_name("Trin Assistant")
        
        # Initialize variables
        self.assistant_process = None
        self.is_running = False
        self.script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trin_assistant.py")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_assistant, daemon=True)
        self.monitor_thread.start()
        
        # Start with idle animation
        self.canvas.start_animation("idle")
        
        # Prevent window from closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def add_decorative_elements(self):
        # Add decorative hearts
        heart_symbol = "❤"
        for i in range(5):
            heart = tk.Label(self.main_frame,
                           text=heart_symbol,
                           font=("Arial", 12),
                           bg=self.BACKGROUND_COLOR,
                           fg=self.PRIMARY_COLOR)
            heart.place(x=10 + i*20, y=10)
            
        # Add decorative border
        border_frame = tk.Frame(self.main_frame,
                              bg=self.PRIMARY_COLOR,
                              height=2)
        border_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def start_assistant(self):
        # Update button appearance
        self.start_button.config(text="Stop Assistant",
                               bg=self.ACCENT_COLOR,
                               command=self.stop_assistant)
        self.status_label.config(text="Status: Running")
        
    def stop_assistant(self):
        # Update button appearance
        self.start_button.config(text="Start Assistant",
                               bg=self.PRIMARY_COLOR,
                               command=self.start_assistant)
        self.status_label.config(text="Status: Stopped")
        
    def monitor_assistant(self):
        while True:
            if self.is_running and self.assistant_process:
                if self.assistant_process.poll() is not None:
                    # Process has ended
                    self.is_running = False
                    self.assistant_process = None
                    self.status_label.config(text="Status: Stopped")
                    self.start_button.config(text="Start Assistant")
                    self.canvas.start_animation("idle")
            time.sleep(1)
    
    def exit_app(self):
        if messagebox.askokcancel("Exit", "Do you want to exit Trin Assistant?"):
            self.stop_assistant()
            self.root.destroy()
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_assistant()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TrinGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 