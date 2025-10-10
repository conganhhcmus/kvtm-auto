# KVTM Auto

**KVTM Auto** is a full-stack Android device automation platform designed for automating mobile games and applications via ADB (Android Debug Bridge). Built with a modern monorepo architecture, it provides a web-based interface for managing multiple devices, executing automation scripts, and monitoring real-time logs.

## Features

- **Multi-Device Management**: Connect and control multiple Android devices simultaneously
- **Web-Based UI**: Modern Next.js interface for managing devices and scripts
- **Live Screen Streaming**: Real-time H.264 video streaming via WebSocket for monitoring device screens
- **Real-Time Logging**: Live log streaming from running automation scripts
- **Image Recognition**: OpenCV-based template matching for visual automation
- **OCR Support**: Text recognition and interaction using Tesseract
- **Script Library**: Extensible script system with shared utilities
- **Process Isolation**: Scripts run as separate processes for stability
- **Auto-Discovery**: Automatic detection and registration of connected devices

## Tech Stack

### Backend
- **Python 3.9+** with Poetry
- **Flask + Flask-SocketIO** - REST API server with WebSocket support
- **adbutils 2.10.2** - Android device control library
- **OpenCV** - Image recognition and matching
- **Tesseract OCR** - Text detection

### Frontend
- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type-safe development
- **TanStack Query** - Data fetching and caching
- **Socket.IO Client** - WebSocket communication
- **JMuxer** - H.264 video playback
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

### Infrastructure
- **Turborepo** - Monorepo build system
- **pnpm** - Fast, disk-efficient package manager
- **PM2** - Production process manager

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** >= 18.0.0
- **pnpm** >= 9.0.0
- **Python** >= 3.9
- **Poetry** - Python dependency management
- **ADB (Android Debug Bridge)** - Included with Android SDK Platform Tools
- **Android Device/Emulator** - With USB debugging enabled

### ADB Setup

