# KVTM Auto - Android Device Automation Platform

A comprehensive full-stack application for automating Android devices using ADB (Android Debug Bridge). Built with a modern React + TypeScript frontend and Python FastAPI backend with advanced Android automation capabilities.

**Recently refactored** for simplicity, maintainability, and better user experience with 50% code reduction and enhanced logging.

## Features

### 🤖 Device Management
- Automatic device discovery via ADB
- Real-time device status monitoring  
- USB device support with privileged Docker access
- Device connection/disconnection management
- Device details and specifications display

### 📝 Script Management - **SIMPLIFIED**
- Custom automation script execution with metadata
- **Subprocess-only execution** (no threading complexity)
- Real-time progress tracking with **clean log format**
- Script execution history and status
- Enhanced shell command building with loop support

### 📊 Logging & Monitoring - **ENHANCED**
- **New Simple Log Format**: `[12:34:56 PM]: Run Script [1000] times`
- Device-specific log filtering
- Real-time log streaming
- User-friendly action-based logging
- Health check endpoints

### 🎛️ Web Interface
- Modern React-based UI with Vite and Tailwind CSS
- Real-time updates with TanStack Query v4
- Responsive device management dashboard
- Interactive script execution controls
- **Enhanced log display** with clean time format
- Mobile-responsive design
- Clean blue gradient interface

### 🔧 Technology Stack - **UPDATED**
- **Backend**: FastAPI 0.104.1, Python 3.9+, **Simplified Architecture**
- **Frontend**: React 18.2, TypeScript 5+, Vite 7.1.2, Tailwind CSS 3.3
- **Containerization**: Docker with privileged mode for USB device access
- **Image Processing**: OpenCV, NumPy for device screenshots
- **Shell Utilities**: **NEW - Enhanced command building with Shell class**
- **Logging**: **NEW - Simple [Time]: [Action] [Index] format**
- **Models**: **NEW - Unified API models in single location**

## Architecture - **REFACTORED**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Android       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Devices       │
│   Vite Dev      │    │   Simplified    │    │   (ADB)         │
│   or Docker     │    │   Subprocess    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Recent Refactoring Benefits**
- **50% less code** - Simplified executor, APIs, and error handling
- **Subprocess-only execution** - Better isolation, simpler debugging
- **Clean logging** - `[12:34:56 PM]: Run Open Game` format
- **Unified models** - All API models centralized
- **Enhanced shell support** - Programmatic command building
- **Global error handling** - Consistent across all endpoints

## Quick Start

### Prerequisites
- Docker and Docker Compose (for containerized deployment)
- **OR** Python 3.9+ and Node.js 16+ (for local development)
- Android SDK platform tools (ADB) 
- USB debugging enabled on Android devices

### Option 1: Docker Deployment (Recommended for Production)

1. Clone the repository:
```bash
git clone <repository-url>
cd kvtm-auto
```

2. **Important**: Ensure ADB is installed on your host system and USB debugging is enabled on your Android devices.

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Option 2: Local Development (Recommended for Development)

1. Clone and setup backend:
```bash
cd kvtm-auto/backend
poetry install
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. Setup frontend (in new terminal):
```bash
cd kvtm-auto/frontend  
npm install
npm run dev  # Starts on localhost:5173
```

3. Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

### Device Management
1. Connect Android devices via USB
2. Enable USB debugging in developer options
3. Devices automatically appear in the web interface
4. Use the interface to manage device connections

### Script Execution - **ENHANCED**
1. Place Python scripts in `backend/scripts/` directory
2. Scripts automatically appear in the web interface
3. Select target devices and run scripts
4. **Monitor progress with clean logs**: `[12:34:56 PM]: Run Script [1000] times`

### Writing Custom Scripts - **SIMPLIFIED**

Create a Python file in `backend/scripts/` with the new simple logging:

```python
from scripts._core import write_log, log_run_open_game, log_run_script, log_loop_iteration

# Script metadata - required for script discovery
SCRIPT_META = {
    "id": "my_script",
    "name": "My Custom Script",
    "order": 1,
    "marked": True,
    "description": "Description of what this script does"
}

