# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**KVTM Auto** is a full-stack Android device automation platform for automating mobile games via ADB (Android Debug Bridge). The system uses:
- **Server (Backend)**: Flask + Flask-SocketIO (Python 3.9+) on port 3001 with WebSocket support
- **Client (Frontend)**: Next.js 14 + React 18 + TypeScript on port 3000 with custom Express server
- **Monorepo**: Turborepo with pnpm workspace management (`apps/server` and `apps/client`)
- **Core Technology**: adbutils for device control, OpenCV for image matching, Socket.IO for live streaming, subprocess for script execution

## Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 9.0.0
- **Python** >= 3.9
- **Poetry** - Python dependency management
- **ADB (Android Debug Bridge)** - For device communication
- **Android Device/Emulator** - With USB debugging enabled

**Key Dependencies**:
- **Server (Backend)**: adbutils 2.10.2, Flask 3.0+, OpenCV, Tesseract OCR
- **Client (Frontend)**: Next.js 14, React 18, Socket.IO Client, JMuxer

## Development Commands

### Monorepo Commands (Root)
```bash
pnpm install                                      # Install all dependencies
pnpm dev                                          # Run both frontend & backend (Turborepo)
pnpm build                                        # Build all packages
pnpm lint                                         # Lint all packages
pnpm clean                                        # Clean all build artifacts
```

### Server Development (Backend)
```bash
cd apps/server
poetry install                                    # Install dependencies
poetry run python src/main.py --env dev          # Run dev server (port 3001, auto-reload)
poetry run python src/main.py --env prod         # Run production server

# Code Quality
poetry run black src/                            # Format code
poetry run isort src/                            # Sort imports
poetry run flake8 src/                           # Lint code
poetry run mypy src/                             # Type checking
poetry run pytest                                # Run tests
```

### Client Development (Frontend)
```bash
cd apps/client
npm install                                       # Install dependencies
npm run dev                                       # Next.js dev server (port 3000)
npm run build                                     # Build for production
npm start                                         # Start production server
npm run lint                                      # ESLint check
npm run format                                    # Fix linting issues
npm run clean                                     # Clean build artifacts
```

**Important**: Client uses custom Express server (`server.ts`) that proxies `/api` and `/socket.io` requests to server (`http://localhost:3001`). Server URL can be configured with `NEXT_PUBLIC_BACKEND_URL` env variable. WebSocket upgrade handling is implemented for Socket.IO connections.

## Architecture

### Server Structure (Backend - Flask + Blueprints)

```
apps/server/src/
├── main.py                    # Flask app entry point with Socket.IO
├── apis/                      # API blueprints
│   ├── device_apis.py         # Device endpoints
│   ├── script_apis.py         # Script endpoints
│   ├── execution_apis.py      # Execution control
│   ├── stream_apis.py         # Live screen streaming (Socket.IO)
│   └── system_apis.py         # Health checks
├── libs/                      # Core libraries
│   ├── device_manager.py      # Device discovery & tracking (Singleton)
│   ├── execution_manager.py   # Script execution via subprocess
│   ├── script_manager.py      # Script loading & management
│   ├── storage_manager.py     # File-based persistence (Singleton)
│   ├── adb_controller.py      # ADB wrapper using adbutils library
│   └── image_controller.py    # OpenCV image matching
├── models/                    # Data models
│   ├── device.py              # Device model
│   ├── script.py              # Script model
│   ├── game_options.py        # Script options
│   └── execution.py           # Running script model
├── scripts/                   # Automation scripts
│   ├── core.py                # Shared utilities (open_game, plant_tree, etc.)
│   └── .ignore                # Patterns to exclude from script discovery
├── data/                      # Runtime data
│   ├── device_state.json      # Persisted device states
│   └── logs/                  # Per-device log files
└── assets/                    # Image templates for matching
```

### Key Architectural Patterns

1. **Singleton Managers**: `DeviceManager`, `StorageManager`, `ExecutionManager` use singleton pattern for shared state across requests
2. **Subprocess Execution**: Scripts run as separate Python processes (not threads) for isolation
3. **Background Threads**: Device discovery runs continuously, log capture runs per-execution, screen streaming runs per-session
4. **File-based Storage**: Device state saved to JSON, logs saved to individual files per device
5. **Socket.IO Integration**: Flask-SocketIO with threading mode for WebSocket communication (compatible with Python 3.13+)
6. **Real-time Streaming**: H.264 video streaming via Socket.IO using `adb screenrecord` with NAL unit detection

### Client Structure (Frontend - Next.js + React + TypeScript)

