#!/usr/bin/env python3
"""Setup script for rango-api."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Define requirements directly
requirements = [
    "aerich==0.9.2",
    "aiosqlite==0.21.0",
    "annotated-types==0.7.0",
    "anyio==4.11.0",
    "asyncclick==8.3.0.7",
    "click==8.3.0",
    "colorama==0.4.6",
    "dictdiffer==0.9.0",
    "fastapi==0.119.0",
    "h11==0.16.0",
    "idna==3.10",
    "iso8601==2.1.0",
    "markdown-it-py==4.0.0",
    "mdurl==0.1.2",
    "pydantic==2.12.0",
    "pydantic_core==2.41.1",
    "Pygments==2.19.2",
    "pypika-tortoise==0.6.2",
    "pytz==2025.2",
    "rich==14.2.0",
    "shellingham==1.5.4",
    "sniffio==1.3.1",
    "starlette==0.48.0",
    "tortoise-orm==0.25.1",
    "typer==0.19.2",
    "typing-inspection==0.4.2",
    "typing_extensions==4.15.0",
    "uvicorn==0.37.0",
]

setup(
    name="rango-api",
    version="0.1.0",
    author="Jahidul Hassan Reshad",
    author_email="hassanjahidul365@gmail.com",
    description="A modern Python web framework built on FastAPI with Django-like features and folder structure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reshadMajumder/rango",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "rango=rango_api.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