def main(device: Device, game_options: GameOptions, context):
    """
    Main script function for CLI execution with new simple logging
    
    Logs will appear as:
    [12:34:56 PM]: Run Open Game
    [12:34:57 PM]: Run Script [1000] times
    [12:34:58 PM]: Loop [1/1000]
    """
    
    # Use simple logging functions
    log_run_open_game(device.id)
    log_run_script(device.id, 1000)
    
    # Custom actions with clean format
    write_log(device.id, "Taking screenshot")
    write_log(device.id, "Waiting", "5.0s")  # [12:34:58 PM]: Waiting [5.0s]
    
    # Loop with progress tracking
    for i in range(1000):
        log_loop_iteration(device.id, i+1, 1000)  # [12:35:01 PM]: Loop [1/1000]
        
        # Your automation logic here
        # No complex try-catch needed - global handler will catch errors
        
    return {"status": "success", "message": "Completed"}
```

### **New Logging Format Examples**
Your logs will now display cleanly:
```
[12:12:39 PM]: Run Open Game
[12:14:23 PM]: Run Script [1000] times  
[12:14:25 PM]: Script started [my_script]
[12:15:45 PM]: Loop [1/1000]
[12:15:47 PM]: Waiting [1.0]s
[12:15:48 PM]: Loop [2/1000]
[12:22:15 PM]: Script completed
```

## API Documentation - **SIMPLIFIED**

The backend provides a RESTful API with simplified endpoints:

### Devices
- `GET /api/devices` - List all devices
- `GET /api/devices/{device_id}` - Get device details  
- `GET /api/devices/{device_id}/logs` - Get device logs (new format)

### Scripts
- `GET /api/scripts` - List available scripts
- `GET /api/scripts/{script_id}` - Get script details

### Script Execution - **STREAMLINED**
- `POST /api/execute/start` - Start script execution
- `POST /api/execute/stop` - Stop script on device
- `POST /api/execute/stop-all` - Stop all running scripts

### System
- `GET /health` - Health check endpoint

## Development

### Project Structure - **UPDATED**
```
kvtm-auto/
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── DeviceDetailModal.tsx
│   │   │   ├── DeviceLogModal.tsx    # NEW - Simple log display
│   │   │   ├── Modal.tsx
│   │   │   ├── MultiSelect.tsx
│   │   │   └── SearchableSelect.tsx
│   │   ├── api.ts              # API client
│   │   ├── App.tsx             # Main application
│   │   └── main.tsx            # Entry point
│   └── package.json            # Dependencies
├── backend/                     # Python FastAPI backend - REFACTORED
│   ├── src/
│   │   ├── api/               # API routes - SIMPLIFIED
│   │   │   ├── devices.py     # Unified models, no complex try-catch
│   │   │   ├── scripts.py     # No validation, simple endpoints
│   │   │   └── execute.py     # Streamlined execution API
│   │   ├── service/           # Service layer - STREAMLINED  
│   │   │   ├── executor.py    # Subprocess-only (450→150 lines)
│   │   │   ├── database.py    # Simple log format storage
│   │   │   └── script.py      # Script management
│   │   ├── libs/              # Core utilities - ENHANCED
│   │   │   ├── adb.py         # Android Debug Bridge wrapper
│   │   │   ├── shell.py       # NEW - Shell command utilities
│   │   │   ├── time_provider.py # Enhanced time utilities
│   │   │   ├── log_actions.py  # NEW - Standard log constants
│   │   │   └── image.py       # Image processing
│   │   ├── models/            # Data models - UNIFIED
│   │   │   ├── device.py      # Device models
│   │   │   ├── script.py      # Script models  
│   │   │   └── api.py         # NEW - All API models centralized
│   │   ├── scripts/           # Automation scripts
│   │   │   ├── _core.py       # ENHANCED - Simple logging utilities
│   │   │   ├── example_script.py
│   │   │   └── open_game.py
│   │   ├── data/              # JSON storage (moved under src/)
│   │   ├── logs/              # Log files (moved under src/)
│   │   └── main.py            # FastAPI entry point
│   └── pyproject.toml         # Poetry configuration
├── docker-compose.yml          # Container orchestration  
├── CLAUDE.md                   # Development guidance (UPDATED)
└── README.md                   # Project documentation (THIS FILE)
```

### Code Quality & Development Commands

```bash
# Local Backend Development
cd backend
poetry install
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
poetry run black src/              # Format code
poetry run isort src/              # Sort imports  
poetry run flake8 src/             # Lint code
poetry run mypy src/               # Type checking
poetry run pytest                 # Run tests