1. Download [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Add ADB to your system PATH
3. Verify installation: `adb version`
4. Enable USB debugging on your Android device:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd kvtm-auto
```

### 2. Install Dependencies

```bash
# Install all packages (frontend + backend)
pnpm install

# Install backend dependencies
cd backend
poetry install
cd ..
```

### 3. Verify Device Connection

```bash
# Check connected devices
adb devices

# Expected output:
# List of devices attached
# emulator-5554   device
```

## Quick Start

### Development Mode

Run both frontend and backend in development mode:

```bash
# From project root
pnpm dev
```

This will start:
- **Backend**: `http://localhost:3001` (Flask with Socket.IO and auto-reload)
- **Frontend**: `http://localhost:3000` (Next.js dev server with custom Express proxy)

The frontend automatically proxies `/api` and `/socket.io` requests to the backend.

### Production Mode

```bash
# Build all packages
pnpm build

# Start with PM2
pnpm prod

# View logs
pnpm prod:logs

# Stop services
pnpm prod:stop
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

You should see:
- Connected devices listed
- Available automation scripts
- Control panel for execution

## Project Structure

```
kvtm-auto/
├── backend/                    # Python Flask backend
│   ├── src/
│   │   ├── main.py            # Flask app entry point
│   │   ├── apis/              # API route blueprints
│   │   ├── libs/              # Core libraries (managers, controllers)
│   │   ├── models/            # Data models
│   │   ├── scripts/           # Automation scripts
│   │   ├── assets/            # Image templates for matching
│   │   └── data/              # Runtime data (logs, state)
│   └── pyproject.toml         # Poetry dependencies
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router pages
│   │   ├── components/        # React components
│   │   └── api.ts             # API client
│   └── package.json
├── turbo.json                 # Turborepo configuration
├── package.json               # Root package with scripts
└── CLAUDE.md                  # Detailed technical documentation
```

## Usage

### Managing Devices

The application automatically discovers connected Android devices. Device status includes:
- **Available**: Ready to run scripts
- **Busy**: Currently running a script
- **Offline**: Disconnected

### Running Scripts

1. Select one or more devices from the UI
2. Choose an automation script from the dropdown
3. Configure script options (if available):
   - Open Game
   - Open Chest
   - Sell Items
4. Click "Start" to begin execution
5. Monitor execution via:
   - **View** button - Live H.264 video stream of device screen
   - **Logs** button - Real-time script output logs
   - **Detail** button - Device information and status

### Viewing Logs

- **Real-time logs**: Automatically stream during script execution
- **Log history**: Persisted to `backend/src/data/logs/<device_serial>.log`
- **Clear logs**: Use the "Clear Logs" button in device details

### Live Screen Monitoring

Click the **View** button on any running device to:
- Stream live H.264 video of the device screen
- Monitor automation in real-time
- Low latency streaming via WebSocket (2.5 Mbps)

## Writing Custom Scripts

### Basic Script Template

Create a new file in `backend/src/scripts/`:

```python
import json
import sys
import os

# Add backend/src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.adb_controller import AdbController
from models.game_options import GameOptions
from scripts.core import open_game, plant_tree, harvest_tree

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <device_id> [game_options_json]")
        sys.exit(1)

    device_id = sys.argv[1]
    game_options = GameOptions()

    # Parse game options
    if len(sys.argv) > 2:
        try:
            options_dict = json.loads(sys.argv[2])
            game_options = GameOptions.from_dict(options_dict)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for game_options")
            sys.exit(1)

    # Initialize ADB controller
    manager = AdbController(device_id)

    # Open game if requested
    if game_options.open_game:
        open_game(manager)

    # Your automation logic
    # Note: All coordinates are percentage-based (0.0-1.0)
    # Example: manager.tap(0.5, 0.5) taps center of screen
    for i in range(10):
        print(f"Loop {i}: Planting trees...")
        plant_tree(manager, "tree-type")
        manager.sleep(3)

        print(f"Loop {i}: Harvesting...")
        harvest_tree(manager)

    print("Script completed successfully!")

if __name__ == "__main__":
    main()
```

### Available Utilities (scripts/core.py)

The `core.py` module provides shared automation functions:

**Game Management**:
- `open_game(manager)` - Launch game and handle popups
- `open_chest(manager)` - Open available chests
- `go_up(manager, times=1)` - Navigate upward
- `go_down(manager, times=1)` - Navigate downward

**Farming**:
- `plant_tree(manager, tree=None, num=12)` - Plant trees in grid
- `harvest_tree(manager)` - Harvest all trees
- `make_items(manager, floor=1, slot=0, num=1)` - Craft items

**Market**:
- `sell_items(manager, option, items)` - Sell items at market

**ADB Controller Methods** (uses percentage coordinates 0.0-1.0):
- `tap(x, y)` - Tap at percentage coordinates (e.g., `0.5, 0.5` for center)
- `swipe(x1, y1, x2, y2, duration)` - Swipe gesture with percentage coords
- `drag(points)` - Multi-point drag (e.g., `[(0.25, 0.78), (0.38, 0.83)]`)
- `find_image_on_screen(template_path, threshold=0.9)` - Find image, returns percentage coords
- `click_image(template_path)` - Find and click image
- `click_text(text, lang="eng")` - OCR-based text clicking
- `press_key(keycode)` - Press Android key (use KeyCode enum)
- `capture_screen()` - Take screenshot

### Script Discovery

Scripts are automatically discovered from `backend/src/scripts/`:
- Filename: `my_script.py` → Script ID: `my_script`
- Display name is auto-generated (title-cased)
- Files matching patterns in `.ignore` are excluded

### Testing Scripts

**Direct execution** (faster iteration):
```bash
cd backend
poetry run python src/scripts/my_script.py emulator-5554 '{"open_game":true}'
```

**Via API** (full integration):
```bash
curl -X POST http://localhost:3001/api/execute/start \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "emulator-5554",
    "script_id": "my_script",
    "game_options": {"open_game": true}
  }'
