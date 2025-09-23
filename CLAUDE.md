# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Local Development

#### Backend (Python Flask)
```bash
cd backend
poetry install                           # Install dependencies
cd src && poetry run python main.py      # Start development server (port 3001)
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
- **main.py**: Flask application entry point with CORS and Blueprint registration
- **apis/**: REST API endpoints using Flask Blueprints
  - **device_apis.py**: Device management endpoints (`/api/devices`)
  - **script_apis.py**: Script discovery and listing (`/api/scripts`)
  - **execution_apis.py**: Script execution management (`/api/execute`)
  - **system_apis.py**: Health check and system status (`/health`)
- **libs/**: Core utility libraries
  - **device_manager.py**: Android device discovery and management via ADB
  - **script_manager.py**: Script file discovery and metadata
  - **execution_manager.py**: Subprocess-based script execution
  - **adb_controller.py**: ADB wrapper with image/text detection (OpenCV + Tesseract)
- **scripts/**: Automation scripts directory
  - **tap_example.py**: Example script demonstrating ADB interactions
  - Scripts use direct ADB commands for device control

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

### Script System - **CURRENT IMPLEMENTATION**
Scripts are Python files that receive device_id as command line argument:
```python
import sys
import os
from src.libs.adb_controller import MultiDeviceManager

def main():
    device_id = sys.argv[1]  # Device serial from command line
    manager = MultiDeviceManager()

    # Direct ADB interactions
    manager.tap(device_id, 500, 1000)  # Tap at coordinates
    manager.click_text(device_id, "Submit")  # Click on text using OCR

    # Image template matching
    template_path = os.path.join("src", "assets", "button_template.png")
    manager.click_image(device_id, template_path)

if __name__ == "__main__":
    main()
    
```

### Device Management
- ADB integration for Android device control
- **Subprocess-only script execution** (no threading complexity)
- **Simple log format**: `[Time]: [Action] [Index]`
- Real-time device status tracking

### Key Integrations - **CURRENT**
- **ADB**: Direct subprocess calls to Android Debug Bridge for device control
- **OpenCV**: Image template matching and computer vision (v4.8.1+)
- **Tesseract**: OCR text recognition for UI automation
- **Flask**: Web framework with Blueprint architecture and CORS support
- **NumPy/Pillow**: Image processing and manipulation
- **Threading**: Background device discovery via ADB polling

## Development Workflow

1. **Local Development**: Use Poetry + npm for fast iteration
2. **Docker Development**: Use for production-like testing
3. **Adding New Scripts**: Use new simple logging format with `_core.py` utilities
4. **Backend Changes**: Rely on global exception handler, avoid try-catch
5. **Frontend Changes**: Use unified API models from `models/api.py`
6. **Shell Commands**: Use `Shell` class for command building

## Important Notes - **UPDATED**

### **Deployment Options**
- **Local Development**: Backend (3001) + Frontend (5173) separate processes
- **Docker**: Backend (3001) + Frontend (3000) containerized

### **Current Architecture Benefits**
- **Flask Blueprint structure** - Modular API organization
- **Subprocess execution** - Isolated script execution
- **ADB integration** - Direct Android device control
- **Computer vision** - OpenCV + Tesseract for UI automation
- **Background discovery** - Automatic device detection

### **Architecture**
- Backend (Flask): port 3001 with health check at `/health`
- Frontend: localhost:5173 (local dev) or localhost:3000 (Docker)
- API endpoints: `/api/devices`, `/api/scripts`, `/api/execute`
- Scripts executed as subprocesses with device_id parameter
- ADB integration for Android device automation
- Image/text recognition for UI automation

### **Script Development Guidelines**
- Scripts receive `device_id` as command line argument
- Use `MultiDeviceManager` for all ADB interactions
- Image templates stored in `src/assets/` for matching
- OCR text detection with Tesseract integration
- Process isolation ensures stability

### **Development**
- Backend: `cd backend/src && poetry run python main.py` (port 3001)
- Frontend: `npm run dev` (port 5173)
- Docker: `docker-compose up` for full-stack testing
- Scripts executed via subprocess with device serial parameter
- Device logs stored in Device objects for UI display

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

- Python 3.9+ installation with pyenv
- Poetry dependency management
- ADB and Tesseract OCR setup
- Development workflow commands
- The frontend and backend is running in dev now. No need to run again