# Local Frontend Development  
cd frontend
npm install
npm run dev                        # Start dev server (localhost:5173)
npm run build                      # Build for production
npm run lint                       # ESLint check
npm run format                     # Fix linting issues

# Docker Development
docker-compose up -d               # Start all services
docker-compose down                # Stop services
docker-compose build               # Rebuild after changes
docker-compose logs backend        # View backend logs
docker-compose logs frontend       # View frontend logs
```

### **New Architecture Benefits**

#### **For Developers**
- **50% less code** to maintain and debug
- **Simplified APIs** - no complex validation or try-catch blocks
- **Unified models** - single source of truth for API contracts
- **Enhanced shell support** - programmatic command building
- **Global error handling** - consistent responses

#### **For Users** 
- **Clean log format** - easy to read `[Time]: [Action] [Index]`
- **Better reliability** - subprocess isolation
- **Faster development** - simplified architecture
- **Consistent experience** - unified error handling

## Configuration

### Environment Variables

#### Backend
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `PYTHONPATH` - Python module path

#### Frontend  
- `VITE_API_URL` - Backend API URL
  - Local: `http://localhost:8000/api`
  - Docker: `http://localhost:8000/api`

### Deployment Options

| Environment | Backend | Frontend | Use Case |
|------------|---------|----------|----------|
| **Local Dev** | localhost:8000 | localhost:5173 | Fast development |
| **Docker** | localhost:8000 | localhost:3000 | Production-like testing |

## Troubleshooting

### Common Issues

**Devices not appearing**
- Ensure USB debugging is enabled
- Check ADB driver installation  
- Verify device authorization in ADB

**Permission denied errors**
- Enable USB debugging on devices
- Run Docker with privileged mode (configured)
- Add user to `plugdev` group on Linux

**Script execution failures**
- Check device connectivity with `adb devices`
- Review execution logs (now in clean format)
- Verify script syntax

**Logs not displaying correctly**
- Check if using new logging format: `write_log(device_id, "Action", "index")`
- Old format logs may not display properly
- Update scripts to use `_core.py` logging utilities

### **Development Tips**

**Local Development**
- Use `poetry run uvicorn src.main:app --reload` for hot reload
- Use `npm run dev` for frontend hot reload
- Logs appear in terminal and database

**Docker Development**  
- Use `docker-compose logs -f backend` for live log monitoring
- Rebuild containers after code changes: `docker-compose build`
- Access logs via API: `GET /api/devices/{device_id}/logs`

**Script Development**
- Use new simple logging: `log_run_script(device_id, 1000)`
- Avoid complex try-catch - let global handler manage errors
- Test with local development for faster iteration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Use the new simplified architecture patterns
4. Add tests for new functionality
5. Use the simple logging format for user-facing logs
6. Ensure all tests pass
7. Submit a pull request

## Recent Changes (v2.0)

### **Architecture Refactoring**
- ✅ **Simplified Executor** - 450 lines → 150 lines (subprocess-only)
- ✅ **Streamlined APIs** - 50% code reduction across all endpoints  
- ✅ **Unified Models** - All API models centralized in `models/api.py`
- ✅ **Enhanced Shell Support** - `Shell` class with loop command building
- ✅ **Simple Logging** - `[Time]: [Action] [Index]` format
- ✅ **Global Error Handling** - Consistent error responses
- ✅ **Directory Restructure** - Data/logs moved under `src/`

### **Benefits**
- **Maintainability**: 50% less code to maintain
- **Reliability**: Better process isolation with subprocess-only approach
- **User Experience**: Clean, readable logs  
- **Developer Experience**: Simplified APIs, unified models
- **Performance**: Removed unnecessary complexity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: Check CLAUDE.md for development guidance
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **Issues**: Use GitHub issue tracker  
- **Architecture**: See refactoring notes in CLAUDE.md