```
apps/client/
├── server.ts                  # Custom Express server with proxy & WebSocket
├── src/
│   ├── app/
│   │   ├── page.tsx           # Main page (home)
│   │   ├── layout.tsx         # Root layout with metadata
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── DeviceDetailModal.tsx  # Device details view
│   │   ├── DeviceLogModal.tsx     # Real-time logs display
│   │   ├── LiveScreenModal.tsx    # Live H.264 screen streaming
│   │   ├── Modal.tsx              # Base modal component
│   │   ├── MultiSelect.tsx        # Device multi-select
│   │   └── SearchableSelect.tsx   # Script selector
│   └── api.ts                 # API client (axios)
```

- Uses **Next.js 14** (App Router)
- **TanStack Query v4** for data fetching and caching
- **Socket.IO Client** for WebSocket communication and live streaming
- **Custom Express Server** (`server.ts`) handles API/WebSocket proxying to backend
- State managed via React hooks and localStorage
- Tailwind CSS for styling
- **JMuxer** for H.264 video playback in browser

## Core System Flows

### Device Discovery & Management

**DeviceManager** (`libs/device_manager.py`):
- Runs background thread using adbutils to check connected devices every 5 seconds
- Automatically creates `Device` objects for new devices
- Persists device state (name, status, execution info) to `data/device_state.json`
- Tracks device status: `available`, `busy`, `offline`
- Uses adbutils `AdbClient.device_list()` for discovery

**Device Serial to Name Mapping**:
```python
SERIAL_NAME_MAP = {
    "emulator-5554": "Kai",
    "emulator-5564": "Cong Anh",
    "emulator-5574": "My Hanh",
}
```

### Script Execution Flow

1. **Start Request** → `POST /api/execute/start`
   - Validates device (must be `available`) and script
   - Clears device logs
   - Launches subprocess: `python -u <script_path> <device_id> [<game_options_json>]`
   - Sets device status to `busy`
   - Creates `RunningScript` tracking object
   - Starts background thread to capture subprocess stdout

2. **Log Capture** (background thread in `ExecutionManager._capture_logs`):
   - Reads subprocess stdout line-by-line
   - Appends to device logs with timestamps: `[HH:MM:SS]: <message>`
   - Saves to `data/logs/<device_serial>.log`
   - Cleans up device state when script completes or errors

3. **Stop Request** → `POST /api/execute/stop`
   - Terminates subprocess
   - Waits for log thread to finish
   - Sets device status back to `available`
   - Saves device state

### ADB Controller Features

**AdbController** (`libs/adb_controller.py`) provides:

**Core Library**: Uses **adbutils 2.10.2** library for all ADB operations (wraps `AdbClient` and device objects)

**Coordinate System**: All methods use **percentage-based coordinates (0.0-1.0)** for screen positions
- Example: `tap(0.5, 0.5)` taps center of screen
- Internally converts to pixel coordinates based on device screen size

**Basic Commands**:
- `tap(x, y)` - Tap at percentage coordinates (0.0-1.0)
- `swipe(x1, y1, x2, y2, duration)` - Swipe gesture with percentage coords
- `press_key(keycode)` - Press Android key using KeyCode enum (HOME, BACK, etc.)
- `open_app(package_name)` / `close_app(package_name)` - App control
- `capture_screen()` - Screenshot as PNG bytes (uses adbutils built-in)

**Image-based Automation**:
- `find_image_on_screen(template_path, threshold=0.9)` - Returns percentage coords (0.0-1.0) or raises IOError
- `click_image(template_path)` - Find and click image, auto-retry up to 3 times
- `click_text(target_text, lang="eng")` - OCR-based text clicking with Tesseract

**Advanced Gestures**:
- `drag(points)` - Multi-point drag using low-level `sendevent` commands
- Points are percentage coordinates: `[(0.25, 0.78), (0.38, 0.83), ...]`
- Converts to device coordinates (0-32767 range for BlueStacks Virtual Touch)
- Default touch device: `/dev/input/event2`

**Assets**: Image templates stored in `apps/server/assets/` directory (supports subdirectories)

**Error Handling**: `@retry_on_error` decorator retries failed operations up to 3 times with exponential backoff

## Writing Custom Scripts

### Script Structure

Scripts must be placed in `apps/server/src/scripts/` and follow this pattern:

```python
import json
import sys
import os

# Add apps/server/src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.adb_controller import AdbController
from models.game_options import GameOptions
from scripts.core import open_game, open_chest, plant_tree, harvest_tree

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <device_id> [game_options_json]")
        sys.exit(1)

    device_id = sys.argv[1]
    game_options = GameOptions()

    # Parse optional game options
    if len(sys.argv) > 2:
        try:
            options_dict = json.loads(sys.argv[2])
            game_options = GameOptions.from_dict(options_dict)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for game_options")
            sys.exit(1)

    # Initialize ADB controller
    manager = AdbController(device_id)

    # Use game options to control behavior
    if game_options.open_game:
        open_game(manager)

    # Your automation logic here
    for i in range(100):
        print(f"Loop {i}: Doing something...")
        plant_tree(manager, "tree-type")
        manager.sleep(5)
        harvest_tree(manager)

    print("Script completed")

if __name__ == "__main__":
    main()
```

