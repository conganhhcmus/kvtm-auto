# API routes for KVTM Auto

from .devices import router as devices_router
from .execute import router as execute_router
from .scripts import router as scripts_router

__all__ = ["devices_router", "execute_router", "scripts_router"]
