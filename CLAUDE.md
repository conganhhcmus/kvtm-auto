# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Python FastAPI)
```bash
cd backend
poetry install                           # Install dependencies
poetry run uvicorn src.main:app --reload # Start development server
poetry run black src/                    # Format code
poetry run isort src/                    # Sort imports
poetry run flake8 src/                   # Lint code
poetry run mypy src/                     # Type checking
```

### Frontend (React + Vite)
```bash
cd frontend
npm install                    # Install dependencies
npm run dev                   # Start development server
npm run build                 # Build for production
npm run lint                  # Lint code
npm run format                # Fix linting issues
npm run preview               # Preview built app
```

### Docker Development
```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs backend   # View backend logs
docker-compose logs frontend  # View frontend logs
```

## Architecture Overview

### Backend Structure (`backend/src/`)
- **main.py**: FastAPI application entry point with CORS, global exception handling, and lifespan management
- **api/**: REST API endpoints
  - **devices.py**: Device management, connection/disconnection, device info
  - **scripts.py**: Script discovery and metadata from filesystem
  - **execute.py**: Script execution endpoints and status management
- **core/**: Core business logic
  - **adb.py**: Android Debug Bridge wrapper for device control (tap, swipe, screenshots, app management)
  - **executor.py**: Multi-threaded script execution system with per-device isolation
  - **database.py**: In-memory database for device state and logging
  - **image.py**: Image processing utilities for device screenshots
- **models/**: Data models and type definitions
  - **device.py**: Device, DeviceStatus, DeviceScriptState models
  - **script.py**: Script metadata and GameOptions models
- **scripts/**: Automation scripts directory (example_script.py, open_game.py)
- **data/**: JSON data storage (devices.json, logs.json, scripts.json)
- **logs/**: Application log files
- **test/**: Test suite directory

### Frontend Structure (`frontend/src/`)
- **App.tsx**: Main application component with device management UI
- **api.ts**: Axios-based API client with interceptors for backend communication
- **components/**: React components for modals and UI elements
  - **DeviceDetailModal.tsx**: Comprehensive device information display
  - **Modal.tsx**: Base modal component for overlays
  - **MultiSelect.tsx**: Multi-selection dropdown component
  - **SearchableSelect.tsx**: Searchable dropdown component
- **main.tsx**: Application entry point with React 18 and TanStack Query setup
- **index.css**: Global styles with Tailwind CSS imports
- Built with Vite 7.1.2 + React 18.2 + TypeScript 5+ + Tailwind CSS 3.3 + TanStack Query v4.24.6

### Script System
- Scripts are Python files in `backend/scripts/` with required metadata:
  ```python
  SCRIPT_META = {
      "id": "script_id",
      "name": "Display Name", 
      "order": 1,
      "marked": True,
      "description": "What this script does"
  }
  
  def run_script(device: Device, game_options: GameOptions, context):
      # Script implementation with proper typing
      return {"success": True, "message": "Completed"}
  ```

### Device Management
- ADB integration for Android device control
- Per-device script execution with threading isolation
- Real-time device status tracking and logging
- Screen capture and touch event simulation

### Key Integrations
- **ADB**: Direct subprocess calls to Android Debug Bridge
- **OpenCV/NumPy**: Image processing for screenshots and image analysis (v4.8.1, v1.24.4)
- **FastAPI**: Async web framework v0.104.1 with automatic OpenAPI docs at `/docs`
- **TanStack Query v4.24.6**: Frontend state management and API caching
- **Loguru v0.7.2**: Structured logging throughout backend
- **Vite 7.1.2**: Fast development and build tooling for frontend
- **Lucide React v0.263.1**: Modern icon system for UI components
- **Axios v1.3.4**: HTTP client with request/response interceptors

## Development Workflow

1. **Adding New Scripts**: Create Python file in `backend/scripts/` with proper `SCRIPT_META` and `run_script` function
2. **Backend Changes**: Use Poetry for dependency management, follow existing async patterns
3. **Frontend Changes**: Use TanStack Query for API calls, Tailwind for styling
4. **Code Quality**: Use Black, isort, flake8, mypy for backend; ESLint for frontend
5. **Docker**: Backend requires privileged mode for ADB/USB device access

## Important Notes

- Backend starts on port 8000 with health check at `/health`
- Frontend served on port 3000 (development) or 80 (Docker)
- API endpoints prefixed with `/api/` (devices, scripts, execute routes)
- Docker containers communicate via `kvtm-network` bridge
- USB devices mounted as volumes (`/dev/bus/usb`) for ADB access in Docker
- Backend container runs in privileged mode for USB device access
- Loguru used for structured logging throughout backend
- TanStack Query v4 handles API caching and real-time updates
- Script execution isolated per device using threading with stop flags
- The frontend and backend run via docker compose. Any changes require rebuilding and restarting services
- Use browser MCP tools to get console logs, network requests, etc. when debugging frontend
- Do not run frontend with `npm run dev` - always use docker-compose and visit localhost:3000
- API documentation available at http://localhost:8000/docs when backend is running

## Testing & Quality Assurance

### Backend Testing
```bash
cd backend
poetry run pytest                        # Run all tests
poetry run pytest test/ -v               # Run with verbose output
poetry run pytest --cov=src test/        # Run with coverage report
```

### Code Quality Commands (run these before commits)
```bash
# Backend
cd backend
poetry run black src/                    # Format code
poetry run isort src/                    # Sort imports
poetry run flake8 src/                   # Lint code
poetry run mypy src/                     # Type checking

# Frontend  
cd frontend
npm run lint                             # ESLint check
npm run format                           # Fix ESLint issues
npm run build                            # Verify build works
```