# KVTM Auto - Android Device Automation Platform

A comprehensive full-stack application for automating Android devices using ADB (Android Debug Bridge). Built with a modern React + TypeScript frontend and Python FastAPI backend with advanced Android automation capabilities.

## Features

### 🤖 Device Management
- Automatic device discovery via ADB
- Real-time device status monitoring
- USB device support with privileged Docker access
- Device connection/disconnection management
- Device details and specifications display

### 📝 Script Management
- Custom automation script execution with metadata
- Multi-device parallel execution with threading isolation
- Real-time progress tracking
- Script execution history and status
- Integrated ADB command execution

### 📊 Logging & Monitoring
- Comprehensive system logging with Loguru
- Device-specific log filtering
- Script execution logs
- Real-time log streaming
- Health check endpoints

### 🎛️ Web Interface
- Modern React-based UI with Vite and Tailwind CSS
- Real-time updates with TanStack Query (React Query v4)
- Responsive device management dashboard
- Interactive script execution controls
- Modal-based device details and logs
- Mobile-responsive design optimized for both desktop and mobile
- Clean blue gradient interface with intuitive controls
- Game options panel with checkboxes for automation features

### 🔧 Technology Stack
- **Backend**: FastAPI 0.104.1, Python 3.9+, Loguru 0.7.2, OpenCV 4.8.1, NumPy 1.24.4
- **Frontend**: React 18.2, TypeScript 5+, Vite 7.1.2, Tailwind CSS 3.3, TanStack Query v4.24.6, Lucide React 0.263.1
- **Containerization**: Docker with privileged mode for USB device access
- **Image Processing**: OpenCV, NumPy for device screenshots and image analysis
- **Build Tools**: Vite 7.1.2 for fast development and optimized production builds
- **Styling**: Tailwind CSS 3.3 for utility-first styling with PostCSS 8.4.21 and Autoprefixer 10.4.14
- **HTTP Client**: Axios 1.3.4 with request/response interceptors
- **Code Quality**: Black, isort, flake8, mypy for Python; ESLint, TypeScript for frontend

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Android       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Devices       │
│                 │    │                 │    │   (ADB)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Android SDK platform tools (ADB) installed on host system
- USB debugging enabled on Android devices
- Python 3.9+ (for local development)
- Node.js 16+ (for frontend development)

### Running with Docker Compose

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

**Note**: The backend container runs in privileged mode and mounts USB devices (`/dev/bus/usb`) to access Android devices via ADB.

4. Access the web interface:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Health: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

### Development Setup

#### Frontend Development
```bash
cd frontend
npm install
npm run dev      # Start Vite development server
npm run build    # Build for production
npm run lint     # Run ESLint
npm run format   # Fix linting issues
```

#### Backend Development
```bash
cd backend
poetry install
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### Device Management
1. Connect Android devices via USB
2. Enable USB debugging in developer options
3. Devices will automatically appear in the web interface
4. Use the interface to connect/disconnect network devices

### Script Execution
1. Place Python scripts in the `backend/scripts/` directory
2. Scripts will automatically appear in the web interface
3. Select target devices and run scripts
4. Monitor progress and logs in real-time

### Writing Custom Scripts

Create a Python file in `backend/scripts/` with the following structure:

```python
from src.core.adb import adb
from src.core.logger import get_logger
from src.models import Device, GameOptions

# Script metadata - required for script discovery
SCRIPT_META = {
    "id": "my_script",
    "name": "My Custom Script",
    "order": 1,
    "marked": True,
    "description": "Description of what this script does"
}

def run_script(device: Device, game_options: GameOptions, context):
    """
    Main script function - this is required for all scripts
    
    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration
        context: ScriptContext object for logging and control
    
    Returns:
        Dict with execution results
    """
    logger = get_logger()
    
    # Your automation logic here
    logger.info(f"Running on device {device.id}")
    
    # Execute ADB commands using the adb helper
    result = adb.shell(device.id, "pm list packages")
    
    return {"status": "success", "packages": result}
