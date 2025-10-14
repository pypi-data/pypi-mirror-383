#rango/core.py
from fastapi import FastAPI
from .router import Router

class RangoApp(FastAPI):
    """Main Rango app wrapper ."""
    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)
        self.router_obj = Router()
        self._router_mounted = False

    def add_view(self, path: str, view_class, methods=None):
        self.router_obj.add(path, view_class, methods or ["GET"])

    def include_router(self, router):
        """Include a router and mount it to the FastAPI app."""
        self.router_obj.include(router)
        # Mount the router to the FastAPI app only once
        if not self._router_mounted:
            super().include_router(self.router_obj.router)
            self._router_mounted = True

    def add_middleware(self, middleware_class, **options):
        super().add_middleware(middleware_class, **options)

    def run(self, host="127.0.0.1", port=8000):
        import uvicorn
        uvicorn.run(self, host=host, port=port)
