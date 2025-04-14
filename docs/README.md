# Trin Assistant

A voice-controlled personal assistant with JARVIS-like capabilities.

## Directory Structure

```
trin-assistant/
├── src/                    # Source code files
│   ├── trin_assistant.py   # Main assistant implementation
│   ├── trin_gui.py         # GUI components
│   ├── lil_trin.py         # Core functionality
│   ├── launch_trin.pyw     # Launcher script
│   └── test_window.py      # GUI testing
├── docs/                   # Documentation
│   ├── README.md          # Project documentation
│   └── COMMANDS.md        # Command reference
├── config/                 # Configuration files
│   └── spotify_config.json # Spotify API configuration
├── models/                 # AI models
│   └── vosk-model-small-en-us-0.15/  # Speech recognition model
└── scripts/               # Utility scripts
    ├── start_trin.bat     # Windows startup script
    └── Trin Assistant.lnk # Windows shortcut
```

## Features

- Voice command recognition
- System monitoring and control
- Weather information
- News updates
- Web search
- File organization
- Spotify integration
- Application control
- System maintenance

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AfroTeddy12/trin-assistant.git
   cd trin-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Spotify (optional):
   - Copy `config/spotify_config.json.example` to `config/spotify_config.json`
   - Add your Spotify API credentials

## Usage

1. Start the assistant:
   ```bash
   python src/launch_trin.pyw
   ```

2. Say "hello trin" or "hello trinity" to wake up the assistant
3. Use voice commands to interact with the assistant
4. Say "goodbye" to put the assistant to sleep

For a complete list of commands, see [COMMANDS.md](docs/COMMANDS.md).

## Requirements

- Python 3.10 or higher
- Windows 10 or higher
- Microphone
- Internet connection (for some features)

## Dependencies

See [requirements.txt](requirements.txt) for a complete list of dependencies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