```

## API Documentation

The backend provides a RESTful API with the following endpoints:

### Devices
- `GET /api/devices` - List all devices
- `GET /api/devices/{device_id}` - Get device details
- `POST /api/devices/refresh` - Refresh device list
- `POST /api/devices/{device_id}/connect` - Connect device
- `POST /api/devices/{device_id}/disconnect` - Disconnect device

### Scripts
- `GET /api/scripts` - List available scripts
- `GET /api/scripts/{script_id}` - Get script details

### Script Execution
- `POST /api/execute/{script_id}` - Execute script on devices
- `GET /api/execute/status` - Get execution status
- `POST /api/execute/stop` - Stop all executions
- `POST /api/execute/stop/{device_id}` - Stop execution on specific device

### System
- `GET /health` - Health check endpoint
- `GET /api/logs` - Get system logs (with filtering)

## Configuration

### Environment Variables

#### Backend
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `PYTHONPATH` - Python module path

#### Frontend
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api)

### Docker Compose Configuration

The `docker-compose.yml` includes:
- **Backend**: FastAPI server with ADB integration
  - Privileged mode for USB device access
  - ADB server port (5037) exposed
  - Health check endpoint
- **Frontend**: React application served via Nginx
- **Network**: Bridge network for service communication

**USB Device Access**: The backend container requires privileged mode and USB device mounting to communicate with Android devices.

## Development

### Project Structure
```
kvtm-auto/
├── frontend/                 # React TypeScript frontend (Vite + Tailwind)
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── DeviceDetailModal.tsx   # Device information display
│   │   │   ├── Modal.tsx              # Base modal component
│   │   │   ├── MultiSelect.tsx        # Multi-selection dropdown
│   │   │   └── SearchableSelect.tsx   # Searchable dropdown
│   │   ├── api.ts          # API client with Axios 1.3.4
│   │   ├── App.tsx         # Main application component
│   │   ├── main.tsx        # Application entry point
│   │   └── index.css       # Global styles with Tailwind imports
│   ├── package.json        # Node.js dependencies
│   ├── nginx.conf          # Nginx configuration for Docker
│   └── Dockerfile          # Frontend container build
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/           # API routes (devices.py, scripts.py, execute.py)
│   │   ├── core/          # Core business logic (adb.py, executor.py, database.py, image.py)
│   │   ├── models/        # Data models (device.py, script.py)
│   │   └── main.py        # FastAPI application entry point
│   ├── scripts/           # Automation scripts (example_script.py, open_game.py)
│   ├── data/              # JSON data storage (devices.json, logs.json, scripts.json)
│   ├── logs/              # Application log files
│   ├── test/              # Test suite directory
│   ├── assets/            # Static assets (test.png)
│   ├── pyproject.toml     # Poetry configuration with dependencies
│   └── Dockerfile         # Backend container build
├── docker-compose.yml      # Container orchestration with USB access
├── CLAUDE.md              # Development guidance for Claude Code
└── README.md              # Project documentation
```

### Code Quality & Linting

```bash
# Backend code quality
cd backend
poetry run black src/              # Format code (Black 23.11.0)
poetry run isort src/              # Sort imports (isort 5.12.0)
poetry run flake8 src/             # Lint code (flake8 6.1.0)
poetry run mypy src/               # Type checking (mypy 1.7.1)
poetry run pytest test/            # Run tests (pytest 7.4.3)

# Frontend code quality
cd frontend
npm run lint                       # Run ESLint 8.38.0
npm run format                     # Fix linting issues
npm run build                      # TypeScript 5+ compilation check
```

### Frontend Features

#### Dashboard Interface
- **Welcome Banner**: Clean blue gradient header with "Welcome to Auto Tools!" message
- **Settings Panel**: Device and script selection dropdowns
- **Game Options**: 
  - Checkboxes for Open Game, Open Chests, and Sell Items
  - Run now button for immediate execution
- **Running Devices Table**: 
  - Real-time view of active devices with script status
  - Actions: Stop, View, Logs, Detail buttons
  - Pagination support and Stop All functionality

#### Modal Components
- **Device Management Modal**: Connect/disconnect devices, view device status
- **Device Detail Modal**: Comprehensive device information with system specs
- **Logs Modal**: Real-time application logs with filtering and export

#### Mobile Responsive Design
- Optimized for both desktop and mobile devices
- Responsive grid layout with mobile-friendly button sizes
- Horizontal scroll for tables on small screens

### Code Quality

The project includes pre-configured tools for code quality:
- **Backend**: Black 23.11.0, isort 5.12.0, flake8 6.1.0, mypy 1.7.1, pytest 7.4.3 with asyncio support
- **Frontend**: ESLint 8.38.0, TypeScript 5.0.2 compiler, React-specific linting rules
- **Build Tools**: Vite 7.1.2 for fast development and optimized production builds
- **Styling**: Tailwind CSS 3.3 with PostCSS 8.4.21 and Autoprefixer 10.4.14

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**Devices not appearing**
- Ensure USB debugging is enabled
- Check ADB driver installation
- Verify device authorization

**Permission denied errors**
- Ensure USB debugging is enabled on devices
- Run Docker with privileged mode (already configured)
- Add user to `plugdev` group on Linux
- Check USB device permissions on host system

**Script execution failures**
- Check device connectivity
- Verify script syntax
- Review execution logs

### Support

For support and questions:
- Check the issue tracker
- Review the API documentation
- Consult the troubleshooting guide

## Roadmap

- [ ] Web-based script editor
- [ ] Device clustering support
- [ ] Enhanced logging dashboard
- [ ] Script scheduling
- [ ] Plugin system
- [ ] Performance monitoring
- [ ] Multi-user support