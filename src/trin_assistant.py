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
import pyttsx3
import webbrowser
import pyautogui
import pywhatkit
import datetime
import traceback
import pyaudio
import wave
import speech_recognition as sr
import win32gui
import win32api
import win32con
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests
import speedtest
import random
import shutil
from bs4 import BeautifulSoup
import tempfile
import winreg
from config_manager import ConfigManager
from trin_gui import TrinGUI

def show_error(title, message):
    """Show error message in a dialog box"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(title, message)
        root.destroy()
    except:
        print(f"Error: {title} - {message}")

class TrinAssistant:
    def __init__(self, root, debug_mode=False):
        try:
            self.debug_mode = debug_mode
            self.config_manager = ConfigManager()
            
            # Load configurations
            self.spotify_config = self.config_manager.get_config('spotify', {})
            self.weather_config = self.config_manager.get_config('weather', {})
            
            if debug_mode:
                print("Debug mode enabled in TrinAssistant")
                print("System information:")
                print("- Platform:", sys.platform)
                print("- Python executable:", sys.executable)
                print("- Tkinter version:", root.tk.call('info', 'patchlevel'))
                print("- Screen resolution:", f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
            
            print("Initializing TrinAssistant...")
            self.root = root
            
            # Initialize GUI
            self.gui = TrinGUI(root)
            
            # Set up error handler for unhandled exceptions
            def handle_exception(exc_type, exc_value, exc_traceback):
                print("Unhandled exception:", exc_type.__name__)
                print("Exception value:", exc_value)
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                try:
                    self.root.destroy()
                except:
                    pass
                sys.exit(1)
            
            sys.excepthook = handle_exception
            
            print("Setting window attributes...")
            # Make window always on top
            self.root.attributes('-topmost', True)
            
            print("Setting process name...")
            # Set process name
            self.set_process_name("Trin Assistant")
            
            print("Initializing voice engine...")
            # Initialize voice engine
            try:
                self.engine = pyttsx3.init()
                self.setup_voice()
            except Exception as e:
                show_error("Voice Engine Error", f"Failed to initialize voice engine: {str(e)}")
                raise
            
            print("Initializing speech recognition...")
            # Initialize speech recognition
            try:
                if debug_mode:
                    print("Checking microphone availability...")
                    print("Available microphones:")
                    for index, name in enumerate(sr.Microphone.list_microphone_names()):
                        print(f"- {index}: {name}")
                
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 300  # Adjust this value based on your microphone
                self.recognizer.pause_threshold = 0.8
                self.is_listening = False
                self.is_awake = False
                
                # Test microphone initialization
                with sr.Microphone() as source:
                    if debug_mode:
                        print("Microphone initialized successfully")
                        print("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    if debug_mode:
                        print("Ambient noise adjustment complete")
                
            except Exception as e:
                error_msg = f"Failed to initialize speech recognition: {str(e)}\n"
                error_msg += "Please ensure you have a working microphone connected and it's not being used by another application."
                show_error("Speech Recognition Error", error_msg)
                raise
            
            print("Initializing Spotify...")
            # Initialize Spotify
            try:
                self.spotify = None
                self.initialize_spotify()
            except Exception as e:
                print(f"Warning: Could not initialize Spotify API: {str(e)}")
                print("Basic media controls will still work")
            
            # Add more natural responses
            self.responses = {
                'greeting': [
                    "Hello! How may I assist you today?",
                    "Good day! What can I do for you?",
                    "At your service! How can I help?",
                    "Hello there! What's on your mind?"
                ],
                'farewell': [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Until next time! Stay safe!",
                    "Goodbye! It was a pleasure assisting you!"
                ],
                'acknowledge': [
                    "I'm on it.",
                    "Right away.",
                    "Consider it done.",
                    "I'll take care of that."
                ],
                'error': [
                    "I apologize, but I'm having trouble with that.",
                    "I'm sorry, I couldn't complete that request.",
                    "I'm afraid I can't do that right now.",
                    "I'm experiencing some difficulties with that."
                ]
            }
            
            # Add configuration for new features
            self.weather_api_key = None
            self.load_configurations()
            
            # Add maintenance schedule
            self.last_maintenance = datetime.datetime.now()
            self.maintenance_interval = datetime.timedelta(days=7)  # Weekly maintenance
            
            # Connect GUI events
            self.gui.start_button.config(command=self.start_assistant)
            self.gui.exit_button.config(command=self.exit_app)
            
            print("TrinAssistant initialization complete")
            
        except Exception as e:
            print(f"Error in initialization: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            raise

    def set_process_name(self, name):
        """Set the process name for better identification in Task Manager"""
        try:
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.SetConsoleTitleW(name)
        except Exception as e:
            print(f"Failed to set process name: {str(e)}")
    
    def setup_voice(self):
        """Configure voice settings"""
        try:
            voices = self.engine.getProperty('voices')
            # Set a female voice if available
            for voice in voices:
                if "female" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            self.engine.setProperty('rate', 150)
        except Exception as e:
            print(f"Failed to setup voice: {str(e)}")
            raise
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"Trin: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Failed to speak: {str(e)}")
    
    def listen(self):
        """Listen for voice commands"""
        try:
            if not self.is_awake:
                print("\nWaiting for wake word 'hello trin' or 'hello trinity'...")
                self.gui.canvas.start_animation("idle")
            else:
                print("\nListening for commands...")
                self.gui.canvas.start_animation("listening")
            
            with sr.Microphone() as source:
                if self.debug_mode:
                    print("Microphone source opened")
                    print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                if self.debug_mode:
                    print("Listening for audio...")
                
                try:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                    
                    if self.debug_mode:
                        print("Audio captured, processing...")
                    
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"Recognized: {text}")
                        self.process_command(text)
                    except sr.UnknownValueError:
                        if self.debug_mode:
                            print("Could not understand audio - no speech detected")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        print("Please check your internet connection")
                    except Exception as e:
                        print(f"Error in speech recognition: {str(e)}")
                        traceback.print_exc()
                
                except sr.WaitTimeoutError:
                    if self.debug_mode:
                        print("No speech detected within timeout period")
                    return
                
        except Exception as e:
            print(f"Error in listen: {str(e)}")
            traceback.print_exc()
            self.gui.canvas.start_animation("error")
            time.sleep(1)  # Prevent tight loop on error

    def close_application(self, app_name):
        """Close an application by name"""
        try:
            if self.debug_mode:
                print(f"Attempting to close application: {app_name}")
            
            # Convert app_name to lowercase for case-insensitive matching
            app_name = app_name.lower()
            
            # Get list of running processes
            for proc in psutil.process_iter(['name']):
                try:
                    # Check if process name contains the app name
                    if app_name in proc.info['name'].lower():
                        if self.debug_mode:
                            print(f"Found process: {proc.info['name']}")
                        proc.terminate()
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if self.debug_mode:
                print(f"No process found matching: {app_name}")
            return False
            
        except Exception as e:
            print(f"Error closing application: {str(e)}")
            traceback.print_exc()
            return False

    def open_application(self, app_name):
        """Open an application by name"""
        try:
            if self.debug_mode:
                print(f"Attempting to open application: {app_name}")
            
            # Convert app_name to lowercase for case-insensitive matching
            app_name = app_name.lower()
            
            # Common application paths
            common_paths = [
                # Start Menu
                os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
                # Desktop
                os.path.join(os.environ['USERPROFILE'], 'Desktop'),
                # Taskbar (Quick Launch)
                os.path.join(os.environ['APPDATA'], 'Microsoft', 'Internet Explorer', 'Quick Launch'),
                # Program Files
                os.environ['PROGRAMFILES'],
                os.environ['PROGRAMFILES(X86)'],
                # Common locations for games
                os.path.join(os.environ['PROGRAMFILES(X86)'], 'Steam', 'steamapps', 'common'),
                os.path.join(os.environ['PROGRAMFILES'], 'Epic Games'),
                os.path.join(os.environ['PROGRAMFILES(X86)'], 'Epic Games'),
                # Spotify specific paths
                os.path.join(os.environ['APPDATA'], 'Spotify'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Spotify'),
            ]
            
            # Common executable extensions
            extensions = ['.exe', '.lnk', '.url']
            
            # Special case for Spotify
            if app_name == "spotify":
                # Try to find Spotify in common locations
                spotify_paths = [
                    os.path.join(os.environ['APPDATA'], 'Spotify', 'Spotify.exe'),
                    os.path.join(os.environ['LOCALAPPDATA'], 'Spotify', 'Spotify.exe'),
                    os.path.join(os.environ['PROGRAMFILES'], 'Spotify', 'Spotify.exe'),
                    os.path.join(os.environ['PROGRAMFILES(X86)'], 'Spotify', 'Spotify.exe'),
                ]
                
                for path in spotify_paths:
                    if os.path.exists(path):
                        if self.debug_mode:
                            print(f"Found Spotify at: {path}")
                        subprocess.Popen([path])
                        return True
                
                # If not found, try to launch from Start Menu
                try:
                    subprocess.Popen(['start', 'spotify:'], shell=True)
                    return True
                except:
                    pass
                
                if self.debug_mode:
                    print("Could not find Spotify executable")
                return False
            
            # Search for the application
            for path in common_paths:
                if not os.path.exists(path):
                    continue
                    
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in extensions):
                            # Check if the file name contains the app name
                            if app_name in file.lower():
                                full_path = os.path.join(root, file)
                                if self.debug_mode:
                                    print(f"Found application: {full_path}")
                                
                                # Handle different file types
                                if file.lower().endswith('.lnk'):
                                    # For shortcuts, we need to resolve the target
                                    try:
                                        import win32com.client
                                        shell = win32com.client.Dispatch("WScript.Shell")
                                        shortcut = shell.CreateShortCut(full_path)
                                        target_path = shortcut.Targetpath
                                        if os.path.exists(target_path):
                                            subprocess.Popen([target_path])
                                            return True
                                    except:
                                        # If win32com fails, try opening the shortcut directly
                                        subprocess.Popen([full_path])
                                        return True
                                else:
                                    # For executables and URLs
                                    subprocess.Popen([full_path])
                                    return True
            
            if self.debug_mode:
                print(f"No application found matching: {app_name}")
            return False
            
        except Exception as e:
            print(f"Error opening application: {str(e)}")
            traceback.print_exc()
            return False

    def initialize_spotify(self):
        """Initialize Spotify API connection"""
        try:
            # Get credentials from secure config
            client_id = self.spotify_config.get('client_id')
            client_secret = self.spotify_config.get('client_secret')
            redirect_uri = self.spotify_config.get('redirect_uri')
            
            if not all([client_id, client_secret, redirect_uri]):
                # Create default config if not exists
                default_config = {
                    'client_id': '78caaa1061d744c88104b2cf9ffc1616',
                    'client_secret': '73d52a36fc5049a5a31b11b95d24fc8b',
                    'redirect_uri': 'http://127.0.0.1:8000/callback'
                }
                self.config_manager.update_config('spotify', default_config)
                self.spotify_config = default_config
                print("Created default Spotify configuration.")
                return
            
            # Initialize Spotify client with secure settings
            self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope='user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-public',
                cache_path=os.path.join(os.path.expanduser("~"), ".trin_assistant", ".spotify_cache"),
                show_dialog=True
            ))
            
            # Test the connection
            self.spotify.current_user()
            
            if self.debug_mode:
                print("Spotify API initialized successfully")
                
        except Exception as e:
            print(f"Error initializing Spotify API: {str(e)}")
            self.spotify = None
            
    def load_configurations(self):
        """Load additional configurations"""
        try:
            # Get weather API key from secure config
            self.weather_api_key = self.weather_config.get('api_key')
            
            if not self.weather_api_key:
                # Create default config if not exists
                default_config = {
                    'api_key': '3abd19d1e099a8d189e6d48ffee0802b'
                }
                self.config_manager.update_config('weather', default_config)
                self.weather_config = default_config
                self.weather_api_key = default_config['api_key']
                print("Created default weather configuration.")
                
        except Exception as e:
            print(f"Error loading configurations: {str(e)}")
            
    def update_configuration(self, service, key, value):
        """Update a configuration value securely"""
        try:
            config = self.config_manager.get_config(service, {})
            config[key] = value
            self.config_manager.update_config(service, config)
            return True
        except Exception as e:
            print(f"Error updating configuration: {str(e)}")
            return False

    def control_spotify(self, action):
        """Control Spotify playback"""
        try:
            if self.debug_mode:
                print(f"Attempting to {action} Spotify")
            
            # Try API first if available
            if self.spotify:
                try:
                    if action == "play":
                        self.spotify.start_playback()
                        self.speak("Playing Spotify")
                    elif action == "pause":
                        self.spotify.pause_playback()
                        self.speak("Pausing Spotify")
                    elif action == "next":
                        self.spotify.next_track()
                        self.speak("Skipping to next track")
                    elif action == "previous":
                        self.spotify.previous_track()
                        self.speak("Playing previous track")
                    elif action == "volume_up":
                        current_volume = self.spotify.current_playback()['device']['volume_percent']
                        new_volume = min(100, current_volume + 10)
                        self.spotify.volume(new_volume)
                        self.speak("Increasing volume")
                    elif action == "volume_down":
                        current_volume = self.spotify.current_playback()['device']['volume_percent']
                        new_volume = max(0, current_volume - 10)
                        self.spotify.volume(new_volume)
                        self.speak("Decreasing volume")
                    elif action == "mute":
                        self.spotify.volume(0)
                        self.speak("Muting volume")
                    elif action.startswith("playlist"):
                        playlist_name = action.split("playlist")[1].strip()
                        results = self.spotify.search(q=playlist_name, type='playlist', limit=1)
                        if results['playlists']['items']:
                            playlist_uri = results['playlists']['items'][0]['uri']
                            self.spotify.start_playback(context_uri=playlist_uri)
                            self.speak(f"Playing playlist {playlist_name}")
                        else:
                            self.speak(f"Could not find playlist {playlist_name}")
                    return True
                except Exception as e:
                    print(f"Spotify API error: {str(e)}")
                    # Fall back to media keys if API fails
            
            # Fall back to media keys
            if action in ["play", "pause", "next", "previous", "volume_up", "volume_down", "mute"]:
                # Spotify window class name
                spotify_class = "Chrome_WidgetWin_0"
                
                # Find Spotify window
                def enum_windows_callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        class_name = win32gui.GetClassName(hwnd)
                        if class_name == spotify_class:
                            extra.append(hwnd)
                    return True
                
                spotify_windows = []
                win32gui.EnumWindows(enum_windows_callback, spotify_windows)
                
                if not spotify_windows:
                    self.speak("Spotify is not running")
                    return False
                
                # Get the main Spotify window
                spotify_hwnd = spotify_windows[0]
                
                # Send appropriate key based on action
                if action == "play" or action == "pause":
                    win32api.keybd_event(0xB3, 0, 0, 0)  # VK_MEDIA_PLAY_PAUSE
                    win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
                    self.speak("Playing Spotify" if action == "play" else "Pausing Spotify")
                elif action == "next":
                    win32api.keybd_event(0xB0, 0, 0, 0)  # VK_MEDIA_NEXT_TRACK
                    win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)
                    self.speak("Skipping to next track")
                elif action == "previous":
                    win32api.keybd_event(0xB1, 0, 0, 0)  # VK_MEDIA_PREV_TRACK
                    win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)
                    self.speak("Playing previous track")
                elif action == "volume_up":
                    win32api.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
                    win32api.keybd_event(0xAF, 0, win32con.KEYEVENTF_KEYUP, 0)
                    self.speak("Increasing volume")
                elif action == "volume_down":
                    win32api.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
                    win32api.keybd_event(0xAE, 0, win32con.KEYEVENTF_KEYUP, 0)
                    self.speak("Decreasing volume")
                elif action == "mute":
                    win32api.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
                    win32api.keybd_event(0xAD, 0, win32con.KEYEVENTF_KEYUP, 0)
                    self.speak("Muting volume")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error controlling Spotify: {str(e)}")
            traceback.print_exc()
            self.speak("Sorry, I couldn't control Spotify")
            return False

    def get_random_response(self, category):
        """Get a random response from the specified category"""
        return random.choice(self.responses.get(category, ["I'm not sure what to say."]))

    def system_status(self):
        """Get system status information"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network speed
            st = speedtest.Speedtest()
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            
            status_message = (
                f"System status: CPU usage is {cpu_percent}%, "
                f"memory usage is {memory_percent}%, "
                f"disk usage is {disk_percent}%, "
                f"and download speed is {download_speed:.2f} Mbps."
            )
            self.speak(status_message)
        except Exception as e:
            print(f"Error getting system status: {str(e)}")
            self.speak("I'm having trouble getting the system status.")

    def get_weather(self, location=None):
        """Get current weather information"""
        try:
            if not self.weather_api_key or self.weather_api_key == 'YOUR_WEATHER_API_KEY':
                self.speak("I need a weather API key to provide weather information.")
                return
            
            if not location:
                # Try to get location from IP
                response = requests.get('http://ip-api.com/json')
                if response.status_code == 200:
                    data = response.json()
                    location = f"{data['city']}, {data['country']}"
                else:
                    location = "New York"  # Default location
            
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                
                weather_message = (
                    f"The current temperature in {location} is {temp} degrees Celsius with {description}. "
                    f"Humidity is {humidity}% and wind speed is {wind_speed} meters per second."
                )
                self.speak(weather_message)
            else:
                self.speak("I couldn't retrieve the weather information.")
        except Exception as e:
            print(f"Error getting weather: {str(e)}")
            self.speak("I'm having trouble getting the weather information.")

    def get_news(self, category="general"):
        """Get latest news headlines"""
        try:
            categories = {
                "general": "https://news.google.com/rss",
                "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
                "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
                "sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB"
            }
            
            url = categories.get(category.lower(), categories["general"])
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:5]  # Get top 5 headlines
            
            self.speak(f"Here are the latest {category} headlines:")
            for item in items:
                self.speak(item.title.text)
        except Exception as e:
            print(f"Error getting news: {str(e)}")
            self.speak("I'm having trouble getting the news.")

    def web_search(self, query):
        """Perform a web search"""
        try:
            self.speak(f"Searching for {query}")
            pywhatkit.search(query)
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            self.speak("I'm having trouble performing the web search.")

    def organize_files(self, directory=None):
        """Organize files in a directory"""
        try:
            if not directory:
                directory = str(Path.home() / "Downloads")  # Default to Downloads folder
            
            if not os.path.exists(directory):
                self.speak(f"The directory {directory} does not exist.")
                return
            
            # Create folders for different file types
            folders = {
                'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
                'Videos': ['.mp4', '.avi', '.mov', '.wmv'],
                'Music': ['.mp3', '.wav', '.flac', '.m4a'],
                'Archives': ['.zip', '.rar', '.7z', '.tar'],
                'Programs': ['.exe', '.msi', '.bat']
            }
            
            # Create folders if they don't exist
            for folder in folders:
                folder_path = os.path.join(directory, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            
            # Move files to appropriate folders
            moved_files = 0
            for file in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, file)):
                    file_ext = os.path.splitext(file)[1].lower()
                    for folder, extensions in folders.items():
                        if file_ext in extensions:
                            src = os.path.join(directory, file)
                            dst = os.path.join(directory, folder, file)
                            shutil.move(src, dst)
                            moved_files += 1
                            break
            
            self.speak(f"I've organized {moved_files} files in the {directory} directory.")
        except Exception as e:
            print(f"Error organizing files: {str(e)}")
            self.speak("I'm having trouble organizing the files.")

    def perform_maintenance(self):
        """Perform system maintenance tasks"""
        try:
            current_time = datetime.datetime.now()
            if current_time - self.last_maintenance < self.maintenance_interval:
                self.speak("It's not time for maintenance yet.")
                return
            
            self.speak("Starting system maintenance...")
            
            # Clear temporary files
            temp_dirs = [
                tempfile.gettempdir(),
                os.path.join(os.environ['LOCALAPPDATA'], 'Temp'),
                os.path.join(os.environ['WINDIR'], 'Temp')
            ]
            
            cleared_files = 0
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for file in os.listdir(temp_dir):
                        try:
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                cleared_files += 1
                        except:
                            continue
            
            # Check disk space
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Check for Windows updates
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update")
                last_check = winreg.QueryValueEx(key, "LastCheckForUpdatesTime")[0]
                last_check_time = datetime.datetime.fromtimestamp(last_check)
                if current_time - last_check_time > datetime.timedelta(days=7):
                    self.speak("It's been more than a week since your last Windows update check.")
            except:
                pass
            
            maintenance_message = (
                f"Maintenance complete. I've cleared {cleared_files} temporary files. "
                f"Your disk usage is at {disk_percent}%."
            )
            self.speak(maintenance_message)
            
            self.last_maintenance = current_time
        except Exception as e:
            print(f"Error performing maintenance: {str(e)}")
            self.speak("I'm having trouble performing system maintenance.")

    def process_command(self, command):
        """Process voice commands"""
        try:
            self.gui.canvas.start_animation("processing")
            
            if not self.is_awake:
                if "hello trin" in command or "hello trinity" in command:
                    self.is_awake = True
                    self.speak(self.get_random_response('greeting'))
                    self.gui.canvas.start_animation("responding")
                    return
                return
            
            if "goodbye" in command:
                self.is_awake = False
                self.speak(self.get_random_response('farewell'))
                self.gui.canvas.start_animation("idle")
                return
                
            if "exit" in command or "quit" in command:
                self.speak("Exiting the assistant")
                self.stop_assistant()
                self.root.after(1000, self.root.destroy)  # Give time for the goodbye message
                return
                
            # Add new JARVIS-like commands
            if "system" in command and "status" in command:
                self.system_status()
                return
                
            if "what time" in command:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {current_time}")
                return
                
            if "what day" in command:
                current_day = datetime.datetime.now().strftime("%A")
                self.speak(f"Today is {current_day}")
                return
                
            if "what date" in command:
                current_date = datetime.datetime.now().strftime("%B %d, %Y")
                self.speak(f"Today's date is {current_date}")
                return
                
            if "weather" in command:
                location = None
                if "in" in command:
                    location = command.split("in")[1].strip()
                self.get_weather(location)
                return
                
            if "news" in command:
                category = "general"
                if "tech" in command or "technology" in command:
                    category = "technology"
                elif "business" in command:
                    category = "business"
                elif "sports" in command:
                    category = "sports"
                self.get_news(category)
                return
                
            if "search" in command and "for" in command:
                query = command.split("for")[1].strip()
                self.web_search(query)
                return
                
            if "organize" in command and "files" in command:
                directory = None
                if "in" in command:
                    directory = command.split("in")[1].strip()
                self.organize_files(directory)
                return
                
            if "maintenance" in command or "clean up" in command:
                self.perform_maintenance()
                return
                
            # Spotify controls
            if "spotify" in command or "open spotify" in command or "launch spotify" in command:
                if "open" in command or "launch" in command:
                    # Try to open Spotify
                    if self.open_application("spotify"):
                        self.speak("Opening Spotify")
                        time.sleep(5)  # Wait for Spotify to start
                    else:
                        self.speak("Could not find Spotify. Please make sure it's installed.")
                        return
                
                # Handle Spotify commands
                if "play" in command and "playlist" in command:
                    playlist_name = command.replace("spotify", "").replace("play", "").replace("playlist", "").strip()
                    self.control_spotify(f"playlist {playlist_name}")
                elif "play" in command:
                    self.control_spotify("play")
                elif "pause" in command:
                    self.control_spotify("pause")
                elif "next" in command or "skip" in command:
                    self.control_spotify("next")
                elif "previous" in command or "back" in command:
                    self.control_spotify("previous")
                elif "volume up" in command:
                    self.control_spotify("volume_up")
                elif "volume down" in command:
                    self.control_spotify("volume_down")
                elif "mute" in command:
                    self.control_spotify("mute")
                else:
                    self.speak("What would you like me to do with Spotify?")
                return
                
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
                    
            elif "kill" in command or "remove" in command or "close" in command:
                app = command.replace("kill", "").replace("remove", "").replace("close", "").strip()
                self.speak(f"Closing {app}")
                if not self.close_application(app):
                    self.speak(f"Sorry, I couldn't find {app} to close")
                    
            else:
                self.speak("I'm not sure how to help with that")
            
            self.gui.canvas.start_animation("listening")
        except Exception as e:
            print(f"Error processing command: {str(e)}")
            traceback.print_exc()
            self.gui.canvas.start_animation("error")

    def start_assistant(self):
        """Start the assistant"""
        try:
            print("Starting assistant...")
            self.gui.status_label.config(text="Status: Running")
            self.gui.start_button.config(text="Stop Assistant", command=self.stop_assistant)
            
            # Start listening in a separate thread
            self.is_listening = True
            self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listening_thread.start()
            
            messagebox.showinfo("Assistant", "Assistant is now running!")
        except Exception as e:
            print(f"Error starting assistant: {str(e)}")
            traceback.print_exc()
            self.gui.canvas.start_animation("error")

    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                self.listen()
            except Exception as e:
                print(f"Error in listen loop: {str(e)}")
                traceback.print_exc()
                time.sleep(1)  # Prevent tight loop on error

    def stop_assistant(self):
        """Stop the assistant"""
        try:
            print("Stopping assistant...")
            self.is_listening = False
            
            # Only try to join if we're not in the listening thread
            if (hasattr(self, 'listening_thread') and 
                self.listening_thread and 
                self.listening_thread != threading.current_thread()):
                self.listening_thread.join(timeout=1)
            
            self.gui.status_label.config(text="Status: Stopped")
            self.gui.start_button.config(text="Start Assistant", command=self.start_assistant)
            self.gui.canvas.start_animation("idle")
            messagebox.showinfo("Assistant", "Assistant has been stopped!")
        except Exception as e:
            print(f"Error stopping assistant: {str(e)}")
            traceback.print_exc()
            self.gui.canvas.start_animation("error")

    def exit_app(self):
        """Exit the application"""
        try:
            print("Exiting application...")
            # Stop all threads before destroying
            if hasattr(self, 'listening_thread') and self.listening_thread:
                self.is_listening = False
                self.listening_thread.join(timeout=1)
            self.root.destroy()
        except Exception as e:
            print(f"Error exiting app: {str(e)}")
            traceback.print_exc()
            self.root.destroy()  # Force close if there's an error

def main():
    try:
        # Check for debug mode
        debug_mode = "--debug" in sys.argv
        if debug_mode:
            print("Debug mode enabled")
            print("Command line arguments:", sys.argv)
            print("Environment variables:", dict(os.environ))
            
        print("Starting application...")
        print("Creating root window...")
        root = tk.Tk()
        print("Initializing TrinAssistant...")
        app = TrinAssistant(root, debug_mode)
        print("Entering mainloop...")
        
        # Add error handling around mainloop
        try:
            root.mainloop()
        except Exception as e:
            print(f"Error in mainloop: {str(e)}")
            traceback.print_exc()
            # Try to clean up
            try:
                root.destroy()
            except:
                pass
            raise
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        print("Python version:", sys.version)
        print("Current working directory:", os.getcwd())
        print("Starting main function...")
        main()
    except Exception as e:
        print(f"Unhandled exception in __main__: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 