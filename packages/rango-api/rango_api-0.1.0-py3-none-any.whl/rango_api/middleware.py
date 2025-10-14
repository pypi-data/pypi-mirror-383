#rango/middleware.py

from starlette.middleware.base import BaseHTTPMiddleware

class SimpleCORSMiddleware(BaseHTTPMiddleware):
    """Example middleware to allow all origins"""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
