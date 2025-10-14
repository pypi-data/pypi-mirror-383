"""
Rango API Framework

A modern Python web framework built on FastAPI with Django-like features.
"""

__version__ = "0.1.0"
__author__ = "Jahidul Hassan Reshad"
__email__ = "hassanjahidul365@gmail.com"

from .core import RangoApp
from .router import Router
from .generics import ListCreateView, RetrieveUpdateDeleteView
from .serializers import ModelSerializer
from .middleware import SimpleCORSMiddleware
from .db import init_db

__all__ = [
    "RangoApp",
    "Router", 
    "ListCreateView",
    "RetrieveUpdateDeleteView",
    "ModelSerializer",
    "SimpleCORSMiddleware",
    "init_db",
]
