import pyttsx3
import os
import sys
import webbrowser
import pyautogui
import pywhatkit
import psutil
import datetime
from pathlib import Path
import sounddevice as sd
import numpy as np
import queue
import json
from vosk import Model, KaldiRecognizer
import winreg
import glob
import subprocess

class LilTrin:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        # Initialize Vosk model
        model_path = "vosk-model-small-en-us-0.15"
        if not os.path.exists(model_path):
            print("Please download and extract the Vosk model to the project directory")
            print("Download from: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
            sys.exit(1)
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()
        self.is_awake = False
        
        # Print available audio devices
        print("\nAvailable audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"{i}: {device['name']}")
        
        # Set default input device
        try:
            sd.default.device = sd.default.device[0], sd.default.device[1]
            print(f"\nUsing input device: {sd.query_devices(sd.default.device[0])['name']}")
        except Exception as e:
            print(f"Error setting audio device: {str(e)}")
            print("Trying to use default device...")
        
    def setup_voice(self):
        """Configure voice settings"""
        voices = self.engine.getProperty('voices')
        # Set a female voice if available
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 150)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Trin: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def find_shortcut(self, app_name):
        """Search for shortcuts in taskbar, desktop, and start menu"""
        app_name = app_name.lower()
        found_paths = []
        
        # Search desktop
        desktop = str(Path.home() / "Desktop")
        for shortcut in glob.glob(os.path.join(desktop, "*.lnk")):
            if app_name in os.path.splitext(os.path.basename(shortcut))[0].lower():
                found_paths.append(shortcut)
        
        # Search start menu
        start_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        for root, _, files in os.walk(start_menu):
            for file in files:
                if file.endswith('.lnk') and app_name in file.lower():
                    found_paths.append(os.path.join(root, file))
        
        # Search taskbar (pinned items)
        taskbar_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Internet Explorer', 'Quick Launch', 'User Pinned', 'TaskBar')
        if os.path.exists(taskbar_path):
            for shortcut in glob.glob(os.path.join(taskbar_path, "*.lnk")):
                if app_name in os.path.splitext(os.path.basename(shortcut))[0].lower():
                    found_paths.append(shortcut)
        
        return found_paths
    
    def open_application(self, app_name):
        """Try to open an application using various methods"""
        # First try direct execution
        try:
            os.startfile(app_name)
            return True
        except:
            pass
        
        # Then try with .exe extension
        try:
            os.startfile(app_name + ".exe")
            return True
        except:
            pass
        
        # Search for shortcuts
        shortcuts = self.find_shortcut(app_name)
        if shortcuts:
            try:
                os.startfile(shortcuts[0])  # Open the first matching shortcut
                return True
            except:
                pass
        
        return False
    
    def close_application(self, app_name):
        """Close an application by name or window title"""
        app_name = app_name.lower()
        closed = False
        
        # Try to find and close by process name
        for proc in psutil.process_iter(['name']):
            try:
                if app_name in proc.info['name'].lower():
                    proc.terminate()
                    closed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # If not found by process name, try to find by window title
        if not closed:
            try:
                # Use taskkill to close by window title
                subprocess.run(['taskkill', '/F', '/FI', f'WINDOWTITLE eq *{app_name}*'], 
                             capture_output=True, text=True)
                closed = True
            except:
                pass
        
        return closed
    
    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def listen(self):
        """Listen for voice commands using Vosk"""
        try:
            if not self.is_awake:
                print("\nWaiting for wake word 'hello trin' or 'hello trinity'...")
            else:
                print("\nListening for commands... (Press Ctrl+C to stop)")
            
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                 channels=1, callback=self.audio_callback):
                while True:
                    try:
                        data = self.audio_queue.get(timeout=1)
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            text = result.get("text", "").strip()
                            if text:
                                print(f"Recognized: {text}")
                                
                                # Check for wake word if not awake
                                if not self.is_awake:
                                    if "hello trin" in text.lower() or "hello trinity" in text.lower():
                                        self.is_awake = True
                                        self.speak("Hello! How can I help you?")
                                        print("\nAvailable commands:")
                                        print("- 'open [application]' or 'launch [application]' - Open an application")
                                        print("- 'kill [application]' or 'remove [application]' - Close an application")
                                        print("- 'search for [query]' - Search the web")
                                        print("- 'play [song]' - Play a song on YouTube")
                                        print("- 'time' - Get current time")
                                        print("- 'list files' - Show files in Documents folder")
                                        print("- 'goodbye' - Exit the assistant")
                                        continue
                                
                                # If awake, process commands
                                if self.is_awake:
                                    if "goodbye" in text.lower():
                                        self.is_awake = False
                                        self.speak("Goodbye! Say 'hello trin' or 'hello trinity' when you need me again.")
                                        continue
                                    return text.lower()
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"Error processing audio: {str(e)}")
                        continue
        except KeyboardInterrupt:
            print("\nStopping listening...")
            return "exit"
        except Exception as e:
            print(f"Error in listen: {str(e)}")
            return "Error occurred"
    
    def process_command(self, command):
        """Process voice commands"""
        if "shutdown" in command or "turn off" in command:
            self.speak("Shutting down the computer")
            os.system("shutdown /s /t 60")
            
        elif "restart" in command:
            self.speak("Restarting the computer")
            os.system("shutdown /r /t 60")
            
        elif "cancel shutdown" in command:
            self.speak("Canceling shutdown")
            os.system("shutdown /a")
            
        elif "open" in command or "launch" in command:
            app = command.replace("open", "").replace("launch", "").strip()
            self.speak(f"Opening {app}")
            if not self.open_application(app):
                self.speak(f"Sorry, I couldn't find {app}")
                
        elif "kill" in command or "remove" in command:
            app = command.replace("kill", "").replace("remove", "").strip()
            self.speak(f"Closing {app}")
            if not self.close_application(app):
                self.speak(f"Sorry, I couldn't find {app} to close")
                
        elif "search for" in command:
            query = command.replace("search for", "").strip()
            self.speak(f"Searching for {query}")
            pywhatkit.search(query)
            
        elif "play" in command:
            song = command.replace("play", "").strip()
            self.speak(f"Playing {song}")
            pywhatkit.playonyt(song)
            
        elif "time" in command:
            time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"Current time is {time}")
            
        elif "list files" in command or "show files" in command:
            path = str(Path.home() / "Documents")  # Default to Documents folder
            files = os.listdir(path)
            self.speak("Here are the files:")
            for file in files[:5]:  # List first 5 files to avoid too long response
                self.speak(file)
            
        else:
            self.speak("I'm not sure how to help with that")

    def run(self):
        """Main loop for the assistant"""
        print("Trin is ready! Say 'hello trin' or 'hello trinity' to start.")
        print("\nAvailable commands:")
        print("- 'open [application]' or 'launch [application]' - Open an application")
        print("- 'kill [application]' or 'remove [application]' - Close an application")
        print("- 'search for [query]' - Search the web")
        print("- 'play [song]' - Play a song on YouTube")
        print("- 'time' - Get current time")
        print("- 'list files' - Show files in Documents folder")
        print("- 'goodbye' - Exit the assistant")
        while True:
            command = self.listen()
            if command and command != "Error occurred":
                self.process_command(command)

if __name__ == "__main__":
    assistant = LilTrin()
    assistant.run() 