```

## Development

### Available Commands

**Monorepo** (from root):
```bash
pnpm dev          # Run all services in development
pnpm build        # Build all packages
pnpm lint         # Lint all packages
pnpm format       # Format all packages
pnpm clean        # Clean build artifacts
```

**Backend** (from `backend/`):
```bash
poetry run python src/main.py --env dev     # Dev server
poetry run python src/main.py --env prod    # Production server
poetry run black src/                       # Format code
poetry run isort src/                       # Sort imports
poetry run flake8 src/                      # Lint
poetry run mypy src/                        # Type checking
poetry run pytest                           # Run tests
```

**Frontend** (from `frontend/`):
```bash
npm run dev       # Next.js dev server
npm run build     # Build for production
npm start         # Start production server
npm run lint      # ESLint
npm run format    # Fix linting issues
```

### Code Quality

The project includes automated code quality tools:

**Python**:
- **Black** - Code formatter (88 char line length)
- **isort** - Import sorting
- **Flake8** - Linting
- **mypy** - Type checking
- **pytest** - Testing framework

**TypeScript**:
- **ESLint** - Linting
- **TypeScript** - Type checking
- **Prettier** - Code formatting (via ESLint)

## API Documentation

### Endpoints Overview

**Devices**:
- `GET /api/devices` - List all devices
- `GET /api/devices/{device_id}` - Get device details
- `GET /api/devices/{device_id}/logs` - Get device logs

**Scripts**:
- `GET /api/scripts` - List available scripts

**Execution**:
- `POST /api/execute/start` - Start script on device
- `POST /api/execute/stop` - Stop specific execution
- `POST /api/execute/stop-all` - Stop all running scripts

**Live Streaming** (Socket.IO via WebSocket):
- `start_stream` event - Start H.264 video stream for device
- `stop_stream` event - Stop current stream
- `stream_data` event - Receive video chunks (base64-encoded H.264)

**System**:
- `GET /health` - Health check

For detailed API documentation and architecture, see [CLAUDE.md](./CLAUDE.md).

## Production Deployment

The project uses PM2 for production process management:

```bash
# Start services
pnpm prod

# View status
pnpm prod:status

# View logs
pnpm prod:logs

# Restart services
pnpm prod:restart

# Stop services
pnpm prod:stop
```

PM2 configuration is defined in `ecosystem.config.js`.

## Troubleshooting

### Devices Not Detected

1. Verify ADB connection: `adb devices`
2. Check USB debugging is enabled on device
3. Restart ADB server: `adb kill-server && adb start-server`
4. Check backend logs for discovery errors

### Script Execution Fails

1. Ensure device status is "available" (not busy or offline)
2. Check script syntax and imports
3. View device logs for error details
4. Test script directly: `poetry run python src/scripts/<script>.py <device_id>`

### Image Matching Fails

1. Verify template exists in `backend/src/assets/`
2. Check screen resolution matches template expectations
3. Lower threshold parameter (default 0.9) for more lenient matching
4. Use `find_image_on_screen()` to debug matching

### Live Streaming Not Working

1. Ensure backend is running with Socket.IO support
2. Check that frontend custom server (`server.ts`) is running (not standard Next.js server)
3. Verify WebSocket connection in browser developer tools (Network → WS tab)
4. Check device supports `screenrecord` command: `adb shell screenrecord --help`
5. Look for errors in backend logs related to H.264 streaming

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Follow code style guidelines (Black, ESLint)
4. Write tests for new functionality
5. Commit with conventional commits: `feat:`, `fix:`, `refactor:`, etc.
6. Submit a pull request

## Documentation

- **CLAUDE.md** - Detailed technical documentation for developers
- **README.md** - This file (quick start and overview)

## License

[Add your license here]

## Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation in CLAUDE.md
- Review script examples in `backend/src/scripts/`

---

**Built with ❤️ for Android automation**
