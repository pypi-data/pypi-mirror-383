# rango/router.py
from fastapi import APIRouter, Request
from typing import Any, Dict
import inspect

class Router:
    """Simple router wrapper for Rango framework."""
    def __init__(self):
        self.router = APIRouter()

    def add(self, path: str, view_class, methods=None):
        """
        Add a route for a view class.
        :param path: URL path
        :param view_class: View class with get/post/put/delete methods
        :param methods: List of HTTP methods
        """
        methods = methods or ["GET"]
        view_instance = view_class()

        for method in methods:
            method_upper = method.upper()
            view_method = getattr(view_instance, method_upper.lower())

            # Create a handler that can accept path parameters
            async def handler(_method=method_upper, _view_method=view_method, _view_instance=view_instance, request: Request = None):
                # Get the method signature to see what parameters it expects
                sig = inspect.signature(_view_method)
                params = list(sig.parameters.keys())
                
                # If the method only expects 'request', call it with just request
                if len(params) == 1 and 'request' in params:
                    return await _view_method(request)
                # If the method expects 'request' and other parameters, we need to handle path params
                elif 'request' in params and len(params) > 1:
                    # Extract path parameters from the request
                    path_params = {}
                    for param in params:
                        if param != 'request' and param in request.path_params:
                            # Convert to int if it looks like an ID
                            value = request.path_params[param]
                            if param == 'id' and value.isdigit():
                                path_params[param] = int(value)
                            else:
                                path_params[param] = value
                    return await _view_method(request, **path_params)
                else:
                    # If the method doesn't expect request, call it without parameters
                    return await _view_method()

            # Register the route with FastAPI
            self.router.add_api_route(path, handler, methods=[method_upper])
            # Also register with trailing slash to avoid 404s
            if not path.endswith("/"):
                self.router.add_api_route(path + "/", handler, methods=[method_upper])

    def include(self, router):
        """
        Include another router.
        Accepts either a Router instance or raw APIRouter.
        """
        if hasattr(router, "router"):  # another Router instance
            self.router.include_router(router.router)
        else:  # raw APIRouter
            self.router.include_router(router)
