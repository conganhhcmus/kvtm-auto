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
  - **devices.py**: Device management, script execution, device logs
  - **scripts.py**: Script discovery and metadata from filesystem
- **core/**: Core business logic
  - **adb.py**: Android Debug Bridge wrapper for device control (tap, swipe, screenshots, app management)
  - **executor.py**: Multi-threaded script execution system with per-device isolation
  - **database.py**: In-memory database for device state and logging
  - **image.py**: Image processing utilities for device screenshots
  - **logger.py**: Centralized logging setup using Loguru
- **models/**: Data models for Device, GameOptions, and device states

### Frontend Structure (`frontend/src/`)
- **App.tsx**: Main application component with device management UI
- **api.ts**: Axios-based API client with interceptors for backend communication
- **components/**: React components for modals and UI elements
- Built with Vite + React 18 + TypeScript + Tailwind CSS + React Query

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
  
  def run_script(device_info, game_options, stop_flag):
      # Script implementation
      return {"success": True, "message": "Completed"}
  ```

### Device Management
- ADB integration for Android device control
- Per-device script execution with threading isolation
- Real-time device status tracking and logging
- Screen capture and touch event simulation

### Key Integrations
- **ADB**: Direct subprocess calls to Android Debug Bridge
- **UIAutomator2/ADBUtils**: Android automation libraries
- **OpenCV/Pillow**: Image processing for screenshots
- **FastAPI**: Async web framework with automatic OpenAPI docs
- **TanStack Query**: Frontend state management and API caching

## Development Workflow

1. **Adding New Scripts**: Create Python file in `backend/scripts/` with proper `SCRIPT_META` and `run_script` function
2. **Backend Changes**: Use Poetry for dependency management, follow existing async patterns
3. **Frontend Changes**: Use TanStack Query for API calls, Tailwind for styling
4. **Code Quality**: Use Black, isort, flake8, mypy for backend; ESLint for frontend
5. **Docker**: Backend requires privileged mode for ADB/USB device access

## Important Notes

- Backend starts on port 8000 with health check at `/health`
- Frontend served on port 3000 (development) or 80 (Docker)
- API endpoints prefixed with `/api/` (devices, scripts routes)
- Docker containers communicate via `kvtm-network` bridge
- USB devices mounted as volumes for ADB access in Docker
- Loguru used for structured logging throughout backend
- TanStack Query handles API caching and real-time updates
- Script execution isolated per device using threading with stop flags
- The application is running by docker compose. Any change need to build and restart service in docker compose
- use browsermcp to get error console log, network, ... in browser