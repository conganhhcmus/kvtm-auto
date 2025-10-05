# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**KVTM Auto** is a full-stack Android device automation platform for automating mobile games via ADB (Android Debug Bridge). The system uses:
- **Backend**: Flask (Python 3.9+) on port 3001
- **Frontend**: Next.js 14 + React 18 + TypeScript on port 3000 (proxies `/api` to backend)
- **Monorepo**: Turborepo with pnpm workspace management
- **Core Technology**: ADB for device control, OpenCV for image matching, subprocess for script execution

## Development Commands

### Monorepo Commands (Root)
```bash
pnpm install                                      # Install all dependencies
pnpm dev                                          # Run both frontend & backend (Turborepo)
pnpm build                                        # Build all packages
pnpm lint                                         # Lint all packages
pnpm clean                                        # Clean all build artifacts
```

### Backend Development
```bash
cd backend
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

### Frontend Development
```bash
cd frontend
npm install                                       # Install dependencies
npm run dev                                       # Next.js dev server (port 3000)
npm run build                                     # Build for production
npm start                                         # Start production server
npm run lint                                      # ESLint check
npm run format                                    # Fix linting issues
npm run clean                                     # Clean build artifacts
```

**Important**: Frontend uses Next.js and proxies `/api` requests to `http://localhost:3001` via `next.config.js` rewrites. Backend URL can be configured with `NEXT_PUBLIC_BACKEND_URL` env variable.

## Architecture

### Backend Structure (Flask + Blueprints)

```
backend/src/
├── main.py                    # Flask app entry point
├── apis/                      # API blueprints
│   ├── device_apis.py         # Device endpoints
│   ├── script_apis.py         # Script endpoints
│   ├── execution_apis.py      # Execution control
│   └── system_apis.py         # Health checks
├── libs/                      # Core libraries
│   ├── device_manager.py      # Device discovery & tracking (Singleton)
│   ├── execution_manager.py   # Script execution via subprocess
│   ├── script_manager.py      # Script loading & management
│   ├── storage_manager.py     # File-based persistence (Singleton)
│   ├── adb_controller.py      # ADB command wrapper
│   └── image_controller.py    # OpenCV image matching
├── models/                    # Data models
│   ├── device.py              # Device model
│   ├── script.py              # Script model
│   ├── game_options.py        # Script options
│   └── execution.py           # Running script model
├── scripts/                   # Automation scripts
│   └── core.py                # Shared utilities (open_game, plant_tree, etc.)
├── data/                      # Runtime data
│   ├── device_state.json      # Persisted device states
│   └── logs/                  # Per-device log files
└── assets/                    # Image templates for matching
```

### Key Architectural Patterns

1. **Singleton Managers**: `DeviceManager`, `StorageManager`, `ExecutionManager` use singleton pattern for shared state across requests
2. **Subprocess Execution**: Scripts run as separate Python processes (not threads) for isolation
3. **Background Threads**: Device discovery runs continuously, log capture runs per-execution
4. **File-based Storage**: Device state saved to JSON, logs saved to individual files per device

### Frontend Structure (Next.js + React + TypeScript)

```
frontend/src/
├── app/
│   ├── page.tsx              # Main page (home)
│   ├── layout.tsx            # Root layout with metadata
│   └── globals.css           # Global styles
├── components/
│   ├── DeviceDetailModal.tsx # Device details view
│   ├── DeviceLogModal.tsx    # Real-time logs display
│   ├── Modal.tsx             # Base modal component
│   ├── MultiSelect.tsx       # Device multi-select
│   └── SearchableSelect.tsx  # Script selector
└── api.ts                     # API client (axios)
```

- Uses **Next.js 14** (App Router)
- **TanStack Query v4** for data fetching and caching
- State managed via React hooks and localStorage
- Tailwind CSS for styling
- API rewrites configured in `next.config.js`

## Core System Flows

### Device Discovery & Management

**DeviceManager** (`libs/device_manager.py`):
- Runs background thread checking `adb devices` every 5 seconds
- Automatically creates `Device` objects for new devices
- Persists device state (name, status, screen_size) to `data/device_state.json`
- Tracks device status: `available`, `busy`, `offline`
- Fetches screen size via `adb shell wm size` and caches it

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

**Basic Commands**:
- `tap(x, y)` - Tap at coordinates
- `swipe(x1, y1, x2, y2, duration)` - Swipe gesture
- `press_key(keycode)` - Press Android key (HOME, BACK, etc.)
- `open_app(package_name)` / `close_app(package_name)` - App control

**Image-based Automation**:
- `find_image_on_screen(template_path, threshold=0.9)` - Returns (x, y) or None
- `click_image(template_path)` - Find and click image
- `click_text(target_text, lang="eng")` - OCR-based text clicking

**Advanced Gestures**:
- `drag(points)` - Multi-point drag using `sendevent` for precise control
- Supports complex paths through coordinate lists
- Uses device coordinate conversion (screen coords → touch device coords)

**Assets**: Image templates stored in `backend/assets/` directory

## Writing Custom Scripts

### Script Structure

Scripts must be placed in `backend/src/scripts/` and follow this pattern:

```python
import json
import sys
import os

# Add backend/src to path
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
- Scans `backend/src/scripts/` for `.py` files
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
- Logs saved to `backend/src/data/logs/<device_serial>.log`
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

### Multi-Touch & Gestures

**Drag Implementation**:
- Uses low-level `sendevent` commands for precise touch control
- Converts screen coordinates to device coordinates (0-32767 range for BlueStacks)
- Supports complex multi-point paths
- Default touch device: `/dev/input/event2`

**Example**:
```python
# Drag item to multiple planting locations
points = [(slot_x, slot_y), (720, 900), (890, 900), (1060, 900)]
manager.drag(points)
```

### Image Matching

**OpenCV-based Detection**:
- Templates stored in `backend/assets/` directory
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

### System
- `GET /health` - Health check endpoint

## Testing & Debugging

### Script Testing

**Direct Execution** (faster for development):
```bash
cd backend
poetry run python src/scripts/vai_tim.py emulator-5554 '{"open_game":true}'
```

**Via API** (full integration test):
1. Start backend: `poetry run python src/main.py --env dev`
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
- Check backend logs for discovery errors

**Script Execution Fails**:
- Check script has correct shebang and imports
- Verify device is `available` (not `busy` or `offline`)
- Check logs: `GET /api/devices/{device_id}/logs`

**Image Matching Fails**:
- Verify template exists in `assets/` directory
- Check image threshold (lower if needed)
- Ensure screen resolution matches template expectations

## Performance Considerations

1. **Device Discovery**: Runs every 5 seconds - adjust if needed in `DeviceManager._start_discovery()`
2. **Log Streaming**: Line-buffered subprocess output for real-time updates
3. **Image Matching**: Max 3 retries with 0.5s delay - adjust `max_retries` parameter
4. **File Locks**: StorageManager uses threading.Lock for thread-safe file operations

## Important Notes

### UI State Persistence

The frontend persists UI state to localStorage:
- **Control Panel Expansion**: Saves Hide/Show state of control panel
- Key: `'controlPanelExpanded'`
- Implementation: `useState` initializer + `useEffect` hook in `app/page.tsx`
