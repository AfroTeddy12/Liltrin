# Trin Assistant

A voice-controlled personal assistant with JARVIS-like capabilities, inspired by Iron Man's JARVIS. This assistant can help you with various tasks including system control, media playback, web searches, and file management.

![Trin Assistant](docs/images/trin-assistant.png)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Requirements](#requirements)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🎤 Voice Command Recognition
  - Natural language processing
  - Wake word detection
  - Multiple command support

- 💻 System Control
  - System status monitoring
  - Application management
  - System maintenance
  - Shutdown/restart control

- 🌦️ Weather Information
  - Current weather
  - Location-based weather
  - Detailed weather reports

- 📰 News Updates
  - General news
  - Technology news
  - Business news
  - Sports news

- 🔍 Web Search
  - Quick web searches
  - Voice-activated search
  - Search history

- 📁 File Management
  - File organization
  - Automatic categorization
  - File type detection

- 🎵 Spotify Integration
  - Play/pause control
  - Playlist management
  - Volume control
  - Track navigation

## Installation

### Prerequisites
- Windows 10 or higher
- Python 3.10 or higher
- Working microphone
- Internet connection

### Step 1: Clone the Repository
```bash
git clone https://github.com/AfroTeddy12/trin-assistant.git
cd trin-assistant
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download Required Models
1. Download the Vosk speech recognition model:
   ```bash
   mkdir models
   cd models
   curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   cd ..
   ```

### Step 4: Configure API Keys
1. Create a `config` directory if it doesn't exist:
   ```bash
   mkdir config
   ```

2. Set up Spotify (optional):
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Copy the client ID and client secret
   - Create `config/spotify_config.json`:
   ```json
   {
     "client_id": "your_client_id",
     "client_secret": "your_client_secret",
     "redirect_uri": "http://127.0.0.1:8000/callback"
   }
   ```

3. Set up Weather API (optional):
   - Go to [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free API key
   - Create `config/weather_config.json`:
   ```json
   {
     "api_key": "your_api_key"
   }
   ```

## Setup

### Windows Setup
1. Create a desktop shortcut:
   ```bash
   copy scripts\Trin Assistant.lnk "%USERPROFILE%\Desktop\"
   ```

2. Add to startup (optional):
   ```bash
   copy scripts\start_trin.bat "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
   ```

### First Run
1. Start the assistant:
   ```bash
   python src/launch_trin.pyw
   ```

2. Test your microphone:
   - Say "hello trin" or "hello trinity"
   - The assistant should respond with a greeting
   - If not, check your microphone settings

## Usage

### Basic Commands
- Wake up: "hello trin" or "hello trinity"
- Put to sleep: "goodbye"
- Exit: "exit" or "quit"

### System Commands
- "what's the system status"
- "what time is it"
- "what day is it"
- "what's today's date"
- "perform maintenance"

### Media Commands
- "open spotify"
- "spotify play"
- "spotify pause"
- "spotify next"
- "spotify previous"
- "spotify volume up"
- "spotify volume down"
- "spotify mute"

### Weather Commands
- "what's the weather"
- "what's the weather in [city]"
- "what's the weather in [city], [country]"

### News Commands
- "get news"
- "get technology news"
- "get business news"
- "get sports news"

### File Management
- "organize files"
- "organize files in [directory]"

For a complete list of commands, see [COMMANDS.md](docs/COMMANDS.md).

## Configuration

### Customizing Voice
Edit `src/trin_assistant.py` to change voice settings:
```python
self.engine.setProperty('rate', 150)  # Speech rate (words per minute)
self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
```

### Adding Custom Commands
1. Open `src/trin_assistant.py`
2. Add your command to the `process_command` method
3. Create a new method for the command functionality

## Requirements

### Hardware
- Windows 10 or higher
- Microphone
- Speakers
- Internet connection

### Software
- Python 3.10 or higher
- Git
- pip package manager

## Dependencies

See [requirements.txt](requirements.txt) for a complete list of dependencies.

## Troubleshooting

### Common Issues

1. **Microphone not working**
   - Check Windows sound settings
   - Ensure microphone is set as default device
   - Test microphone in Windows settings

2. **Speech recognition issues**
   - Check internet connection
   - Ensure Vosk model is properly installed
   - Try speaking more clearly

3. **Spotify integration not working**
   - Verify API credentials
   - Check Spotify app is installed
   - Ensure you're logged into Spotify

4. **Weather information not available**
   - Verify API key
   - Check internet connection
   - Ensure location services are enabled

### Debug Mode
Run the assistant with debug mode for more information:
```bash
python src/launch_trin.pyw --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Check code style
flake8
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for speech recognition
- [Spotify](https://developer.spotify.com/) for music integration
- [OpenWeatherMap](https://openweathermap.org/) for weather data