### Script Discovery

**ScriptManager** automatically discovers scripts:
- Scans `apps/server/src/scripts/` for `.py` files
- Excludes files matching patterns in `.ignore` file
- Generates script ID from filename (e.g., `vai_tim.py` → `vai_tim`)
- Generates display name by title-casing (e.g., `vai_tim` → `Vai Tim`)

### Shared Utilities (scripts/core.py)

Common automation functions available:

**Game Management**:
- `open_game(manager)` - Open game app, wait for load, close popups
- `open_chest(manager)` - Open available chests
- `go_up(manager, times=1)` / `go_down(manager, times=1)` - Navigation
- `go_last(manager)` - Navigate to last position

**Farming Automation**:
- `plant_tree(manager, tree=None, num=12, next=True)` - Plant trees in grid
- `harvest_tree(manager)` - Harvest all trees
- `make_items(manager, floor=1, slot=0, num=1)` - Craft items

**Market**:
- `sell_items(manager, option: SellOption, items)` - Sell items at market
- SellOption enum: `TREES=0, GOODS=1, OTHERS=2, MINERAL=3, EVENTS=4`

**Core Utilities**:
- `_close_all_popup(manager, num=10)` - Close popups via BACK key

## Important Implementation Details

### Logging System

**Log Format**: All logs timestamped with `[HH:MM:SS]: <message>` format

**Storage**:
- Logs saved to `apps/server/src/data/logs/<device_serial>.log`
- Thread-safe file operations via `StorageManager._file_lock`
- `device.add_log(message)` - Append log
- `device.get_logs(limit=100)` - Retrieve recent logs
- `device.clear_logs()` - Clear all logs

**Real-time Updates**:
- Frontend polls logs via `GET /api/devices/{device_id}/logs`
- Subprocess output captured line-by-line and streamed to logs
- Use `python -u` flag for unbuffered output

### Game Options

**GameOptions Model** (`models/game_options.py`):
```python
class GameOptions:
    def __init__(self, open_game=False, open_chest=False, sell_items=False):
        self.open_game = open_game
        self.open_chest = open_chest
        self.sell_items = sell_items
```

Passed from frontend to scripts as JSON argument.

### Live Screen Streaming

**Architecture** (`apis/stream_apis.py`):
- Uses **Socket.IO** for real-time H.264 video streaming
- Backend spawns `adb screenrecord` process per session
- Streams raw H.264 data over WebSocket using NAL unit boundary detection
- Frontend uses **JMuxer** library to decode and play H.264 in browser

**Stream Configuration**:
- Bit rate: 2.5 Mbps (balanced for live monitoring)
- Format: H.264 raw stream (`--output-format=h264`)
- Time limit: 3 minutes per session (auto-restarts if needed)
- NAL unit detection: Splits stream at `0x00 0x00 0x00 0x01` boundaries

**Socket.IO Events**:
- `start_stream` - Client requests stream for device
- `stream_data` - Server sends base64-encoded H.264 chunks
- `stop_stream` - Client stops stream
- `stream_error` / `stream_ended` - Status events

**Implementation Details**:
- Each session tracked in `active_streams` dict with stop flag
- Background thread reads from adb connection and emits chunks
- Buffer accumulates data until NAL boundary found
- Automatic cleanup on disconnect or errors

### Multi-Touch & Gestures

**Drag Implementation**:
- Uses low-level `sendevent` commands for precise touch control
- Converts percentage coordinates to device coordinates (0-32767 range for BlueStacks)
- Supports complex multi-point paths
- Default touch device: `/dev/input/event2`

**Example**:
```python
# Drag item to multiple planting locations (percentage coords)
points = [(0.25, 0.78), (0.38, 0.83), (0.46, 0.83), (0.55, 0.83)]
manager.drag(points)
```

### Image Matching

**OpenCV-based Detection**:
- Templates stored in `apps/server/assets/` directory
- Default threshold: 0.9 (90% match)
- Auto-retry up to 3 times with 0.5s delay
- Returns center coordinates of matched region

**Image Assets Paths**:
- Can use relative path: `"cay/oai-huong"` → searches `assets/cay/oai-huong.png`
- Or just filename: `"game"` → searches `assets/game.png`

## API Endpoints

### Devices
- `GET /api/devices` - List all devices
- `GET /api/devices/{device_id}` - Get device details
- `GET /api/devices/{device_id}/logs` - Get device logs

