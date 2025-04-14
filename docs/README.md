# Trin Assistant

A modern, feminine AI assistant with voice recognition and system control capabilities. Trin Assistant features a beautiful pink-themed interface and powerful functionality for managing your computer and media.

## Installation

### Method 1: Using the Installer (Recommended)
1. Contact me on Discord at `afroteddy` to get the latest installer
2. Run the installer and follow the on-screen instructions
3. Choose whether to create desktop and startup shortcuts
4. The installer will automatically set up all required dependencies and configurations

### Method 2: Manual Installation (Alternative)
If you prefer manual installation or want to contribute to development:

1. Clone the repository:
```bash
git clone https://github.com/AfroTeddy12/trin-assistant.git
cd trin-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the Vosk model:
```bash
# Create models directory if it doesn't exist
mkdir models
# Download and extract the model
# Windows:
curl -L https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -o vosk-model-small-en-us-0.15.zip
powershell Expand-Archive vosk-model-small-en-us-0.15.zip -DestinationPath models
# Linux/Mac:
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models
```

5. Configure Spotify (optional):
   - Copy `config/spotify_config.json.example` to `config/spotify_config.json`
   - Add your Spotify API credentials

## Features

- Voice command recognition
- System monitoring and control
- Spotify integration
- Weather information
- News updates
- Web search
- File management
- Application control
- Beautiful pink-themed GUI

## Usage

1. Launch Trin Assistant using the desktop shortcut or from the Start menu
2. Click "Start Assistant" to begin
3. Use voice commands to interact with the assistant
4. Common commands:
   - "Hello Trin" - Wake up the assistant
   - "What's the weather?" - Get weather information
   - "Play Spotify" - Control Spotify playback
   - "System status" - Check system information
   - "Goodbye" - Put the assistant to sleep

## Directory Structure

```
trin-assistant/
├── src/                    # Source code
│   ├── trin_assistant.py   # Main assistant logic
│   ├── trin_gui.py         # GUI implementation
│   ├── launch_trin.pyw     # Windows launcher
│   └── create_shortcut.py  # Shortcut creator
├── docs/                   # Documentation
│   ├── README.md
│   └── COMMANDS.md
├── config/                 # Configuration files
│   └── spotify_config.json
├── models/                 # AI models
│   └── vosk-model-small-en-us-0.15
└── scripts/                # Utility scripts
    └── start_trin.bat
```

## Requirements

- Python 3.8 or higher
- Windows 10 or higher
- Microphone
- Internet connection (for some features)

## Dependencies

See `requirements.txt` for a complete list of dependencies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support or to get the installer:
- Discord: `afroteddy`
- GitHub Issues: [Create an issue](https://github.com/AfroTeddy12/trin-assistant/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for speech recognition
- [Spotify](https://developer.spotify.com/) for music integration
- [OpenWeatherMap](https://openweathermap.org/) for weather data
