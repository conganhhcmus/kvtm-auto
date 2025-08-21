# KVTM Auto - Android Device Automation Platform

A comprehensive full-stack application for automating Android devices using ADB (Android Debug Bridge). Built with a modern React + TypeScript frontend (Vite/Tailwind) and Python FastAPI backend with advanced Android automation capabilities.

## Features

### 🤖 Device Management
- Automatic device discovery via ADB
- Real-time device status monitoring
- USB and network device support
- Device connection/disconnection management
- Device details and specifications display

### 📝 Script Management
- Custom automation script execution with metadata
- Multi-device parallel execution
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
- Real-time updates with TanStack Query (React Query)
- Responsive device management dashboard
- Interactive script execution controls
- Modal-based device details and logs
- Mobile-responsive design optimized for both desktop and mobile
- Clean blue gradient interface with intuitive controls
- Game options panel with checkboxes for automation features

### 🔧 Technology Stack
- **Backend**: FastAPI, Python 3.9+, ADB Utils, UIAutomator2
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Lucide React
- **Containerization**: Docker with USB device access
- **Image Processing**: OpenCV, Pillow for device screenshots
- **Build Tools**: Vite for fast development and optimized production builds
- **Styling**: Tailwind CSS for utility-first styling with custom theme
- **HTTP Client**: Axios with request/response interceptors

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
- `GET /devices` - List all devices
- `GET /devices/{device_id}` - Get device details
- `POST /devices/refresh` - Refresh device list
- `POST /devices/{device_id}/connect` - Connect device
- `POST /devices/{device_id}/disconnect` - Disconnect device

### Scripts
- `GET /scripts` - List available scripts
- `GET /scripts/{script_id}` - Get script details
- `POST /scripts/{script_id}/run` - Execute script
- `GET /scripts/executions` - List executions
- `POST /scripts/executions/{execution_id}/stop` - Stop execution

### System
- `GET /health` - Health check endpoint
- `GET /logs` - Get system logs (with filtering)

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
│   │   ├── api.ts          # API client
│   │   └── ...
│   └── ...
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core business logic
│   │   ├── models/        # Data models
│   │   └── main.py        # Application entry point
│   ├── scripts/           # Automation scripts
│   └── pyproject.toml     # Poetry configuration
└── docker-compose.yml      # Container orchestration
```

### Code Quality & Linting

```bash
# Backend code quality
cd backend
poetry run black src/              # Format code
poetry run isort src/              # Sort imports
poetry run flake8 src/             # Lint code
poetry run mypy src/               # Type checking

# Frontend code quality
cd frontend
npm run lint                       # Run ESLint
npm run format                     # Fix linting issues
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
- **Backend**: Black, isort, flake8, mypy for Python code quality
- **Frontend**: ESLint, TypeScript compiler, React-specific linting
- **Build Tools**: Vite for fast development and optimized production builds
- **Styling**: Tailwind CSS with PostCSS and Autoprefixer

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