### Scripts
- `GET /api/scripts` - List available scripts

### Execution
- `POST /api/execute/start` - Start script on device
  - Body: `{ device_id, script_id, game_options }`
  - Returns: `{ execution_id, status, device, script }`
- `POST /api/execute/stop` - Stop specific execution
  - Body: `{ execution_id }`
- `POST /api/execute/stop-all` - Stop all running scripts

### Streaming (Socket.IO)
- `start_stream` event - Start live screen streaming for device
  - Data: `{ device_id }`
- `stop_stream` event - Stop current stream
- `stream_data` event - Receive H.264 video chunks (base64-encoded)
- `stream_started` / `stream_stopped` / `stream_error` / `stream_ended` - Status events

### System
- `GET /health` - Health check endpoint

## Testing & Debugging

### Script Testing

**Direct Execution** (faster for development):
```bash
cd apps/server
poetry run python src/scripts/vai_tim.py emulator-5554 '{"open_game":true}'
```

**Via API** (full integration test):
1. Start server: `cd apps/server && poetry run python src/main.py --env dev`
2. Use frontend or curl:
```bash
curl -X POST http://localhost:3001/api/execute/start \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "emulator-5554",
    "script_id": "vai_tim",
    "game_options": {"open_game": true}
  }'
```

### Common Issues

**Devices Not Appearing**:
- Check `adb devices` shows devices
- Ensure USB debugging enabled
- Check server logs for discovery errors

**Script Execution Fails**:
- Check script has correct shebang and imports
- Verify device is `available` (not `busy` or `offline`)
- Check logs: `GET /api/devices/{device_id}/logs`

**Image Matching Fails**:
- Verify template exists in `assets/` directory
- Check image threshold (lower if needed)
- Ensure screen resolution matches template expectations

## Production Deployment

### PM2 Process Management

**Configuration** (`ecosystem.config.js`):
- **Server (Backend)**: Runs via `poetry run gunicorn` on port 3001
  - Working directory: `./apps/server/src`
  - Worker timeout: 120 seconds
  - Max memory restart: 1GB
  - Logs: `logs/server-{error,out}.log`
- **Client (Frontend)**: Runs via `pnpm start` on port 3000
  - Working directory: `./apps/client`
  - Max memory restart: 500MB
  - Logs: `logs/client-{error,out}.log`

**Commands** (from project root):
```bash
pnpm prod         # Start all services with PM2
pnpm prod:stop    # Stop all services
pnpm prod:restart # Restart all services
pnpm prod:logs    # View combined logs
pnpm prod:status  # Check service status
```

**Important**: Client server uses custom Express server (`server.ts`) in production, not Next.js standalone. This ensures WebSocket proxying works correctly.

## Performance Considerations

1. **Device Discovery**: Runs every 5 seconds - adjust if needed in `DeviceManager._start_discovery()`
2. **Log Streaming**: Line-buffered subprocess output for real-time updates
3. **Image Matching**: Max 3 retries with 0.5s delay via `@retry_on_error` decorator
4. **File Locks**: StorageManager uses threading.Lock for thread-safe file operations
5. **Video Streaming**: 2.5 Mbps H.264 with NAL-based chunking for low latency
6. **Socket.IO**: Threading mode (async_mode='threading') for Python 3.13+ compatibility

## Important Notes

### Server Configuration (Backend)

**Flask-SocketIO Setup** (`apps/server/src/main.py`):
- Uses `async_mode='threading'` for Socket.IO compatibility with Python 3.13+
- Alternative: `eventlet` mode has issues with newer Python versions
- Server started via `socketio.run(app)` instead of `app.run()`
- CORS enabled for all origins during development

### Client Server Architecture (Frontend)

**Custom Express Server** (`apps/client/server.ts`):
- **Required** for WebSocket proxying (Socket.IO) to backend
- Standard Next.js server doesn't support WebSocket upgrade properly
- Handles two separate proxy paths:
  - `/api/*` - HTTP requests to backend REST API
  - `/socket.io/*` - WebSocket connections for live streaming
- Implements `upgrade` event handler for WebSocket handshake

### UI State Persistence

The client persists UI state to localStorage:
- **Control Panel Expansion**: Saves Hide/Show state of control panel
- Key: `'controlPanelExpanded'`
- Implementation: `useState` initializer + `useEffect` hook in `apps/client/src/app/page.tsx`

### Coordinate System

**All ADB operations use percentage-based coordinates (0.0-1.0)**:
- Screen-agnostic: Works across different device resolutions
- Example: `manager.tap(0.5, 0.5)` always taps center regardless of screen size
- Conversion to pixels happens internally in `AdbController`
- Drag gestures: `[(0.25, 0.78), (0.38, 0.83)]` instead of pixel coordinates
