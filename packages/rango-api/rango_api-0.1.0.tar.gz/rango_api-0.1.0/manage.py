#!/usr/bin/env python3
"""
Rango Framework CLI
-----------------------------------
Usage:
    python manage.py startproject myproject
    python manage.py startapp blog
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
"""
import typer
import os
import subprocess
import shutil
from pathlib import Path

cli = typer.Typer(help="Rango Framework management CLI")
PROJECT_ROOT = Path(__file__).resolve().parent

def _update_project_settings(project_path: Path, app_name: str):
    """Update project settings to include the new app."""
    settings_file = project_path / "project" / "settings.py"
    if not settings_file.exists():
        return
    
    content = settings_file.read_text()
    
    # Add app to INSTALLED_APPS
    if f'"apps.{app_name}"' not in content:
        if "INSTALLED_APPS = []" in content:
            content = content.replace("INSTALLED_APPS = []", f'INSTALLED_APPS = ["apps.{app_name}"]')
        elif "INSTALLED_APPS = [" in content:
            # Find the closing bracket and add the new app
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "INSTALLED_APPS = [" in line:
                    # Look for the closing bracket
                    for j in range(i, len(lines)):
                        if "]" in lines[j] and f'"apps.{app_name}"' not in content:
                            lines[j] = lines[j].replace("]", f'    "apps.{app_name}",\n]')
                            content = '\n'.join(lines)
                            break
                    break
    
    # Add model to TORTOISE_ORM
    model_path = f'"apps.{app_name}.models"'
    if model_path not in content:
        if "'models':['aerich.models']" in content:
            content = content.replace("'models':['aerich.models']", f"'models':['aerich.models',{model_path}]")
    
    settings_file.write_text(content)

def _update_project_urls(project_path: Path, app_name: str):
    """Update project URLs to include the new app router."""
    urls_file = project_path / "project" / "urls.py"
    if not urls_file.exists():
        return
    
    content = urls_file.read_text()
    
    # Add import for the new app router
    import_line = f"from apps.{app_name}.urls import router as {app_name}_router"
    if import_line not in content:
        lines = content.split('\n')
        # Add import after existing imports
        for i, line in enumerate(lines):
            if line.startswith("from ") and "import" in line:
                continue
            else:
                lines.insert(i, import_line)
                break
        content = '\n'.join(lines)
    
    # Add router inclusion
    include_line = f"router.include({app_name}_router)"
    if include_line not in content:
        content += f"\n{include_line}\n"
    
    urls_file.write_text(content)

# ----------------------------
# STARTPROJECT
# ----------------------------
@cli.command()
def startproject(name: str):
    project_dir = PROJECT_ROOT / name
    if project_dir.exists():
        typer.echo(f"❌ Project '{name}' exists")
        raise typer.Exit(code=1)
    os.makedirs(project_dir / "apps", exist_ok=True)
    os.makedirs(project_dir / "project", exist_ok=True)
    # settings.py
    (project_dir / "project" / "settings.py").write_text(
        "DATABASE_URL='sqlite://db.sqlite3'\n"
        "TORTOISE_ORM={\n"
        "    'connections':{'default': DATABASE_URL},\n"
        "    'apps':{\n"
        "        'models':{\n"
        "            'models':['aerich.models'],\n"
        "            'default_connection':'default'\n"
        "            }\n"
        "        }\n"
        "}\n\n"
        "INSTALLED_APPS = []\n"
    )
    # urls.py
    (project_dir / "project" / "urls.py").write_text(
        "from rango_api.router import Router\n"
        "from .views import HomeView\n\n"
        "router = Router()\n"
        "router.add(\"/\", HomeView, methods=[\"GET\"])\n"
    )
    # views.py
    (project_dir / "project" / "views.py").write_text(
        "from rango_api.generics import ListCreateView\n"
        "from fastapi.responses import JSONResponse\n\n"
        "class HomeView:\n"
        "    async def get(self, request):\n"
        "        return JSONResponse({\"message\": \"Welcome to Rango Framework!\"})\n"
    )
    # asgi.py
    (project_dir / "project" / "asgi.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.append(str(Path(__file__).resolve().parent.parent.parent))\n\n"
        "from rango_api.core import RangoApp\n"
        "from rango_api.middleware import SimpleCORSMiddleware\n"
        "from project.urls import router\n\n"
        "app = RangoApp(debug=True)\n"
        "app.add_middleware(SimpleCORSMiddleware)\n"
        "app.include_router(router)\n\n"
        "# Add startup event handler for database initialization\n"
        "@app.on_event(\"startup\")\n"
        "async def startup_event():\n"
        "    from rango_api.db import init_db\n"
        "    await init_db()\n"
    )
    # main.py
    (project_dir / "main.py").write_text(
        "from project.asgi import app\n"
        "if __name__=='__main__':\n"
        "    import uvicorn\n"
        "    uvicorn.run(\"project.asgi:app\", host='127.0.0.1', port=8000, reload=True)\n"
    )
    
    # Copy manage.py to the project directory
    shutil.copy2(PROJECT_ROOT / "manage.py", project_dir / "manage.py")
    
    typer.echo(f"✅ Project '{name}' created!")

