# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Local Development

#### Backend (Python FastAPI)
```bash
cd backend
poetry install                           # Install dependencies
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000  # Start development server
poetry run black src/                    # Format code
poetry run isort src/                    # Sort imports
poetry run flake8 src/                   # Lint code
poetry run mypy src/                     # Type checking
poetry run pytest                        # Run tests
```

#### Frontend (React + Vite)
```bash
cd frontend
npm install                    # Install dependencies
npm run dev                   # Start development server (localhost:5173)
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
docker-compose build          # Rebuild containers after code changes
```

## Architecture Overview (Post-Refactoring)

### Backend Structure (`backend/src/`)
- **main.py**: FastAPI application entry point with CORS and global exception handling
- **api/**: REST API endpoints - **SIMPLIFIED**
  - **devices.py**: Device management with unified API models
  - **scripts.py**: Script discovery without complex validation
  - **execute.py**: Script execution with simplified error handling
- **service/**: Service layer - **STREAMLINED**
  - **executor.py**: **Subprocess-only** execution system (no threading complexity)
  - **database.py**: JSON database with **simplified logging format**
  - **script.py**: Script management utilities
- **libs/**: Core utility libraries - **ENHANCED**
  - **adb.py**: Android Debug Bridge wrapper
  - **image.py**: Image processing utilities
  - **shell.py**: **NEW - Shell command utilities with loop support**
  - **time_provider.py**: **Enhanced time utilities (UTC + GMT+7)**
  - **log_actions.py**: **NEW - Standard log action constants**
- **models/**: Data models - **UNIFIED**
  - **device.py**: Device and DeviceStatus models
  - **script.py**: Script metadata and GameOptions models
  - **api.py**: **NEW - All API request/response models in one place**
- **scripts/**: Automation scripts directory
  - **_core.py**: **Enhanced with simple log format [Time]: [Action] [Index]**
  - **example_script.py**, **open_game.py**: Sample automation scripts
- **data/**: JSON data storage (**moved under src/**)
- **logs/**: Application log files (**moved under src/**)

### Frontend Structure (`frontend/src/`)
- **App.tsx**: Main application component
- **api.ts**: Axios-based API client with interceptors
- **components/**: React components for modals and UI elements
  - **DeviceDetailModal.tsx**: Device information display
  - **DeviceLogModal.tsx**: **NEW - Simple log format display**
  - **Modal.tsx**: Base modal component
  - **MultiSelect.tsx**: Multi-selection dropdown
  - **SearchableSelect.tsx**: Searchable dropdown
- Built with Vite 7.1.2 + React 18.2 + TypeScript 5+ + Tailwind CSS 3.3

### Script System - **SIMPLIFIED**
Scripts use the new simple logging format:
```python
from scripts._core import write_log, log_run_open_game, log_run_script

SCRIPT_META = {
    "id": "script_id",
    "name": "Display Name", 
    "order": 1,
    "marked": True,
    "description": "What this script does"
}

def main(device: Device, game_options: GameOptions, context):
    # New simple logging - displays as [12:34:56 PM]: Run Open Game
    log_run_open_game(device.id)
    log_run_script(device.id, 1000)  # [12:34:57 PM]: Run Script [1000] times
    
    # Custom actions
    write_log(device.id, "Taking screenshot")
    write_log(device.id, "Waiting", "5.0s")  # [12:34:58 PM]: Waiting [5.0s]
    
    return {"success": True, "message": "Completed"}
```

### Device Management
- ADB integration for Android device control
- **Subprocess-only script execution** (no threading complexity)
- **Simple log format**: `[Time]: [Action] [Index]`
- Real-time device status tracking

### Key Integrations - **UPDATED**
- **ADB**: Direct subprocess calls to Android Debug Bridge
- **OpenCV/NumPy**: Image processing (v4.8.1, v1.24.4)
- **FastAPI**: Async web framework v0.104.1 with automatic OpenAPI docs at `/docs`
- **Shell Utilities**: **NEW - Enhanced shell command building with loop support**
- **Simple Logging**: **NEW - User-friendly log format [Time]: [Action] [Index]**
- **Unified Models**: **NEW - All API models centralized in models/api.py**
- **Global Exception Handling**: **Simplified error handling**

## Development Workflow

1. **Local Development**: Use Poetry + npm for fast iteration
2. **Docker Development**: Use for production-like testing
3. **Adding New Scripts**: Use new simple logging format with `_core.py` utilities
4. **Backend Changes**: Rely on global exception handler, avoid try-catch
5. **Frontend Changes**: Use unified API models from `models/api.py`
6. **Shell Commands**: Use `Shell` class for command building

## Important Notes - **UPDATED**

### **Deployment Options**
- **Local Development**: Backend (8000) + Frontend (5173) separate processes
- **Docker**: Backend (8000) + Frontend (3000) containerized

### **Recent Refactoring Benefits**
- **50% less code** - Simplified executor and API endpoints
- **Subprocess-only execution** - No threading complexity
- **Unified API models** - Single source of truth
- **Simple log format** - User-friendly `[Time]: [Action] [Index]`
- **Enhanced shell support** - Programmatic command building
- **Global error handling** - Consistent across all endpoints

### **Architecture**
- Backend starts on port 8000 with health check at `/health`
- Frontend: localhost:5173 (local dev) or localhost:3000 (Docker)
- API endpoints prefixed with `/api/`
- **Data/logs moved under `src/`** for better organization
- **Shell class** provides clean command building interface
- **Time provider** supports both UTC and GMT+7 operations

### **Logging System** - **NEW**
```python
# Old format: 2024-01-01 12:12:39.123 | INFO | device_123: Starting script
# New format: [12:12:39 PM]: Run Script [1000] times

# Usage in scripts:
write_log(device_id, "Script started", script_name)
log_run_open_game(device_id)
log_run_script(device_id, 1000)
log_loop_iteration(device_id, 1, 1000)  # [12:13:01 PM]: Loop [1/1000]
```

### **Development**
- Use `poetry run uvicorn src.main:app --reload` for backend development
- Use `npm run dev` for frontend development  
- Use `docker-compose up` for full-stack testing
- All logs display in clean `[Time]: [Action] [Index]` format
- Shell commands built with `Shell.build_script_execution_command()`
- Keep `__init__.py` file is empty

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

## Key Refactoring Changes Summary

### **What Changed**
1. **Executor**: From 450 lines → 150 lines (subprocess-only)
2. **Execute API**: From 350 lines → 140 lines (simplified)
3. **Scripts API**: From 100 lines → 40 lines (no validation)
4. **Logging**: Complex format → Simple `[Time]: [Action] [Index]`
5. **Models**: Scattered → Unified in `models/api.py`
6. **Shell**: Functions → `Shell` class with enhanced capabilities
7. **Error Handling**: Try-catch everywhere → Global exception handler

### **Benefits**
- **Maintainability**: 50% less code, cleaner architecture
- **Reliability**: Subprocess isolation, consistent error handling  
- **User Experience**: Clean, readable logs
- **Developer Experience**: Unified models, simplified APIs
- **Performance**: Removed unnecessary complexity and overhead