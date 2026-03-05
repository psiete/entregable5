"""Aplicación principal FastAPI para gestión de tareas y historias de usuario."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from lib.database import init_db
from lib.routes import router


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI.
    
    Returns:
        Instancia configurada de FastAPI.
    """
    app = FastAPI(
        title="API de Gestión de Tareas",
        description="Sistema de generación de tareas a partir de historias de usuario",
        version="1.0.0"
    )
    
    # Inicializar base de datos
    init_db()
    
    # Incluir router principal
    app.include_router(router)
    
    # Montar carpeta de templates/static si existe
    templates_path = Path(__file__).parent / "templates"
    if templates_path.exists():
        try:
            app.mount("/static", StaticFiles(directory=str(templates_path)), name="static")
        except Exception:
            pass
    
    @app.get("/")
    async def home():
        """Ruta de inicio."""
        return {
            "message": "API de gestión de tareas",
            "endpoints": {
                "GET /user-stories": "Obtener todas las historias de usuario",
                "POST /user-stories": "Crear una nueva historia de usuario",
                "GET /user-stories/{id}/tasks": "Obtener tareas de una historia",
                "POST /user-stories/{id}/generate-tasks": "Generar tareas con IA"
            }
        }
    
    return app


# Crear instancia global de la aplicación para uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