# ----------------------------
# STARTAPP
# ----------------------------
@cli.command()
def startapp(name: str):
    project_path = Path.cwd()
    apps_dir = project_path / "apps"
    app_dir = apps_dir / name
    if not (project_path / "project" / "settings.py").exists():
        typer.echo("❌ Not in a Rango project")
        raise typer.Exit(code=1)
    os.makedirs(app_dir, exist_ok=True)
    (app_dir / "__init__.py").write_text("")
    (app_dir / "models.py").write_text(
        "from tortoise import fields, models\n\n\n"
        "class Example(models.Model):\n"
        "    id = fields.IntField(pk=True)\n"
        "    title = fields.CharField(max_length=255)\n"
        "    description = fields.TextField(null=True)\n"
        "    created_at = fields.DatetimeField(auto_now_add=True)\n\n"
        "    def __str__(self):\n"
        "        return self.title\n"
    )
    (app_dir / "serializers.py").write_text(
        "from rango_api.serializers import ModelSerializer\n"
        "from .models import Example\n\n"
        "class ExampleSerializer(ModelSerializer):\n"
        "    class Meta:\n"
        "        model = Example\n"
        "        fields = [\"id\", \"title\", \"description\", \"created_at\"]\n"
    )
    (app_dir / "views.py").write_text(
        "from rango_api.generics import ListCreateView, RetrieveUpdateDeleteView\n"
        "from .models import Example\n"
        "from .serializers import ExampleSerializer\n\n"
        "class ExampleListCreateView(ListCreateView):\n"
        "    model = Example\n"
        "    serializer_class = ExampleSerializer\n\n"
        
        "    \n\n"
        "class ExampleDetailView(RetrieveUpdateDeleteView):\n"
        "    model = Example\n"
        "    serializer_class = ExampleSerializer\n\n"
        "    \n"
    )
    (app_dir / "urls.py").write_text(
        "from rango_api.router import Router\n"
        "from .views import ExampleListCreateView, ExampleDetailView\n\n"
        "router = Router()\n"
        "router.add(\"/example\", ExampleListCreateView, methods=[\"GET\", \"POST\"])\n"
        "router.add(\"/example/{id}\", ExampleDetailView, methods=[\"GET\", \"PUT\", \"DELETE\"])\n"
    )
    
    # Update project settings to include the new app
    _update_project_settings(project_path, name)
    _update_project_urls(project_path, name)
    
    typer.echo(f"✅ App '{name}' created and configured!")

# ----------------------------
# DB COMMANDS
# ----------------------------
@cli.command()
def makemigrations(message: str = "auto"):
    typer.echo("📦 Making migrations...")
    subprocess.run(["aerich", "migrate", "--name", message], check=False)

@cli.command()
def migrate():
    typer.echo("⚙️ Applying migrations...")
    subprocess.run(["aerich", "upgrade"], check=False)

# ----------------------------
# RUN SERVER
# ----------------------------
@cli.command()
def runserver(host: str = "127.0.0.1", port: int = 8000):
    typer.echo(f"🚀 Running server at http://{host}:{port}")
    subprocess.run(["uvicorn", "project.asgi:app", "--host", host, "--port", str(port), "--reload"])

if __name__ == "__main__":
    cli()
