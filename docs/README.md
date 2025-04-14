# Trin Assistant

A voice-controlled personal assistant with a modern, feminine aesthetic. Trin Assistant can help you with various tasks including system control, media playback, weather information, news updates, and file management.

## Features

- 🎤 Voice command recognition
- 💖 Modern pink-themed GUI
- 🎵 Spotify integration
- 🌤️ Weather information
- 📰 News updates
- 📂 File management
- 🔒 Secure configuration management
- 🚀 Easy Windows integration

## Directory Structure

```
trin-assistant/
├── src/                    # Source code
│   ├── trin_assistant.py   # Main assistant implementation
│   ├── trin_gui.py         # GUI implementation
│   ├── launch_trin.pyw     # Windows launcher
│   ├── create_shortcut.py  # Shortcut creator
│   └── config_manager.py   # Secure configuration manager
├── docs/                   # Documentation
│   ├── README.md          # This file
│   └── COMMANDS.md        # Command reference
├── config/                 # Configuration files
│   └── spotify_config.json # Spotify API configuration
├── models/                 # AI models
│   └── vosk-model-small-en-us-0.15/ # Speech recognition model
└── scripts/               # Utility scripts
    └── start_trin.bat     # Batch file for starting the assistant
```

## Installation

### Prerequisites

- Windows 10 or higher
- Python 3.10 or higher
- Microphone
- Internet connection

### Setup

1. Clone the repository:
```bash
git clone https://github.com/AfroTeddy12/trin-assistant.git
cd trin-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install cryptography pywin32 winshell
```

3. Download required models:
```bash
# Download Vosk model
python -m vosk_model_downloader vosk-model-small-en-us-0.15
```

4. Create shortcuts (run once):
```bash
python src/create_shortcut.py
```

## Configuration

### Secure Configuration System

Trin Assistant uses a secure configuration system to store sensitive data:

- API keys and credentials are encrypted using Fernet encryption
- Configuration is stored in your home directory under `.trin_assistant`
- Automatic key generation and management
- Secure storage of Spotify and weather API credentials

### Initial Setup

1. Run the assistant for the first time
2. Enter your API credentials when prompted:
   - Spotify API credentials
   - Weather API key
3. Credentials are automatically encrypted and stored securely

## Usage

### Starting the Assistant

You can start Trin Assistant in several ways:

1. Double-click the desktop shortcut
2. Run `python src/launch_trin.pyw`
3. The assistant starts automatically with Windows

### Voice Commands

Trin Assistant responds to various voice commands:

#### Basic Commands
- "Hello Trin" - Wake up the assistant
- "Goodbye" - Put the assistant to sleep
- "Exit" - Close the assistant

#### System Information
- "What's the system status" - Get system information
- "What time is it" - Get current time
- "What day is it" - Get current day
- "What's the date" - Get current date

#### Weather Information
- "What's the weather" - Get weather for current location
- "What's the weather in [city], [country]" - Get weather for specific location

#### News Updates
- "Get me the news" - Get general news
- "Get me tech news" - Get technology news
- "Get me business news" - Get business news
- "Get me sports news" - Get sports news

#### Web Search
- "Search for [query]" - Perform a web search

#### File Management
- "Organize my files" - Organize files in Downloads folder
- "Organize files in [directory]" - Organize files in specified directory

#### Application Control
- "Open [application]" - Open an application
- "Close [application]" - Close an application
- "Kill [application]" - Force close an application

#### Spotify Control
- "Open Spotify" - Launch Spotify
- "Play Spotify" - Start playback
- "Pause Spotify" - Pause playback
- "Next track" - Skip to next track
- "Previous track" - Go to previous track
- "Play playlist [name]" - Play specific playlist

#### System Control
- "Shutdown computer" - Shutdown the system
- "Restart computer" - Restart the system
- "Cancel shutdown" - Cancel pending shutdown

## Troubleshooting

### Common Issues

1. **Microphone Not Working**
   - Check if microphone is properly connected
   - Ensure microphone permissions are granted
   - Try selecting a different microphone in system settings

2. **Speech Recognition Issues**
   - Check internet connection
   - Ensure clear audio input
   - Try speaking closer to the microphone

3. **Spotify Integration**
   - Verify Spotify credentials in secure config
   - Ensure Spotify is installed and running
   - Check internet connection

4. **Weather Information**
   - Verify weather API key in secure config
   - Check internet connection
   - Ensure location services are enabled

### Debug Mode

Run the assistant with debug mode for detailed information:
```bash
python src/trin_assistant.py --debug
```

## Development

### Setting Up Development Environment

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
pip install cryptography pywin32 winshell
```

### Running Tests

```bash
python -m unittest discover tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for speech recognition
- [Spotify](https://developer.spotify.com/) for music integration
- [OpenWeatherMap](https://openweathermap.org/) for weather data
